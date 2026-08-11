import io
import unittest

from gnss_parser.novatel.ascii import NovatelAsciiParseError, novatel_crc32
from gnss_parser.novatel.bestpos import iter_bestpos, parse_bestpos_line


def sentence(body: str, crc: int | None = None) -> str:
    if crc is None:
        crc = novatel_crc32(body.encode("ascii"))
    return f"#{body}*{crc:08x}"


class BestposParserTests(unittest.TestCase):
    def test_parse_official_shape(self) -> None:
        body = (
            'BESTPOSA,USB1,0,58.5,FINESTEERING,2209,502061.000,02000020,cdba,16809;'
            'SOL_COMPUTED,PPP,51.15043706870,-114.03067882331,1097.3462,-17.0001,WGS84,'
            '0.0154,0.0139,0.0288,"TSTR",11.000,0.000,43,39,39,38,00,00,7f,37'
        )
        record = parse_bestpos_line(sentence(body), verify_crc=True)
        self.assertEqual(record.sol_status, "SOL_COMPUTED")
        self.assertEqual(record.pos_type, "PPP")
        self.assertAlmostEqual(record.msl_height_m, 1097.3462)
        self.assertAlmostEqual(record.undulation_m, -17.0001)
        self.assertEqual(record.station_id, "TSTR")
        self.assertEqual(record.tracked_sv, 43)
        self.assertEqual(record.used_sv, 39)
        self.assertEqual(record.gal_bds_signal_mask, 0x7F)
        self.assertEqual(record.gps_glo_signal_mask, 0x37)

    def test_preserves_noncomputed_solution(self) -> None:
        body = (
            'BESTPOSA,USB1,0,1,FINE,2209,1.0,0,0,1;INSUFFICIENT_OBS,NONE,1,2,3,4,WGS84,'
            '5,6,7,"",0,0,8,0,0,0,00,00,00,00'
        )
        record = parse_bestpos_line(sentence(body))
        self.assertEqual(record.sol_status, "INSUFFICIENT_OBS")
        self.assertEqual(record.used_sv, 0)

    def test_field_count_and_strict_mode(self) -> None:
        bad = sentence("BESTPOSA,USB1,0,1,FINE,2209,1.0,0,0,1;SOL_COMPUTED,PPP")
        with self.assertRaises(NovatelAsciiParseError):
            parse_bestpos_line(bad)
        with self.assertRaisesRegex(NovatelAsciiParseError, r"line 2:"):
            list(iter_bestpos(io.StringIO("noise\n" + bad + "\n"), strict=True))
        self.assertEqual(list(iter_bestpos(io.StringIO("noise\n" + bad + "\n"))), [])

    def test_crc_mismatch(self) -> None:
        body = (
            'BESTPOSA,USB1,0,1,FINE,2209,1.0,0,0,1;SOL_COMPUTED,SINGLE,1,2,3,4,WGS84,'
            '5,6,7,"ABCD",0,0,8,7,6,5,00,00,00,00'
        )
        with self.assertRaisesRegex(NovatelAsciiParseError, "CRC mismatch"):
            parse_bestpos_line(sentence(body, 0), verify_crc=True)


if __name__ == "__main__":
    unittest.main()
