from __future__ import annotations

import io
from pathlib import Path
import sys
import tempfile
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON_DIR = REPO_ROOT / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from gnss_parser.common.gpst import GPS_SECONDS_PER_WEEK, GpsTime, normalize_gpst
from gnss_parser.common.io import iter_text_lines


class GpsTimeTests(unittest.TestCase):
    def test_absolute_seconds(self) -> None:
        value = GpsTime(week=2, sow=3.5)
        self.assertEqual(value.absolute_seconds, 2 * GPS_SECONDS_PER_WEEK + 3.5)

    def test_normalize_positive_week_overflow(self) -> None:
        week, sow = normalize_gpst(2426, GPS_SECONDS_PER_WEEK + 0.1)
        self.assertEqual(week, 2427)
        self.assertAlmostEqual(sow, 0.1, places=6)

    def test_normalize_negative_sow(self) -> None:
        week, sow = normalize_gpst(2426, -0.1)
        self.assertEqual(week, 2425)
        self.assertAlmostEqual(sow, GPS_SECONDS_PER_WEEK - 0.1, places=6)

    def test_record_preserves_raw_time_until_requested(self) -> None:
        value = GpsTime(week=2426, sow=GPS_SECONDS_PER_WEEK + 1.25)
        self.assertEqual(value.week, 2426)
        self.assertEqual(value.sow, GPS_SECONDS_PER_WEEK + 1.25)
        self.assertEqual(value.normalized(), GpsTime(week=2427, sow=1.25))

    def test_non_finite_sow_rejected_by_normalizer(self) -> None:
        with self.assertRaises(ValueError):
            normalize_gpst(2426, float("nan"))


class TextIoTests(unittest.TestCase):
    def test_existing_stream_is_not_closed(self) -> None:
        stream = io.StringIO(" first \r\nsecond\n")
        rows = list(iter_text_lines(stream))
        self.assertEqual(rows, [(1, " first "), (2, "second")])
        self.assertFalse(stream.closed)

    def test_path_input_streams_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "sample.log"
            path.write_text("A\nB\n", encoding="utf-8")
            self.assertEqual(list(iter_text_lines(path)), [(1, "A"), (2, "B")])


if __name__ == "__main__":
    unittest.main()
