import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from gnss_parser.novatel import (
    NovatelAsciiParseError,
    iter_psrvel,
    parse_psrvel_line,
    read_psrvel,
)

SAMPLE = "#PSRVELA,USB1,0,51.5,FINESTEERING,2209,511827.000,02000020,0dd6,16809;SOL_COMPUTED,WAAS,0.000,4.000,0.0175,290.743174,0.0309,0*3d24adcc"


class TestPsrvel(unittest.TestCase):
    def test_parse_official_sample(self):
        record = parse_psrvel_line(SAMPLE, verify_crc=True)
        self.assertEqual(record.sol_status, "SOL_COMPUTED")
        self.assertEqual(record.vel_type, "WAAS")
        self.assertEqual(record.latency_s, 0.0)
        self.assertEqual(record.age_s, 4.0)
        self.assertAlmostEqual(record.hor_speed_mps, 0.0175)
        self.assertAlmostEqual(record.track_deg, 290.743174)
        self.assertAlmostEqual(record.vert_speed_mps, 0.0309)
        self.assertEqual(record.week, 2209)
        self.assertEqual(record.sow, 511827.0)
        self.assertEqual(record.time_status, "FINESTEERING")

    def test_mixed_log_exact_matching(self):
        text = "\n".join(
            [
                "$GPRMC,unrelated",
                SAMPLE.replace("#PSRVELA", "#PSRVEL2A"),
                SAMPLE,
            ]
        )
        records = read_psrvel(io.StringIO(text), verify_crc=True)
        self.assertEqual(len(records), 1)

    def test_tolerant_skips_malformed_target(self):
        bad = SAMPLE.replace(",0.0309,0*", ",BAD,0*")
        records = list(iter_psrvel(io.StringIO(bad + "\n" + SAMPLE)))
        self.assertEqual(len(records), 1)

    def test_strict_reports_line_number(self):
        bad = SAMPLE.replace(",0.0309,0*", ",BAD,0*")
        with self.assertRaisesRegex(NovatelAsciiParseError, "line 2:"):
            list(iter_psrvel(io.StringIO("$GPRMC,x\n" + bad), strict=True))

    def test_no_hidden_solution_filter(self):
        bad_status = SAMPLE.replace(
            "SOL_COMPUTED,WAAS", "INSUFFICIENT_OBS,NONE"
        )
        record = parse_psrvel_line(bad_status)
        self.assertEqual(record.sol_status, "INSUFFICIENT_OBS")
        self.assertEqual(record.vel_type, "NONE")

    def test_wrong_body_field_count(self):
        truncated = SAMPLE.replace(",0.0309,0*", ",0.0309*")
        with self.assertRaisesRegex(
            NovatelAsciiParseError, "requires 8 body fields"
        ):
            parse_psrvel_line(truncated)


if __name__ == "__main__":
    unittest.main()
