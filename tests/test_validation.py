import csv
import tempfile
import unittest
from pathlib import Path

from gnss_parser.validation import validate_real_log
from gnss_parser.validation_compare import compare_validation_outputs

FIXTURE = Path(__file__).parent / "fixtures" / "cross_language" / "sample.log"


class RealLogValidationTests(unittest.TestCase):
    def test_validation_outputs_shared_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "python"
            summary = validate_real_log(FIXTURE, out, verify_crc=True, verify_checksum=True)
            self.assertEqual(summary["stats"]["total_lines"], 7)
            self.assertEqual(summary["stats"]["unrelated_lines"], 1)
            for key in summary["stats"]["selected_messages"]:
                self.assertEqual(summary["messages"][key]["records"], 1)
                self.assertEqual(summary["messages"][key]["malformed"], 0)
                self.assertTrue((out / f"{key}.csv").exists())
            with (out / "range.csv").open(encoding="utf-8", newline="") as stream:
                row = next(csv.DictReader(stream))
            self.assertEqual(row["source_line_number"], "3")
            self.assertTrue(row["raw_line"].startswith("#RANGEA,"))
            self.assertEqual(row["prn"], "26")
            self.assertEqual(row["tracking_raw"], str(0x1810DC04))

    def test_comparator_passes_equal_outputs_and_fails_changed_field(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            left = Path(tmp) / "python"; right = Path(tmp) / "matlab"
            validate_real_log(FIXTURE, left, implementation="python")
            validate_real_log(FIXTURE, right, implementation="matlab")
            self.assertEqual(compare_validation_outputs(left, right)["status"], "PASS")
            path = right / "psrvel.csv"
            text = path.read_text(encoding="utf-8").replace("290.743174", "291.743174")
            path.write_text(text, encoding="utf-8")
            report = compare_validation_outputs(left, right)
            self.assertEqual(report["status"], "FAIL")
            self.assertEqual(report["messages"]["psrvel"]["status"], "FAIL")

    def test_full_export_uses_same_fixture_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            summary = validate_real_log(FIXTURE, tmp, full_export=True)
            self.assertEqual(summary["messages"]["range"]["exported_rows"], 1)
            self.assertEqual(summary["messages"]["psrvel"]["export_mode"], "full")


if __name__ == "__main__":
    unittest.main()
