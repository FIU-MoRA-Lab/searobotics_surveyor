from surveyor_lib.helpers import (
    are_coordinates_close,
    get_attitude,
    get_attitude_message,
    get_command_status,
    get_command_status_message,
    get_coordinates,
    get_gga,
    process_surveyor_message,
)

# Sample messages
GGA_VALID = "$GPGGA,115739.00,4158.8441,N,09147.4416,W,4,13,0.9,255.747,M,-32.00,M,01,0000*6E\r\n"
GGA_INVALID = "$GPGGA,,,,,,0,,,,M,,M,,*66\r\n"
ATTITUDE_MSG = "$PSEAA,12.34,56.78,-90.12,34.56,18.0,0.5,-0.2,0.8,1.5*7F\r\n"
COMMAND_MSG = "$PSEAD,1.5,T,2.5,0.5*7A\r\n"


def test_are_coordinates_close_true():
    coord1 = (25.7617, -80.1918)
    coord2 = (25.7618, -80.1919)
    assert are_coordinates_close(coord1, coord2, tolerance_meters=20)


def test_are_coordinates_close_false():
    coord1 = (25.7617, -80.1918)
    coord2 = (25.7650, -80.2000)
    assert not are_coordinates_close(coord1, coord2, tolerance_meters=5)


def test_get_gga_valid():
    msg = GGA_VALID + "$PSEAA,..."
    assert get_gga(msg) == GGA_VALID.strip()


def test_get_attitude_message():
    msg = ATTITUDE_MSG + "$GPGGA,..."
    assert get_attitude_message(msg) == ATTITUDE_MSG.strip()


def test_get_command_status_message():
    msg = COMMAND_MSG + "$GPGGA,..."
    assert get_command_status_message(msg) == COMMAND_MSG.strip()


def test_get_coordinates_valid():
    coords = get_coordinates(GGA_VALID)
    assert coords["Latitude"] != 0.0 and coords["Longitude"] != 0.0


def test_get_coordinates_invalid():
    coords = get_coordinates(GGA_INVALID)
    assert coords == {"Latitude": 0.0, "Longitude": 0.0}


def test_get_attitude_parsing():
    result = get_attitude(ATTITUDE_MSG)
    assert result["Pitch (degrees)"] == 12.34
    assert result["Yaw rate [degrees/s]"] == 1.5


def test_get_command_status_parsing():
    result = get_command_status(COMMAND_MSG)
    assert result["Control Mode"] == 1.5
    assert result["Heading (degrees Magnetic)"] == "Thruster"


def test_process_surveyor_message_dispatch():
    msg = GGA_VALID + "\r\n" + ATTITUDE_MSG + "\r\n" + COMMAND_MSG
    result = process_surveyor_message(msg)
    assert (
        "Latitude" in result
        and "Pitch (degrees)" in result
        and "Control Mode" in result
    )


def test_process_surveyor_message_empty():
    result = process_surveyor_message("")
    assert "Day" in result and "Time" in result
