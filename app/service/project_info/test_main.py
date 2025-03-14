from unittest.mock import patch, MagicMock

from google.cloud import resourcemanager_v3, bigquery, monitoring_v3
from google.protobuf.json_format import MessageToDict
from google.protobuf.timestamp_pb2 import Timestamp
from google.api_core.exceptions import GoogleAPIError

import main  

def test_get_projects_success(monkeypatch):
    mock_projects_client = MagicMock()
    mock_list_projects = mock_projects_client.return_value.list_projects = MagicMock()
    mock_project = MagicMock()
    mock_list_projects.return_value = [mock_project]

    monkeypatch.setattr("main.resourcemanager_v3.ProjectsClient", lambda: mock_projects_client.return_value)

    projects = main.get_projects("test_folder")
    assert projects == [mock_project]

def test_get_projects_no_projects(monkeypatch):
    mock_projects_client = MagicMock()
    mock_list_projects = mock_projects_client.return_value.list_projects = MagicMock()
    mock_list_projects.return_value = []

    monkeypatch.setattr("main.resourcemanager_v3.ProjectsClient", lambda: mock_projects_client.return_value)

    projects = main.get_projects("test_folder")
    assert projects == []

def test_get_projects_api_error(monkeypatch):
    mock_projects_client = MagicMock()
    mock_list_projects = mock_projects_client.return_value.list_projects = MagicMock()
    mock_list_projects.side_effect = GoogleAPIError("API Error")

    monkeypatch.setattr("main.resourcemanager_v3.ProjectsClient", lambda: mock_projects_client.return_value)

    projects = main.get_projects("test_folder")
    assert projects == []

def test_get_projects_unexpected_error(monkeypatch):
    mock_projects_client = MagicMock()
    mock_list_projects = mock_projects_client.return_value.list_projects = MagicMock()
    mock_list_projects.side_effect = Exception("Unexpected Error")

    monkeypatch.setattr("main.resourcemanager_v3.ProjectsClient", lambda: mock_projects_client.return_value)

    projects = main.get_projects("test_folder")
    assert projects == []

@patch("main.MessageToDict")
def test_transform(mock_message_to_dict):
    mock_message_to_dict.return_value = {
        "project_id": "test_project_id",
        "name": "test_project_number",
        "display_name": "test_project_name",
        "labels": {"key1": "value1"},
        "state": "ACTIVE",
        "parent": "test_folder_id",
        "etag": "test_etag",
        "create_time": "test_create_time",
        "update_time": "test_update_time"
    }
    transformed_data = main.transform([MagicMock()])
    assert len(transformed_data) == 1
    assert transformed_data[0]["project_id"] == "test_project_id"
    assert transformed_data[0]["project_number"] == "test_project_number"
    assert transformed_data[0]["project_name"] == "test_project_name"
    assert transformed_data[0]["folder_id"] == "test_folder_id"
    assert transformed_data[0]["labels"] == [{"key": "key1", "value": "value1"}]

@patch("main.bq_client")
def test_store_success(mock_bq_client):
    mock_insert_rows_json = mock_bq_client.insert_rows_json = MagicMock(return_value=[])
    main.BQ_TABLE = "observability.project_info"
    rows = [{"project_id": "test_project_id", "project_number": "test_project_number"}]
    result = main.store(rows)
    assert result is True
    mock_insert_rows_json.assert_called_once_with("observability.project_info", rows)

def test_store_no_data():
    result = main.store([])
    assert result is False

def test_store_bigquery_error(monkeypatch):
    mock_bigquery_client = MagicMock()
    mock_insert_rows_json = mock_bigquery_client.return_value.insert_rows_json = MagicMock()
    mock_insert_rows_json.side_effect = GoogleAPIError("BigQuery Error")
    monkeypatch.setattr("main.bigquery.Client", lambda: mock_bigquery_client.return_value)
    rows = [{"project_id": "test_project_id"}]
    result = main.store(rows)
    assert result is False

def test_store_unexpected_error(monkeypatch):
    mock_bigquery_client = MagicMock()
    mock_insert_rows_json = mock_bigquery_client.return_value.insert_rows_json = MagicMock()
    mock_insert_rows_json.side_effect = Exception("Unexpected Error")
    monkeypatch.setattr("main.bigquery.Client", lambda: mock_bigquery_client.return_value)
    rows = [{"project_id": "test_project_id"}]
    result = main.store(rows)
    assert result is False

@patch("main.monitoring_client")
def test_monitor(mock_monitoring_client):
    mock_create_time_series = mock_monitoring_client.create_time_series = MagicMock(return_value=None)
    main.PROJECT_ID = "test_project"
    main._monitor("test_metric", 1.0)
    mock_create_time_series.assert_called_once()

def test_main_success(monkeypatch):
    mock_get_projects = MagicMock(return_value=[MagicMock()])
    mock_transform = MagicMock(return_value=[{"project_id": "test_project_id", "project_number": "test_project_number"}])
    mock_store = MagicMock(return_value=True)

    monkeypatch.setattr("main.get_projects", mock_get_projects)
    monkeypatch.setattr("main.transform", mock_transform)
    monkeypatch.setattr("main.store", mock_store)
    monkeypatch.setenv("GCP_PROJECT", "test_project")

    result = main.main(MagicMock())
    assert result == "Project details loaded successfully"
    mock_get_projects.assert_called_once_with("1062810406170")
    mock_transform.assert_called_once()
    mock_store.assert_called_once()

def test_main_no_projects(monkeypatch):
    mock_get_projects = MagicMock(return_value=[])
    monkeypatch.setattr("main.get_projects", mock_get_projects)
    result = main.main(MagicMock())
    assert result == "Project details loaded successfully"