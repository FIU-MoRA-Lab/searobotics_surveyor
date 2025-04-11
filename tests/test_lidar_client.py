from unittest.mock import MagicMock, patch

import pytest

from surveyor_lib.clients.lidar_client import (  # Change surveyor_lib.clients to the actual package name
    LidarClient,
)


@pytest.fixture
def lidar_client():
    return LidarClient(server_ip="127.0.0.1", server_port="1234")


def test_lidar_client_initialization(lidar_client):
    assert lidar_client.server_ip == "127.0.0.1"
    assert lidar_client.server_port == "1234"
    assert lidar_client.server_url == "http://127.0.0.1:1234/data"
    assert lidar_client._angles == list(range(360))


@patch("surveyor_lib.clients.lidar_client.requests.get")
def test_get_data_success(mock_get, lidar_client):
    # Fake 360 distance values (in meters)
    fake_data = [1.0] * 360

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = fake_data
    mock_get.return_value = mock_response

    data, angles = lidar_client.get_data()

    assert data == fake_data
    assert angles == list(range(360))
    mock_get.assert_called_once_with("http://127.0.0.1:1234/data")


@patch("surveyor_lib.clients.lidar_client.requests.get")
def test_get_data_failure(mock_get, lidar_client, capsys):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    result = lidar_client.get_data()

    assert result is None
    captured = capsys.readouterr()
    assert "Failed to get RPLidar data: 500" in captured.out
