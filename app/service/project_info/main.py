import logging
import json
import os
from datetime import datetime, timezone
import time
from google.cloud import resourcemanager_v3, bigquery, monitoring_v3
from google.protobuf.json_format import MessageToDict
from google.protobuf.timestamp_pb2 import Timestamp
from google.api_core.exceptions import GoogleAPIError
import functions_framework
import google.cloud.logging

client = google.cloud.logging.Client()
client.setup_logging()
bq_client = bigquery.Client()
monitoring_client = monitoring_v3.MetricServiceClient()

# Log Event
def log_event(level, message, event, **kwargs):
    """Log Event"""
    log_data = {
        "service_name": "project_info", 
        "event": event, 
        "message": message, 
        **kwargs
    }
    
    if level == "info":
        logging.info(json.dumps(log_data))
    elif level == "warning":
        logging.warning(json.dumps(log_data))
    elif level == "error":
        logging.error(json.dumps(log_data))

# variables
BQ_TABLE = os.getenv("BQ_TABLE", "observability.project_info")
FOLDER_ID = os.getenv("FOLDER_ID", "1062810406170")
PROJECT_ID = os.getenv("GCP_PROJECT", "dev2-ea8f")

if not BQ_TABLE or not FOLDER_ID or not PROJECT_ID:
    log_event("error", "Missing environment variables", "config_error")

def get_projects(folder_id):
    """Fetches projects from GCP Resource Manager API."""
    try:
        start_time = time.time()
        client = resourcemanager_v3.ProjectsClient()
        request = resourcemanager_v3.ListProjectsRequest(parent=f"folders/{folder_id}")
        projects = list(client.list_projects(request=request))
        duration = time.time() - start_time
        _monitor("dfc_prj_api_duration", duration)

        if not projects:
            log_event("warning", f"No projects found under folder {folder_id}", "load")

        # log_event("info", "Fetched projects successfully", "load", count=len(projects))
        return projects
    except GoogleAPIError as e:
        log_event("error", "API error while fetching projects", "load", error=str(e))
        return []
    except Exception as e:
        log_event("error", "Unexpected error while fetching projects", "load", error=str(e))
        return []

def transform(projects):
    """Transforms GCP project data for BigQuery."""
    start_time = time.time()
    ingestion_timestamp = datetime.now(timezone.utc).isoformat()
    rows_to_insert = []

    for project in projects:
        try:
            project_dict = MessageToDict(project._pb, preserving_proto_field_name=True)
            labels_list = [{"key": k, "value": v} for k, v in project_dict.get("labels", {}).items()]
            row = {
                "project_id": project_dict["project_id"],
                "project_number": project_dict["name"],
                "folder_id": project_dict.get("parent"),
                "project_name": project_dict.get("display_name"),
                "state": project_dict.get("state"),
                "create_time": project_dict.get("create_time"),
                "update_time": project_dict.get("update_time"),
                "ingestion_time": ingestion_timestamp,
                "etag": project_dict.get("etag"),
                "labels": labels_list,
            }
            rows_to_insert.append(row)
        except KeyError as e:
            log_event("warning", f"Missing key in project data: {e}", "transform")
        except Exception as e:
            log_event("error", "Error transforming project data", "transform", error=str(e))

    duration = time.time() - start_time
    _monitor("dfc_prj_processing_duration", duration)
    # log_event("info", "Transformed project data successfully", "transform", count=len(rows_to_insert))
    return rows_to_insert

def store(rows):
    """Inserts transformed project data into BigQuery."""
    start_time = time.time()
    if not rows:
        log_event("warning", "No data to insert into BigQuery", "store")
        return False

    try:
        errors = bq_client.insert_rows_json(BQ_TABLE, rows)
        if errors:
            log_event("error", "Failed to insert data into project_info", "store", errors=errors)
            return False

        # log_event("info", "Inserted data to project_info successfully", "store", count=len(rows))
        _monitor("dfc_bigquery_insert_duration", time.time() - start_time)
        return True
    except GoogleAPIError as e:
        log_event("error", "BigQuery API error", "store", error=str(e))
        return False
    except Exception as e:
        log_event("error", "Unexpected error while inserting into project_info", "store", error=str(e))
        return False

def _monitor(metric_name, value):
    """Reports a custom metric to Cloud Monitoring."""
    try:
        series = monitoring_v3.TimeSeries()
        series.metric.type = f"custom.googleapis.com/{metric_name}"
        now = time.time()
        timestamp = Timestamp(seconds=int(now), nanos=int((now - int(now)) * 1e9))

        interval = monitoring_v3.TimeInterval(start_time=timestamp, end_time=timestamp)
        point = monitoring_v3.Point(interval=interval, value=monitoring_v3.TypedValue(double_value=value))
        series.points = [point]

        monitoring_client.create_time_series(name=f"projects/{PROJECT_ID}", time_series=[series])
        # log_event("info", "Metric reported successfully", "monitor", metric_name=metric_name, value=value)
    except Exception as e:
        log_event("error", "Failed to report metric", "monitor", metric_name=metric_name, error=str(e))

@functions_framework.http
def main(request):
    """Main Cloud Function entry point (HTTP Triggered)."""
    start_time = time.time()

    # Adding service_name to the main log and structured JSON
    # log_event("info", "Function execution started", "start", folder_id=FOLDER_ID, service_name="project_info")

    projects = get_projects(FOLDER_ID)
    if projects:
        transformed_data = transform(projects)
        store(transformed_data)
    else:
        log_event("info", "No projects to process", "complete")

    _monitor("dfc_prj_total_duration", time.time() - start_time)
    # log_event("info", "Function execution complete", "complete", service_name="project_info")

    return "Project details loaded successfully"
