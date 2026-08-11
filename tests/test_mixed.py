import io
import unittest
from pathlib import Path

from gnss_parser.mixed import GnssLogStats, iter_gnss_log, read_gnss_log
from gnss_parser.novatel import (
    NovatelAsciiParseError,
    read_bestpos,
    read_bestvel,
    read_inspva,
    read_psrvel,
    read_range,
)
from gnss_parser.ublox import read_rmc


FIXTURE = Path(__file__).parent / "fixtures" / "cross_language" / "sample.log"


class MixedGnssLogTests(unittest.TestCase):
    def test_single_pass_matches_individual_readers(self) -> None:
        result = read_gnss_log(
            FIXTURE,
            verify_crc=True,
            verify_checksum=True,
        )
        expected = {
            "psrvel": read_psrvel(FIXTURE, verify_crc=True),
            "range": read_range(FIXTURE, verify_crc=True),
            "inspva": read_inspva(FIXTURE, verify_crc=True),
            "bestpos": read_bestpos(FIXTURE, verify_crc=True),
            "bestvel": read_bestvel(FIXTURE, verify_crc=True),
            "rmc": read_rmc(FIXTURE, verify_checksum=True),
        }
        for key, records in expected.items():
            self.assertEqual(result[key], records, key)

        self.assertEqual(result.stats.total_lines, 7)
        self.assertEqual(result.stats.unrelated_lines, 1)
        for key in expected:
            self.assertEqual(result.stats.target_lines[key], 1, key)
            self.assertEqual(result.stats.records[key], 1, key)
            self.assertEqual(result.stats.malformed[key], 0, key)

    def test_iterator_preserves_file_order_and_populates_stats(self) -> None:
        stats = GnssLogStats()
        events = list(iter_gnss_log(FIXTURE, stats=stats))
        self.assertEqual(
            [event.message_type for event in events],
            ["psrvel", "range", "inspva", "bestpos", "bestvel", "rmc"],
        )
        self.assertEqual([event.line_number for event in events], [2, 3, 4, 5, 6, 7])
        self.assertEqual(stats.total_lines, 7)
        self.assertEqual(stats.unrelated_lines, 1)

    def test_subset_is_still_one_scan_and_uses_stable_keys(self) -> None:
        result = read_gnss_log(FIXTURE, messages={"RANGEA", "RMC"})
        self.assertEqual(len(result["range"]), 1)
        self.assertEqual(len(result["rmc"]), 1)
        self.assertEqual(result["psrvel"], [])
        self.assertEqual(result.stats.selected_messages, ("range", "rmc"))
        self.assertEqual(result.stats.total_lines, 7)
        self.assertEqual(result.stats.unrelated_lines, 5)

    def test_unsupported_message_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported message type"):
            read_gnss_log(FIXTURE, messages={"GGA"})

    def test_tolerant_and_strict_malformed_target_behavior(self) -> None:
        text = (
            "#PSRVELA,bad*00000000\n"
            "$GPRMC,083559.00,A,4717.11437,N,00833.91522,E,0.004,77.52,091202,,,A,V*2D\n"
        )
        result = read_gnss_log(io.StringIO(text), messages={"PSRVEL", "RMC"})
        self.assertEqual(result.stats.malformed["psrvel"], 1)
        self.assertEqual(result.stats.records["rmc"], 1)
        self.assertEqual(len(result["rmc"]), 1)

        with self.assertRaisesRegex(NovatelAsciiParseError, r"line 1:"):
            list(
                iter_gnss_log(
                    io.StringIO(text),
                    messages={"PSRVEL", "RMC"},
                    strict=True,
                )
            )


if __name__ == "__main__":
    unittest.main()
