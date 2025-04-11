import csv
import time
from datetime import date

from MockSurveyor import MockSurveyor

import surveyor_lib.helpers as hlp


def test_append_to_csv_and_save(tmp_path):
    # Setup test directory and patch output dir

    today = date.today().strftime("%Y%m%d")

    data = {"latitude": 25.0, "longitude": -80.0}
    hlp.save(data, post_fix="_test", dir_path=tmp_path)

    csv_path = tmp_path / f"{today}_test.csv"
    assert csv_path.exists()

    with open(csv_path, "r") as f:
        reader = list(csv.reader(f))
        assert reader[0] == ["latitude", "longitude"]
        assert reader[1] == ["25.0", "-80.0"]


def test_process_gga_and_save_data(tmp_path):
    mock_surveyor = MockSurveyor()
    hlp.process_gga_and_save_data.last_save_time = time.time() - 2

    result = hlp.process_gga_and_save_data(
        mock_surveyor,
        data_keys=None,
        delay=0.1,
        post_fix="_gps",
        dir_path=tmp_path,
    )

    today = date.today().strftime("%Y%m%d")
    csv_path = tmp_path / f"{today}_gps.csv"

    assert csv_path.exists()

    # Read the first data row as a dictionary
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        first_row = next(reader)

    # print(first_row)
    expected = result  # strings from CSV
    for key in result.keys():
        assert first_row[key] in (expected[key], str(expected[key]))


def test_read_csv_into_tuples(tmp_path):
    csv_path = tmp_path / "test.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["latitude", "longitude"])
        writer.writerow([25.1, -80.1])
        writer.writerow([25.2, -80.2])

    result = hlp.read_csv_into_tuples(csv_path)
    assert result == [(25.1, -80.1), (25.2, -80.2)]
