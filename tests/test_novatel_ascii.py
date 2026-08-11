import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from gnss_parser.novatel.ascii import (
    NovatelAsciiParseError,
    novatel_crc32,
    parse_ascii_line,
    peek_ascii_message_name,
)

SAMPLE = "#PSRVELA,USB1,0,51.5,FINESTEERING,2209,511827.000,02000020,0dd6,16809;SOL_COMPUTED,WAAS,0.000,4.000,0.0175,290.743174,0.0309,0*3d24adcc"


class TestNovatelAscii(unittest.TestCase):
    def test_official_psrvel_sample_header_and_crc(self):
        msg = parse_ascii_line(SAMPLE, verify_crc=True)
        self.assertEqual(msg.header.message, "PSRVELA")
        self.assertEqual(msg.header.port, "USB1")
        self.assertEqual(msg.header.week, 2209)
        self.assertEqual(msg.header.sow, 511827.0)
        self.assertEqual(msg.header.receiver_status, 0x02000020)
        self.assertEqual(msg.header.reserved, 0x0DD6)
        self.assertEqual(msg.header.software_version, 16809)
        self.assertEqual(msg.crc, 0x3D24ADCC)
        self.assertEqual(
            novatel_crc32(SAMPLE[1:SAMPLE.rfind("*")].encode("ascii")),
            0x3D24ADCC,
        )

    def test_exact_message_peek(self):
        self.assertEqual(peek_ascii_message_name(SAMPLE), "PSRVELA")
        self.assertEqual(
            peek_ascii_message_name("#PSRVEL2A,COM1,0;1*00000000"),
            "PSRVEL2A",
        )
        self.assertIsNone(peek_ascii_message_name("$GPRMC,1"))

    def test_expected_message_is_exact(self):
        with self.assertRaises(NovatelAsciiParseError):
            parse_ascii_line(SAMPLE, expected_message="PSRVEL")

    def test_crc_mismatch(self):
        bad = SAMPLE[:-8] + "00000000"
        with self.assertRaisesRegex(NovatelAsciiParseError, "CRC mismatch"):
            parse_ascii_line(bad, verify_crc=True)

    def test_truncated_header(self):
        with self.assertRaises(NovatelAsciiParseError):
            parse_ascii_line("#PSRVELA,USB1,0;A*00000000")


if __name__ == "__main__":
    unittest.main()
