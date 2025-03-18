"""
    Summary : unit test scripts
"""
from unittest.mock import patch, MagicMock
from google.api_core import exceptions

import main


def test_get_projects_success(monkeypatch):
    """_summary_

    Args:
        monkeypatch (_type_): _description_
    """
    mock_projects_client = MagicMock()
    mock_list_projects = (
        mock_projects_client.return_value.list_projects
    ) = MagicMock()
    mock_project = MagicMock()
    mock_list_projects.return_value = [mock_project]

    monkeypatch.setattr(
        "main.resourcemanager_v3.ProjectsClient",
        lambda: mock_projects_client.return_value,
    )

    projects = main.get_projects("test_folder")
    assert projects == [mock_project]


def test_get_projects_no_projects(monkeypatch):
    """_summary_

    Args:
        monkeypatch (_type_): _description_
    """
    mock_projects_client = MagicMock()
    mock_list_projects = (
        mock_projects_client.return_value.list_projects
    ) = MagicMock()
    mock_list_projects.return_value = []

    monkeypatch.setattr(
        "main.resourcemanager_v3.ProjectsClient",
        lambda: mock_projects_client.return_value,
    )

    projects = main.get_projects("test_folder")
    assert not projects


def test_get_projects_invalid_argument(monkeypatch):
    """_summary_

    Args:
        monkeypatch (_type_): _description_
    """
    mock_projects_client = MagicMock()
    mock_list_projects = (
        mock_projects_client.return_value.list_projects
    ) = MagicMock()
    mock_list_projects.side_effect = exceptions.InvalidArgument(
        "Invalid Argument")

    monkeypatch.setattr(
        "main.resourcemanager_v3.ProjectsClient",
        lambda: mock_projects_client.return_value,
    )

    projects = main.get_projects("test_folder")
    assert not projects


def test_get_projects_permission_denied(monkeypatch):
    """_summary_

    Args:
        monkeypatch (_type_): _description_
    """
    mock_projects_client = MagicMock()
    mock_list_projects = (
        mock_projects_client.return_value.list_projects
    ) = MagicMock()
    mock_list_projects.side_effect = exceptions.PermissionDenied(
        "Permission Denied")

    monkeypatch.setattr(
        "main.resourcemanager_v3.ProjectsClient",
        lambda: mock_projects_client.return_value,
    )

    projects = main.get_projects("test_folder")
    assert not projects


def test_get_projects_not_found(monkeypatch):
    """_summary_

    Args:
        monkeypatch (_type_): _description_
    """
    mock_projects_client = MagicMock()
    mock_list_projects = (
        mock_projects_client.return_value.list_projects
    ) = MagicMock()
    mock_list_projects.side_effect = exceptions.NotFound("Not Found")

    monkeypatch.setattr(
        "main.resourcemanager_v3.ProjectsClient",
        lambda: mock_projects_client.return_value,
    )

    projects = main.get_projects("test_folder")
    assert not projects


def test_get_projects_service_unavailable(monkeypatch):
    """_summary_

    Args:
        monkeypatch (_type_): _description_
    """
    mock_projects_client = MagicMock()
    mock_list_projects = (
        mock_projects_client.return_value.list_projects
    ) = MagicMock()
    mock_list_projects.side_effect = exceptions.ServiceUnavailable(
        "Service Unavailable"
    )

    monkeypatch.setattr(
        "main.resourcemanager_v3.ProjectsClient",
        lambda: mock_projects_client.return_value,
    )

    projects = main.get_projects("test_folder")
    assert not projects


def test_get_projects_deadline_exceeded(monkeypatch):
    """_summary_

    Args:
        monkeypatch (_type_): _description_
    """
    mock_projects_client = MagicMock()
    mock_list_projects = (
        mock_projects_client.return_value.list_projects
    ) = MagicMock()
    mock_list_projects.side_effect = exceptions.DeadlineExceeded(
        "Deadline Exceeded")

    monkeypatch.setattr(
        "main.resourcemanager_v3.ProjectsClient",
        lambda: mock_projects_client.return_value,
    )

    projects = main.get_projects("test_folder")
    assert not projects


def test_get_projects_google_api_call_error(monkeypatch):
    """_summary_

    Args:
        monkeypatch (_type_): _description_
    """
    mock_projects_client = MagicMock()
    mock_list_projects = (
        mock_projects_client.return_value.list_projects
    ) = MagicMock()
    mock_list_projects.side_effect = exceptions.GoogleAPICallError(
        "Google API Call Error"
    )

    monkeypatch.setattr(
        "main.resourcemanager_v3.ProjectsClient",
        lambda: mock_projects_client.return_value,
    )

    projects = main.get_projects("test_folder")
    assert not projects


def test_get_projects_key_error(monkeypatch):
    """_summary_

    Args:
        monkeypatch (_type_): _description_
    """
    mock_projects_client = MagicMock()
    mock_list_projects = (
        mock_projects_client.return_value.list_projects
    ) = MagicMock()
    mock_list_projects.side_effect = KeyError("Key Error")

    monkeypatch.setattr(
        "main.resourcemanager_v3.ProjectsClient",
        lambda: mock_projects_client.return_value,
    )

    projects = main.get_projects("test_folder")
    assert not projects


def test_get_projects_value_error(monkeypatch):
    """_summary_

    Args:
        monkeypatch (_type_): _description_
    """
    mock_projects_client = MagicMock()
    mock_list_projects = (
        mock_projects_client.return_value.list_projects
    ) = MagicMock()
    mock_list_projects.side_effect = ValueError("Value Error")

    monkeypatch.setattr(
        "main.resourcemanager_v3.ProjectsClient",
        lambda: mock_projects_client.return_value,
    )

    projects = main.get_projects("test_folder")
    assert not projects


def test_get_projects_timeout_error(monkeypatch):
    """_summary_

    Args:
        monkeypatch (_type_): _description_
    """
    mock_projects_client = MagicMock()
    mock_list_projects = (
        mock_projects_client.return_value.list_projects
    ) = MagicMock()
    mock_list_projects.side_effect = TimeoutError("Timeout Error")

    monkeypatch.setattr(
        "main.resourcemanager_v3.ProjectsClient",
        lambda: mock_projects_client.return_value,
    )

    projects = main.get_projects("test_folder")
    assert not projects


def test_get_projects_unexpected_error(monkeypatch):
    """_summary_

    Args:
        monkeypatch (_type_): _description_
    """
    mock_projects_client = MagicMock()
    mock_list_projects = (
        mock_projects_client.return_value.list_projects
    ) = MagicMock()
    mock_list_projects.side_effect = Exception("Unexpected Error")

    monkeypatch.setattr(
        "main.resourcemanager_v3.ProjectsClient",
        lambda: mock_projects_client.return_value,
    )

    projects = main.get_projects("test_folder")
    assert not projects


@patch("main.MessageToDict")
def test_transform(mock_message_to_dict):
    """_summary_

    Args:
        mock_message_to_dict (_type_): _description_
    """
    mock_message_to_dict.return_value = {
        "project_id": "test_project_id",
        "name": "test_project_number",
        "display_name": "test_project_name",
        "labels": {"key1": "value1"},
        "state": "ACTIVE",
        "parent": "test_folder_id",
        "etag": "test_etag",
        "create_time": "test_create_time",
        "update_time": "test_update_time",
    }
    transformed_data = main.transform([MagicMock()])
    assert len(transformed_data) == 1
    assert transformed_data[0]["project_id"] == "test_project_id"
    assert transformed_data[0]["project_number"] == "test_project_number"
    assert transformed_data[0]["project_name"] == "test_project_name"
    assert transformed_data[0]["folder_id"] == "test_folder_id"
    assert transformed_data[0]["labels"] == [
        {"key": "key1", "value": "value1"}]


@patch("main.bq_client")
def test_store_success(mock_bq_client):
    """_summary_

    Args:
        mock_bq_client (_type_): _description_
    """
    mock_insert_rows_json = mock_bq_client.insert_rows_json = MagicMock(
        return_value=[])
    main.BQ_TABLE = "observability.project_info"
    rows = [{"project_id": "test_project_id",
             "project_number": "test_project_number"}]
    result = main.store(rows)
    assert result is True
    mock_insert_rows_json.assert_called_once_with(
        "observability.project_info", rows)


def test_store_no_data():
    """_summary_
    """
    result = main.store([])
    assert result is False


def test_store_bad_request(monkeypatch):
    """_summary_

    Args:
        monkeypatch (_type_): _description_
    """
    mock_bigquery_client = MagicMock()
    mock_insert_rows_json = MagicMock()
    mock_bigquery_client.return_value.insert_rows_json = mock_insert_rows_json
    mock_insert_rows_json.side_effect = exceptions.BadRequest("Bad Request")
    monkeypatch.setattr(
        "main.bigquery.Client", lambda: mock_bigquery_client.return_value
    )
    rows = [{"project_id": "test_project_id"}]
    result = main.store(rows)
    assert result is False


def test_store_not_found(monkeypatch):
    """_summary_

    Args:
        monkeypatch (_type_): _description_
    """
    mock_bigquery_client = MagicMock()
    mock_insert_rows_json = MagicMock()
    mock_bigquery_client.return_value.insert_rows_json = mock_insert_rows_json
    mock_insert_rows_json.side_effect = exceptions.NotFound("Not Found")
    monkeypatch.setattr(
        "main.bigquery.Client", lambda: mock_bigquery_client.return_value
    )
    rows = [{"project_id": "test_project_id"}]
    result = main.store(rows)
    assert result is False


def test_store_forbidden(monkeypatch):
    """_summary_

    Args:
        monkeypatch (_type_): _description_
    """
    mock_bigquery_client = MagicMock()
    mock_insert_rows_json = MagicMock()
    mock_bigquery_client.return_value.insert_rows_json = mock_insert_rows_json
    mock_insert_rows_json.side_effect = exceptions.Forbidden("Forbidden")
    monkeypatch.setattr(
        "main.bigquery.Client", lambda: mock_bigquery_client.return_value
    )
    rows = [{"project_id": "test_project_id"}]
    result = main.store(rows)
    assert result is False


def test_store_service_unavailable(monkeypatch):
    """_summary_

    Args:
        monkeypatch (_type_): _description_
    """
    mock_bigquery_client = MagicMock()
    mock_insert_rows_json = MagicMock()
    mock_bigquery_client.return_value.insert_rows_json = mock_insert_rows_json
    mock_insert_rows_json.side_effect = exceptions.ServiceUnavailable(
        "Service Unavailable"
    )
    monkeypatch.setattr(
        "main.bigquery.Client", lambda: mock_bigquery_client.return_value
    )
    rows = [{"project_id": "test_project_id"}]
    result = main.store(rows)
    assert result is False


def test_store_too_many_requests(monkeypatch):
    """_summary_

    Args:
        monkeypatch (_type_): _description_
    """
    mock_bigquery_client = MagicMock()
    mock_insert_rows_json = MagicMock()
    mock_bigquery_client.return_value.insert_rows_json = mock_insert_rows_json
    mock_insert_rows_json.side_effect = exceptions.TooManyRequests(
        "Too Many Requests")
    monkeypatch.setattr(
        "main.bigquery.Client", lambda: mock_bigquery_client.return_value
    )
    rows = [{"project_id": "test_project_id"}]
    result = main.store(rows)
    assert result is False


def test_store_google_api_call_error(monkeypatch):
    """_summary_

    Args:
        monkeypatch (_type_): _description_
    """
    mock_bigquery_client = MagicMock()
    mock_insert_rows_json = MagicMock()
    mock_bigquery_client.return_value.insert_rows_json = mock_insert_rows_json
    mock_insert_rows_json.side_effect = exceptions.GoogleAPICallError(
        "Google API Call Error"
    )
    monkeypatch.setattr(
        "main.bigquery.Client", lambda: mock_bigquery_client.return_value
    )
    rows = [{"project_id": "test_project_id"}]
    result = main.store(rows)
    assert result is False


def test_store_type_error(monkeypatch):
    """_summary_

    Args:
        monkeypatch (_type_): _description_
    """
    mock_bigquery_client = MagicMock()
    mock_insert_rows_json = MagicMock()
    mock_bigquery_client.return_value.insert_rows_json = mock_insert_rows_json
    mock_insert_rows_json.side_effect = TypeError("Type Error")
    monkeypatch.setattr(
        "main.bigquery.Client", lambda: mock_bigquery_client.return_value
    )
    rows = [{"project_id": "test_project_id"}]
    result = main.store(rows)
    assert result is False


def test_store_value_error(monkeypatch):
    """_summary_

    Args:
        monkeypatch (_type_): _description_
    """
    mock_bigquery_client = MagicMock()
    mock_insert_rows_json = MagicMock()
    mock_bigquery_client.return_value.insert_rows_json = mock_insert_rows_json
    mock_insert_rows_json.side_effect = ValueError("Value Error")
    monkeypatch.setattr(
        "main.bigquery.Client", lambda: mock_bigquery_client.return_value
    )
    rows = [{"project_id": "test_project_id"}]
    result = main.store(rows)
    assert result is False


def test_store_unexpected_error(monkeypatch):
    """_summary_

    Args:
        monkeypatch (_type_): _description_
    """
    mock_bigquery_client = MagicMock()
    mock_insert_rows_json = MagicMock()
    mock_bigquery_client.return_value.insert_rows_json = mock_insert_rows_json
    mock_insert_rows_json.side_effect = Exception("Unexpected Error")
    monkeypatch.setattr(
        "main.bigquery.Client", lambda: mock_bigquery_client.return_value
    )
    rows = [{"project_id": "test_project_id"}]
    result = main.store(rows)
    assert result is False


@patch("main.monitoring_client")
def test_monitor(mock_monitoring_client):
    """_summary_

    Args:
        mock_monitoring_client (_type_): _description_
    """
    mock_create_time_series = MagicMock(return_value=None)
    mock_monitoring_client.create_time_series = mock_create_time_series
    main.PROJECT_ID = "test_project"
    main.monitor("test_metric", 1.0)
    mock_create_time_series.assert_called_once()


def test_main_success(monkeypatch):
    """Test main function with successful execution."""

    mock_request = MagicMock()
    mock_request.method = "POST"
    mock_request.path = "/test-path"

    mock_get_projects = MagicMock(return_value=[{
        "project_id": "test_project_id",
        "name": "test_project_number",
        "parent": "test_folder_id",
        "display_name": "Test Project",
        "state": "ACTIVE",
        "create_time": "2025-03-18T12:00:00Z",
        "update_time": "2025-03-18T12:05:00Z",
        "etag": "test_etag",
        "labels": {"env": "test"}
    }])

    mock_transform = MagicMock(return_value=[
        {"project_id": "test_project_id",
         "project_number": "test_project_number"}
    ])

    mock_store = MagicMock(return_value=True)
    monkeypatch.setattr("main.FOLDER_ID", "test_project")
    monkeypatch.setattr("main.get_projects", mock_get_projects)
    monkeypatch.setattr("main.transform", mock_transform)
    monkeypatch.setattr("main.store", mock_store)

    # Call main function with a proper mock request
    result = main.main(mock_request)

    assert result == "Project details loaded successfully"
    mock_get_projects.assert_called_once_with(
        "test_project")  # Now it should match
    mock_transform.assert_called_once()
    mock_store.assert_called_once()


def test_main_no_projects(monkeypatch):
    """Test main function when no projects are returned."""

    mock_request = MagicMock()
    mock_request.method = "POST"
    mock_request.path = "/test-path"
    mock_get_projects = MagicMock(return_value=[])
    monkeypatch.setattr("main.get_projects", mock_get_projects)

    mock_log_event = MagicMock()
    monkeypatch.setattr("main.log_event", mock_log_event)

    monkeypatch.setattr("main.FOLDER_ID", "test_project")

    result = main.main(mock_request)
    assert result == "Project details loaded successfully"
    mock_get_projects.assert_called_once_with("test_project")
    mock_log_event.assert_any_call(
        "info", "No projects to process", "complete")
