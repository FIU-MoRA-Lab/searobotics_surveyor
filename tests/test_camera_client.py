from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from surveyor_lib.clients.camera_client import CameraClient


@pytest.fixture
def mock_video_capture():
    with patch(
        "surveyor_lib.clients.camera_client.cv2.VideoCapture"
    ) as mock_vc:
        yield mock_vc


def test_camera_client_initialization_success(mock_video_capture):
    """Test successful initialization and stream start."""
    mock_instance = MagicMock()
    mock_instance.isOpened.return_value = True
    mock_instance.read.return_value = (
        True,
        np.ones((480, 640, 3), dtype=np.uint8),
    )
    mock_video_capture.return_value = mock_instance

    client = CameraClient(server_ip="127.0.0.1", server_port="1234")

    assert client.cap.isOpened()
    assert client.server_url.endswith("/video_feed")
    assert client._current_frame is None or isinstance(
        client._current_frame, np.ndarray
    )


def test_camera_client_get_image(mock_video_capture):
    """Test that get_image returns a tuple (bool, frame)."""
    fake_frame = np.ones((480, 640, 3), dtype=np.uint8)

    mock_instance = MagicMock()
    mock_instance.isOpened.return_value = True
    mock_instance.read.return_value = (True, fake_frame)
    mock_video_capture.return_value = mock_instance

    client = CameraClient()
    client._current_frame = fake_frame  # Simulate a frame being captured

    success, frame = client.get_data()

    assert success is True
    assert np.array_equal(frame, fake_frame)


def test_camera_client_connection_failure(mock_video_capture, capsys):
    """Test behavior when camera connection fails."""
    mock_instance = MagicMock()
    mock_instance.isOpened.return_value = False
    mock_video_capture.return_value = mock_instance

    CameraClient()

    captured = capsys.readouterr()
    assert "Unable to open video stream" in captured.out
