import os
import threading
import time

import h5py
import numpy as np


class HDF5Logger:
    """Logs structured data to an HDF5 file at regular intervals."""

    def __init__(self, filepath, data_getter_func, interval=1.0):
        """
        Initializes the HDF5Logger.

        Args:
            filepath (str): Path to the HDF5 file to write to.
            data_getter_func (Callable): A function that returns a dictionary of data to log.
            interval (float): Time interval (in seconds) between consecutive logs in continuous mode.
        """
        self.filepath = filepath
        self.get_data = lambda: self._normalize_types_for_hdf5(
            data_getter_func()
        )
        self.interval = interval
        self._stopped = False
        self._file = None  # persistent HDF5 file handle
        self._thread = None

        example_data = self.get_data()
        if example_data not in (None, {}):
            self.state_dtype = self._infer_state_dtype(example_data)

        if not os.path.exists(self.filepath):
            self._init_file()

    def _init_file(self):
        """Initializes the HDF5 file with an extendable structured dataset."""
        with h5py.File(self.filepath, "w") as f:
            if hasattr(self, "state_dtype"):
                f.create_dataset(
                    "data",
                    shape=(0,),
                    maxshape=(None,),
                    dtype=self.state_dtype,
                    chunks=True,
                )

    @staticmethod
    def _infer_state_dtype(data_example_dict):
        """
        Infers the dtype of a structured NumPy array from a dictionary example.

        Args:
            data_example_dict (dict): Example dictionary with representative data.

        Returns:
            np.dtype: A structured dtype suitable for HDF5 storage.

        Raises:
            TypeError: If a value type is unsupported.
        """
        dtype_fields = []
        for key, value in data_example_dict.items():
            if isinstance(value, int):
                dtype_fields.append((key, "int32"))
            elif isinstance(value, float):
                dtype_fields.append((key, "float32"))
            elif isinstance(value, np.ndarray):
                dtype_fields.append((key, value.dtype.str, value.shape))
            elif isinstance(value, list):
                value = np.array(value)
                dtype_fields.append((key, value.dtype.str, value.shape))
            elif isinstance(value, str):
                dtype_fields.append((key, "S10", (1,)))
            else:
                raise TypeError(
                    f"Unsupported type for key '{key}': {type(value)}"
                )
        return np.dtype(dtype_fields)

    def _dict_to_structured_array(self, d):
        """
        Converts a dictionary to a single-entry structured NumPy array.

        Args:
            d (dict): Dictionary with values matching the logger's inferred dtype.

        Returns:
            np.ndarray: A structured array with one entry.
        """
        values = tuple(np.array(d[k]) for k in self.state_dtype.names)
        return np.array([values], dtype=self.state_dtype)

    def _open_file(self):
        """
        Opens the HDF5 file in append mode and stores the handle.

        Returns:
            h5py.File: The open HDF5 file object.
        """
        if self._file is None:
            self._file = h5py.File(self.filepath, "a")
        return self._file

    def log_once(self):
        """
        Logs a single data sample into the HDF5 file.
        """
        if not self._file or not self._file.id.valid:
            self._open_file()
        data = self.get_data()
        if data not in (None, {}):
            struct_data = self._dict_to_structured_array(data)
            f = self._file
            ds = f["data"]
            idx = ds.shape[0]
            ds.resize((idx + 1,))
            ds[idx] = struct_data

    def start_continuous_logging(self):
        """
        Starts a background thread that logs data continuously at the specified interval.
        """
        self._stopped = False
        self._open_file()
        self._thread = threading.Thread(target=self._run_logger, daemon=True)
        self._thread.start()

    def _run_logger(self):
        """
        The main loop for the background logging thread.
        """
        while not self._stopped:
            self.log_once()
            time.sleep(self.interval)

    def stop(self):
        """
        Stops the background logging thread and closes the HDF5 file.
        """
        self._stopped = True
        if self._thread:
            self._thread.join()
        if self._file:
            self._file.flush()
            self._file.close()
            self._file = None

    @staticmethod
    def _normalize_types_for_hdf5(data_dict):
        """
        Normalizes data types for compatibility with HDF5 structured storage.

        - Converts bools to integers.
        - Converts strings to numpy.str_.

        Args:
            data_dict (dict): Original data dictionary.

        Returns:
            dict: Dictionary with normalized types.
        """
        normalized = {}
        for key, value in data_dict.items():
            if isinstance(value, bool):
                normalized[key] = int(value)
            elif isinstance(value, str):
                normalized[key] = np.str_(value)
            else:
                normalized[key] = value
        return normalized
