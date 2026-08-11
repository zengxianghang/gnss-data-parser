import io
import unittest

from gnss_parser.novatel.ascii import NovatelAsciiParseError, novatel_crc32
from gnss_parser.novatel.bestvel import iter_bestvel, parse_bestvel_line


def sentence(body: str, crc: int | None = None) -> str:
    if crc is None:
        crc = novatel_crc32(body.encode("ascii"))
    return f"#{body}*{crc:08x}"


class BestvelParserTests(unittest.TestCase):
    def test_parse_official_shape(self) -> None:
        body = (
            "BESTVELA,USB1,0,57.5,FINESTEERING,2209,502223.000,02000020,10a2,16809;"
            "SOL_COMPUTED,PPP,0.250,13.000,0.0025,28.358727,0.0021,0"
        )
        record = parse_bestvel_line(sentence(body), verify_crc=True)
        self.assertEqual(record.week, 2209)
        self.assertEqual(record.vel_type, "PPP")
        self.assertAlmostEqual(record.latency_s, 0.25)
        self.assertAlmostEqual(record.hor_speed_mps, 0.0025)
        self.assertAlmostEqual(record.track_deg, 28.358727)
        self.assertAlmostEqual(record.vert_speed_mps, 0.0021)

    def test_preserves_noncomputed_status(self) -> None:
        body = (
            "BESTVELA,USB1,0,1,FINE,2209,1.0,0,0,1;"
            "INSUFFICIENT_OBS,NONE,0,0,0,0,0,0"
        )
        record = parse_bestvel_line(sentence(body))
        self.assertEqual(record.sol_status, "INSUFFICIENT_OBS")

    def test_tolerant_and_strict(self) -> None:
        bad = sentence("BESTVELA,USB1,0,1,FINE,2209,1.0,0,0,1;SOL_COMPUTED")
        self.assertEqual(list(iter_bestvel(io.StringIO("noise\n" + bad + "\n"))), [])
        with self.assertRaisesRegex(NovatelAsciiParseError, r"line 2:"):
            list(iter_bestvel(io.StringIO("noise\n" + bad + "\n"), strict=True))

    def test_crc_mismatch(self) -> None:
        body = (
            "BESTVELA,USB1,0,1,FINE,2209,1.0,0,0,1;"
            "SOL_COMPUTED,DOPPLER_VELOCITY,0,0,1,2,3,0"
        )
        with self.assertRaisesRegex(NovatelAsciiParseError, "CRC mismatch"):
            parse_bestvel_line(sentence(body, 0), verify_crc=True)


if __name__ == "__main__":
    unittest.main()
