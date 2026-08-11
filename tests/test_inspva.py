import io
import unittest

from gnss_parser.novatel.ascii import NovatelAsciiParseError, novatel_crc32
from gnss_parser.novatel.inspva import iter_inspva, parse_inspva_line


def sentence(body: str, crc: int | None = None) -> str:
    if crc is None:
        crc = novatel_crc32(body.encode("ascii"))
    return f"#{body}*{crc:08x}"


class InspvaParserTests(unittest.TestCase):
    def test_parse_official_shape(self) -> None:
        body = (
            "INSPVAA,USB1,0,67.5,FINESTEERING,2209,490558.000,02000020,18bc,16809;"
            "2209,490558.000000000,51.15043714042,-114.03067871718,1080.3548,"
            "0.0051,-0.0014,-0.0012,-0.296402993,0.311887972,157.992156267,INS_SOLUTION_GOOD"
        )
        record = parse_inspva_line(sentence(body), verify_crc=True)
        self.assertEqual(record.week, 2209)
        self.assertAlmostEqual(record.sow, 490558.0)
        self.assertEqual(record.header_week, 2209)
        self.assertAlmostEqual(record.vel_n_mps, 0.0051)
        self.assertAlmostEqual(record.vel_u_mps, -0.0012)
        self.assertEqual(record.ins_status, "INS_SOLUTION_GOOD")

    def test_preserves_distinct_header_and_data_times(self) -> None:
        body = (
            "INSPVAA,USB1,0,67.5,FINESTEERING,2209,490558.100,02000020,18bc,16809;"
            "2209,490558.000000000,1,2,3,4,5,6,7,8,9,INS_SOLUTION_GOOD"
        )
        record = parse_inspva_line(sentence(body))
        self.assertAlmostEqual(record.header_sow, 490558.1)
        self.assertAlmostEqual(record.sow, 490558.0)

    def test_wrong_field_count(self) -> None:
        body = "INSPVAA,USB1,0,1,FINE,2209,1.0,0,0,1;2209,1,2"
        with self.assertRaises(NovatelAsciiParseError):
            parse_inspva_line(sentence(body))

    def test_iterator_tolerant_and_strict(self) -> None:
        good = (
            "INSPVAA,USB1,0,1,FINE,2209,1.0,0,0,1;"
            "2209,1.0,1,2,3,4,5,6,7,8,9,INS_SOLUTION_GOOD"
        )
        text = "noise\n#INSPVAA,bad*00000000\n" + sentence(good) + "\n"
        self.assertEqual(len(list(iter_inspva(io.StringIO(text)))), 1)
        with self.assertRaisesRegex(NovatelAsciiParseError, r"line 2:"):
            list(iter_inspva(io.StringIO(text), strict=True))

    def test_crc_mismatch(self) -> None:
        body = (
            "INSPVAA,USB1,0,1,FINE,2209,1.0,0,0,1;"
            "2209,1.0,1,2,3,4,5,6,7,8,9,INS_SOLUTION_GOOD"
        )
        with self.assertRaisesRegex(NovatelAsciiParseError, "CRC mismatch"):
            parse_inspva_line(sentence(body, 0), verify_crc=True)


if __name__ == "__main__":
    unittest.main()
