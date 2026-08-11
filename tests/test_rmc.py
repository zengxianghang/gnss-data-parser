import io
import unittest

from gnss_parser.ublox.rmc import NmeaParseError, iter_rmc, nmea_checksum, parse_rmc_line


def sentence(payload: str, checksum: int | None = None) -> str:
    if checksum is None:
        checksum = nmea_checksum(payload)
    return f"${payload}*{checksum:02X}"


class RmcParserTests(unittest.TestCase):
    def test_known_nmea_checksum(self) -> None:
        payload = "GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W"
        self.assertEqual(nmea_checksum(payload), 0x6A)

    def test_parse_ublox_field_shape(self) -> None:
        payload = "GPRMC,083559.00,A,4717.11437,N,00833.91522,E,0.004,77.52,091202,,,A,V"
        self.assertEqual(nmea_checksum(payload), 0x2D)
        record = parse_rmc_line(sentence(payload), verify_checksum=True)
        self.assertEqual(record.talker_id, "GP")
        self.assertEqual(record.status, "A")
        self.assertAlmostEqual(record.utc_seconds_of_day, 8 * 3600 + 35 * 60 + 59.0)
        self.assertAlmostEqual(record.latitude_deg, 47 + 17.11437 / 60.0)
        self.assertAlmostEqual(record.longitude_deg, 8 + 33.91522 / 60.0)
        self.assertAlmostEqual(record.speed_knots, 0.004)
        self.assertEqual(record.date_ddmmyy, "091202")
        self.assertEqual(record.position_mode, "A")
        self.assertEqual(record.navigation_status, "V")

    def test_accepts_gn_talker_and_invalid_empty_fix(self) -> None:
        payload = "GNRMC,120000.00,V,,,,,,,110826,,,,N"
        record = parse_rmc_line(sentence(payload), verify_checksum=True)
        self.assertEqual(record.talker_id, "GN")
        self.assertEqual(record.status, "V")
        self.assertIsNone(record.latitude_deg)
        self.assertIsNone(record.longitude_deg)
        self.assertIsNone(record.speed_knots)

    def test_legacy_sentence_without_trailing_optional_fields(self) -> None:
        payload = "GPRMC,120000.00,A,3500.0000,N,13900.0000,E,1.0,2.0,110826"
        record = parse_rmc_line(sentence(payload))
        self.assertEqual(record.position_mode, "")
        self.assertEqual(record.navigation_status, "")

    def test_south_west_coordinates_are_negative(self) -> None:
        payload = "GPRMC,120000.00,A,3500.0000,S,13900.0000,W,1.0,2.0,110826,,,,"
        record = parse_rmc_line(sentence(payload))
        self.assertAlmostEqual(record.latitude_deg, -35.0)
        self.assertAlmostEqual(record.longitude_deg, -139.0)

    def test_tolerant_and_strict(self) -> None:
        bad = "$GPRMC,broken*00"
        self.assertEqual(list(iter_rmc(io.StringIO("noise\n" + bad + "\n"))), [])
        with self.assertRaisesRegex(NmeaParseError, r"line 2:"):
            list(iter_rmc(io.StringIO("noise\n" + bad + "\n"), strict=True))

    def test_checksum_mismatch(self) -> None:
        payload = "GPRMC,120000.00,V,,,,,,,110826,,,,N"
        with self.assertRaisesRegex(NmeaParseError, "checksum mismatch"):
            parse_rmc_line(sentence(payload, 0), verify_checksum=True)


if __name__ == "__main__":
    unittest.main()
