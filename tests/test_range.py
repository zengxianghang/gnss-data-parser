import io
import unittest

from gnss_parser.novatel.ascii import NovatelAsciiParseError, novatel_crc32
from gnss_parser.novatel.range import (
    decode_tracking_status,
    iter_range,
    parse_range_line,
)


def sentence(body: str, crc: int | None = None) -> str:
    if crc is None:
        crc = novatel_crc32(body.encode("ascii"))
    return f"#{body}*{crc:08x}"


class RangeParserTests(unittest.TestCase):
    def test_parse_one_observation(self) -> None:
        body = (
            "RANGEA,USB1,0,54.0,FINESTEERING,2209,512449.000,02000020,5103,16809;"
            "1,26,0,24101771.233,0.199,-126655684.482618,0.012,2806.247,44.4,853.017,1810dc04"
        )
        record = parse_range_line(sentence(body), verify_crc=True)
        self.assertEqual(record.week, 2209)
        self.assertEqual(record.observation_count, 1)
        obs = record.observations[0]
        self.assertEqual(obs.prn, 26)
        self.assertAlmostEqual(obs.cn0_dbhz, 44.4)
        self.assertAlmostEqual(obs.doppler_hz, 2806.247)
        self.assertEqual(obs.tracking.raw, 0x1810DC04)
        self.assertEqual(obs.tracking.tracking_state, 4)
        self.assertTrue(obs.tracking.phase_locked)
        self.assertTrue(obs.tracking.parity_known)
        self.assertTrue(obs.tracking.code_locked)
        self.assertEqual(obs.tracking.satellite_system_name, "GPS")
        self.assertEqual(obs.tracking.signal_name, "L1CA")
        self.assertTrue(obs.tracking.primary_l1)
        self.assertTrue(obs.tracking.half_cycle_added)

    def test_decode_system_and_signal(self) -> None:
        value = (4 << 16) | (9 << 21) | (1 << 10) | (1 << 12)
        status = decode_tracking_status(value)
        self.assertEqual(status.satellite_system_name, "BEIDOU")
        self.assertEqual(status.signal_name, "B2AP")
        self.assertTrue(status.phase_locked)
        self.assertTrue(status.code_locked)
        self.assertFalse(status.parity_known)

    def test_observation_count_mismatch(self) -> None:
        body = (
            "RANGEA,USB1,0,54.0,FINESTEERING,2209,512449.000,02000020,5103,16809;"
            "2,26,0,1,1,1,1,1,1,1,1810dc04"
        )
        with self.assertRaises(NovatelAsciiParseError):
            parse_range_line(sentence(body))

    def test_iterator_skips_unrelated_and_malformed_by_default(self) -> None:
        good_body = (
            "RANGEA,USB1,0,54.0,FINESTEERING,2209,512449.000,02000020,5103,16809;"
            "1,26,0,1,1,1,1,1,1,1,1810dc04"
        )
        text = "#PSRVELA,bad*00000000\n#RANGEA,bad*00000000\n" + sentence(good_body) + "\n"
        records = list(iter_range(io.StringIO(text)))
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].observations[0].prn, 26)

    def test_strict_reports_source_line(self) -> None:
        with self.assertRaisesRegex(NovatelAsciiParseError, r"line 2:"):
            list(iter_range(io.StringIO("noise\n#RANGEA,bad*00000000\n"), strict=True))

    def test_crc_mismatch(self) -> None:
        body = (
            "RANGEA,USB1,0,54.0,FINESTEERING,2209,512449.000,02000020,5103,16809;0"
        )
        with self.assertRaisesRegex(NovatelAsciiParseError, "CRC mismatch"):
            parse_range_line(sentence(body, 0), verify_crc=True)


if __name__ == "__main__":
    unittest.main()
