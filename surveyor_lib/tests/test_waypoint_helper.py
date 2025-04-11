import pandas as pd

from surveyor_lib.helpers import (
    compute_nmea_checksum,
    convert_lat_to_nmea_degrees_minutes,
    convert_lon_to_nmea_degrees_minutes,
    create_nmea_message,
    create_waypoint_message,
    create_waypoint_messages_df,
    create_waypoint_messages_df_from_list,
    create_waypoint_mission,
    get_hemisphere_lat,
    get_hemisphere_lon,
)


def test_compute_nmea_checksum():
    assert compute_nmea_checksum("GPGGA,123456") == "7D"


def test_convert_lat_to_nmea_degrees_minutes():
    assert convert_lat_to_nmea_degrees_minutes(25.5) == "2530.0000"


def test_convert_lon_to_nmea_degrees_minutes():
    assert convert_lon_to_nmea_degrees_minutes(-80.75) == "08045.0000"


def test_get_hemisphere_lat():
    assert get_hemisphere_lat(10.0) == "N"
    assert get_hemisphere_lat(-10.0) == "S"


def test_get_hemisphere_lon():
    assert get_hemisphere_lon(100.0) == "E"
    assert get_hemisphere_lon(-100.0) == "W"


def test_create_nmea_message():
    msg = "GPGGA,123456"
    expected_checksum = compute_nmea_checksum(msg)
    assert create_nmea_message(msg) == f"${msg}*{expected_checksum}\r\n"


def test_create_waypoint_message():
    msg = create_waypoint_message("2530.0000", "N", "08045.0000", "W", 1)
    assert msg == "OIWPL,2530.0000,N,08045.0000,W,1"


def test_create_waypoint_messages_df(tmp_path):
    # Create dummy waypoint and ERP CSVs
    waypoints_csv = tmp_path / "waypoints.csv"
    erp_csv = tmp_path / "erp.csv"
    waypoints_csv.write_text("latitude,longitude\n25.5,-80.75\n26.0,-80.6\n")
    erp_csv.write_text("latitude,longitude\n25.4,-80.8\n")

    df = create_waypoint_messages_df(str(waypoints_csv), str(erp_csv))
    assert len(df) == 3
    assert all(col in df.columns for col in ["nmea_waypoints", "nmea_message"])


def test_create_waypoint_messages_df_from_list(tmp_path):
    waypoints = [(25.5, -80.75), (26.0, -80.6)]
    erp = [(25.4, -80.8)]
    df = create_waypoint_messages_df_from_list(waypoints, erp)
    assert len(df) == 3
    assert all(col in df.columns for col in ["nmea_waypoints", "nmea_message"])


def test_create_waypoint_mission():
    df = pd.DataFrame(
        {
            "nmea_message": [
                create_nmea_message("OIWPL,2530.0000,N,08045.0000,W,0"),
                create_nmea_message("OIWPL,2600.0000,N,08036.0000,W,1"),
            ]
        }
    )
    mission = create_waypoint_mission(df, throttle=30)
    assert mission.startswith("PSEAR,0,000,30,0,000*")
    assert "OIWPL,2530.0000" in mission
    assert mission.endswith("\r\n")
