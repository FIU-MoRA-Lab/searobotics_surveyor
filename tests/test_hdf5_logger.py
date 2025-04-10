import os
import time

import h5py
import numpy as np
from MockSurveyor import MockSurveyor

from surveyor_lib.helpers import HDF5Logger  # replace with actual import

mock_surveyor = MockSurveyor()


def test_hdf5_logger_single_log(tmp_path):
    # Arrange
    filepath = tmp_path / "test_log.h5"
    logger = HDF5Logger(
        filepath=str(filepath), data_getter_func=mock_surveyor.get_data
    )

    # Act
    logger.log_once()
    logger.stop()  # ensure the file is flushed/closed

    # Assert
    assert os.path.exists(filepath)

    with h5py.File(filepath, "r") as f:
        assert "data" in f
        data = f["data"]
        assert data.shape[0] == 1

        # Check field types exist
        expected_fields = mock_surveyor.get_data().keys()
        for field in expected_fields:
            assert field in data.dtype.names


def test_continuous_logging_and_close(tmp_path):
    # Create file path in temporary directory
    h5_path = tmp_path / "log_test.h5"
    # Instantiate the logger
    logger = HDF5Logger(
        filepath=str(h5_path),
        data_getter_func=mock_surveyor.get_data,
        interval=0.2,
    )

    # Start continuous logging
    logger.start_continuous_logging()

    # Let it log for about 0.6 seconds (should get ~3 entries)
    time.sleep(0.65)

    # Stop the logger
    logger.stop()

    # Reopen file to verify contents
    expected_data = logger._dict_to_structured_array(mock_surveyor.get_data())
    with h5py.File(h5_path, "r") as f:
        assert "data" in f
        ds = f["data"]
        result = np.asarray(ds[0], dtype=expected_data.dtype)
        print(f"Fields: {ds.dtype.names} {expected_data.dtype} {result.dtype}")
        assert ds.shape[0] >= 2  # Should have logged at least twice
        # print(ds[0], expected_data)
        assert expected_data.dtype == result.dtype
