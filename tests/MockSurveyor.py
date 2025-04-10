import numpy as np


class MockSurveyor:
    def get_data(
        self,
        keys=[
            "latitude",
            "longitude",
            "image",
            "lidar_data",
            "lidar_angle",
            "ret",
        ],
    ):
        data = {
            "latitude": 26.0,
            "longitude": -81.0,
            "image": np.random.randint(0, 255, (64, 128, 3), dtype=np.uint8),
            "lidar_data": np.random.rand(360).astype(np.float32),
            "lidar_angle": np.linspace(-np.pi, np.pi, 360, dtype=np.float32),
            "mode": "autonomous",
            "ret": True,
        }
        return {key: data.get(key, "unknown") for key in keys}
