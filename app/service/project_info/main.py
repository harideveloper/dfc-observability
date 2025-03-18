"""
    Project Info service collects project details from Resource Manager API.

    Step 1 : Batch Trigger from Cloud Scheduler
    Step 2 : Collect Project info from Resource Manager API
    Step 3 : Minor Data Transformation
    Step 4 : Store Data in BigQuery
    Step 5 : Report Telemetry Metrics to GCP Monitoring
"""

import logging
import json
import os
from datetime import datetime, timezone
import time
from google.cloud import resourcemanager_v3, bigquery, monitoring_v3
from google.protobuf.json_format import MessageToDict
from google.protobuf.timestamp_pb2 import Timestamp  # pylint: disable=E0611
from google.api_core import exceptions
import functions_framework
import google.cloud.logging

logging_client = google.cloud.logging.Client()
logging_client.setup_logging()
bq_client = bigquery.Client()
monitoring_client = monitoring_v3.MetricServiceClient()

SERVICE_NAME = os.getenv("SERVICE_NAME", "project_info")

logging.basicConfig(
    format="%(levelname)s %(asctime)s [%(service_name)s]: %(message)s",
    level=logging.INFO
)


def log_event(level, message, event, **kwargs):
    """Structured log event"""

    log_message = (
        f"service_name: {SERVICE_NAME}| "
        f"event: {message}, "
        f"json_payload: {json.dumps(event)}, "
        f"additional_info: {json.dumps(kwargs)}"
    )

    if level == "info":
        logging.info(log_message)
    elif level == "warning":
        logging.warning(log_message)
    elif level == "error":
        logging.error(log_message)


# variables
BQ_TABLE = os.getenv("BQ_TABLE", "observability.project_info")
FOLDER_ID = os.getenv("FOLDER_ID", "1062810406170")
PROJECT_ID = os.getenv("GCP_PROJECT", "dev2-ea8f")

if not BQ_TABLE or not FOLDER_ID or not PROJECT_ID:
    log_event("error", "Missing environment variables", "config_error")


def get_projects(folder_id):
    """Fetches projects from GCP Resource Manager API."""
    projects = []

    try:
        start_time = time.time()
        client = resourcemanager_v3.ProjectsClient()
        request = resourcemanager_v3.ListProjectsRequest(
            parent=f"folders/{folder_id}")
        projects = list(client.list_projects(request=request))
        duration = time.time() - start_time
        monitor("dfc_prj_api_duration", duration)

        if not projects:
            log_event(
                "warning",
                f"No projects found under folder {folder_id}",
                "load"
            )

    except exceptions.InvalidArgument as e:
        log_event(
            "error", f"Invalid folder ID: {str(e)}", "load", error=str(e)
        )
    except exceptions.PermissionDenied as e:
        log_event(
            "error", f"Permission denied to access folder: {str(e)}",
            "load", error=str(e)
        )
    except exceptions.NotFound as e:
        log_event(
            "error", f"Folder not found: {str(e)}", "load", error=str(e)
        )
    except exceptions.ServiceUnavailable as e:
        log_event(
            "error", f"Resource Manager API service unavailable: {str(e)}",
            "load", error=str(e))
    except exceptions.DeadlineExceeded as e:
        log_event(
            "error", f"Resource Manager API request timed out: {str(e)}",
            "load", error=str(e))
    except exceptions.GoogleAPICallError as e:
        log_event(
            "error", f"General Resource Manager API error: {str(e)}",
            "load", error=str(e))
    except KeyError as e:
        log_event("error", f"Key error: {str(e)}", "load", error=str(e))
    except ValueError as e:
        log_event("error", f"Value error: {str(e)}", "load", error=str(e))
    except TimeoutError as e:
        log_event("error", f"Timeout error: {str(e)}", "load", error=str(e))
    except Exception as e:  # pylint: disable=broad-except
        log_event("error", f"Unexpected error: {str(e)}", "load", error=str(e))

    return projects


def transform(projects):
    """Transforms GCP project data for BigQuery."""
    start_time = time.time()
    ingestion_timestamp = datetime.now(timezone.utc).isoformat()
    rows = []

    for project in projects:
        try:
            project_dict = MessageToDict(
                project._pb,  # pylint: disable=W0212
                preserving_proto_field_name=True)

            labels = project_dict.get("labels", {})
            labels_list = [{"key": k, "value": v} for k, v in labels.items()]

            row = {
                "project_id": project_dict.get("project_id"),
                "project_number": project_dict.get("name"),
                "folder_id": project_dict.get("parent"),
                "project_name": project_dict.get("display_name"),
                "state": project_dict.get("state"),
                "create_time": project_dict.get("create_time"),
                "update_time": project_dict.get("update_time"),
                "ingestion_time": ingestion_timestamp,
                "etag": project_dict.get("etag"),
                "labels": labels_list,
            }
            rows.append(row)

        except Exception as e:  # pylint: disable=broad-except
            log_event("error", "Error transforming project data",
                      "transform", error=str(e))

    duration = time.time() - start_time
    monitor("dfc_prj_processing_duration", duration)
    return rows


def store(rows):
    """Inserts transformed project data into BigQuery."""
    success = False
    start_time = time.time()
    if not rows:
        log_event("warning", "No data to insert into BigQuery", "store")
        return success
    try:
        errors = bq_client.insert_rows_json(BQ_TABLE, rows)
        if errors:
            log_event("error", "Failed to insert data into project_info",
                      "store", errors=errors)
        else:
            monitor("dfc_bigquery_insert_duration", time.time() - start_time)
            success = True
    except exceptions.BadRequest as e:
        log_event("error", "BigQuery Bad Request error", "store", error=str(e))
    except exceptions.NotFound as e:
        log_event("error", "BigQuery Not Found error", "store", error=str(e))
    except exceptions.Forbidden as e:
        log_event("error", "BigQuery Forbidden error", "store", error=str(e))
    except exceptions.ServiceUnavailable as e:
        log_event("error", "BigQuery Service Unavailable error",
                  "store", error=str(e))
    except exceptions.TooManyRequests as e:
        log_event("error", "BigQuery Too Many Requests error",
                  "store", error=str(e))
    except exceptions.GoogleAPICallError as e:
        log_event("error", "General BigQuery API error", "store", error=str(e))
    except TypeError as e:
        log_event("error", "Type error during BigQuery insertion",
                  "store", error=str(e))
    except ValueError as e:
        log_event("error", "Value error during BigQuery insertion",
                  "store", error=str(e))
    except Exception as e:  # pylint: disable=broad-except
        log_event(
            "error", "Unable to insert to project_info", "store", error=str(e))
    return success


def monitor(metric_name, value):
    """Reports a custom metric to Cloud Monitoring."""
    if not metric_name:
        log_event("error", "Metric name is required", "monitor")
        return

    if value is None:
        log_event("error", "Metric value is required",
                  "monitor", metric_name=metric_name)
        return

    try:
        series = monitoring_v3.TimeSeries()
        series.metric.type = f"custom.googleapis.com/{metric_name}"
        now = time.time()
        timestamp = Timestamp(seconds=int(
            now), nanos=int((now - int(now)) * 1e9))

        interval = monitoring_v3.TimeInterval(
            start_time=timestamp, end_time=timestamp)
        point = monitoring_v3.Point(
            interval=interval,
            value=monitoring_v3.TypedValue(double_value=value))
        series.points = [point]

        monitoring_client.create_time_series(
            name=f"projects/{PROJECT_ID}", time_series=[series])

    except exceptions.InvalidArgument as e:
        log_event("error", "Invalid argument for Cloud Monitoring",
                  "monitor", metric_name=metric_name, error=str(e))
    except exceptions.PermissionDenied as e:
        log_event("error", "Permission denied for Cloud Monitoring",
                  "monitor", metric_name=metric_name, error=str(e))
    except exceptions.ServiceUnavailable as e:
        log_event("error", "Cloud Monitoring service unavailable",
                  "monitor", metric_name=metric_name, error=str(e))
    except exceptions.DeadlineExceeded as e:
        log_event("error", "Cloud Monitoring request timed out",
                  "monitor", metric_name=metric_name, error=str(e))
    except exceptions.GoogleAPICallError as e:
        log_event("error", "General Google API error", "monitor",
                  metric_name=metric_name, error=str(e))
    except TypeError as e:
        log_event("error", "Type error during metric creation",
                  "monitor", metric_name=metric_name, error=str(e))
    except ValueError as e:
        log_event("error", "Value error during metric creation",
                  "monitor", metric_name=metric_name, error=str(e))
    except Exception as e:  # pylint: disable=broad-except
        log_event("error", "Failed to report metric", "monitor",
                  metric_name=metric_name, error=str(e))


@functions_framework.http
def main(request):
    """Main Cloud Function entry point (HTTP Triggered)."""
    start_time = time.time()
    log_event("info", "batch triggered : {start_time}",
              {"method": request.method, "path": request.path})
    try:
        projects = get_projects(FOLDER_ID)
        if projects:
            transformed_data = transform(projects)
            store(transformed_data)
        else:
            log_event("info", "No projects to process", "complete")
        monitor("dfc_prj_total_duration", time.time() - start_time)
        return "Project details loaded successfully"

    except exceptions.GoogleAPICallError as e:
        log_event(
            "error",
            f"Google API error during main execution: {str(e)}",
            "main",
            error=str(e)
        )
        return "Error occurred while processing the request", 500

    except TimeoutError as e:
        log_event(
            "error",
            f"Timeout error during main execution: {str(e)}",
            "main", error=str(e)
        )
        return "Request timed out", 500

    except Exception as e:  # pylint: disable=broad-except
        log_event(
            "error",
            f"Unexpected error during main execution: {str(e)}",
            "main",
            error=str(e)
        )
        return "Internal server error", 500
