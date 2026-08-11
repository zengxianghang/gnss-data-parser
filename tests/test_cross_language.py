import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from gnss_parser.novatel import (
    read_bestpos,
    read_bestvel,
    read_inspva,
    read_psrvel,
    read_range,
)
from gnss_parser.ublox import read_rmc

FIXTURE_DIR = ROOT / "tests" / "fixtures" / "cross_language"
LOG = FIXTURE_DIR / "sample.log"
EXPECTED = json.loads((FIXTURE_DIR / "expected.json").read_text(encoding="utf-8"))


class CrossLanguageFixtureTests(unittest.TestCase):
    def assert_float(self, actual, expected, places=10):
        self.assertAlmostEqual(actual, expected, places=places)

    def test_psrvel(self):
        r = read_psrvel(LOG, verify_crc=True)[0]
        e = EXPECTED["psrvel"]
        self.assertEqual((r.week, r.sol_status, r.vel_type), (e["week"], e["sol_status"], e["vel_type"]))
        for name in ("sow", "latency_s", "age_s", "hor_speed_mps", "track_deg", "vert_speed_mps"):
            self.assert_float(getattr(r, name), e[name])

    def test_range(self):
        r = read_range(LOG, verify_crc=True)[0]
        e = EXPECTED["range"]
        self.assertEqual(r.week, e["week"])
        self.assertEqual(r.observation_count, e["observation_count"])
        self.assert_float(r.sow, e["sow"])
        o = r.observations[0]
        for name in ("prn", "glofreq"):
            self.assertEqual(getattr(o, name), e[name])
        for name in ("pseudorange_m", "pseudorange_std_m", "adr_cycles", "adr_std_cycles", "doppler_hz", "cn0_dbhz", "lock_time_s"):
            self.assert_float(getattr(o, name), e[name], places=8)
        t = o.tracking
        self.assertEqual(t.raw, e["tracking_raw"])
        self.assertEqual(t.tracking_state, e["tracking_state"])
        self.assertEqual(t.satellite_system_name, e["satellite_system_name"])
        self.assertEqual(t.signal_name, e["signal_name"])
        self.assertEqual(t.phase_locked, e["phase_locked"])
        self.assertEqual(t.parity_known, e["parity_known"])
        self.assertEqual(t.code_locked, e["code_locked"])

    def test_inspva(self):
        r = read_inspva(LOG, verify_crc=True)[0]
        e = EXPECTED["inspva"]
        for name in ("week", "header_week", "ins_status"):
            self.assertEqual(getattr(r, name), e[name])
        for name in ("sow", "header_sow", "latitude_deg", "longitude_deg", "ellipsoidal_height_m", "vel_n_mps", "vel_e_mps", "vel_u_mps", "roll_deg", "pitch_deg", "azimuth_deg"):
            self.assert_float(getattr(r, name), e[name], places=9)

    def test_bestpos(self):
        r = read_bestpos(LOG, verify_crc=True)[0]
        e = EXPECTED["bestpos"]
        for name in ("week", "sol_status", "pos_type", "datum", "station_id", "tracked_sv", "used_sv", "used_l1_sv", "used_multi_sv"):
            self.assertEqual(getattr(r, name), e[name])
        for name in ("sow", "latitude_deg", "longitude_deg", "msl_height_m", "undulation_m", "lat_std_m", "lon_std_m", "hgt_std_m"):
            self.assert_float(getattr(r, name), e[name], places=9)
        self.assertEqual(r.gal_bds_signal_mask, e["gal_bds_signal_mask"])
        self.assertEqual(r.gps_glo_signal_mask, e["gps_glo_signal_mask"])

    def test_bestvel(self):
        r = read_bestvel(LOG, verify_crc=True)[0]
        e = EXPECTED["bestvel"]
        for name in ("week", "sol_status", "vel_type"):
            self.assertEqual(getattr(r, name), e[name])
        for name in ("sow", "latency_s", "age_s", "hor_speed_mps", "track_deg", "vert_speed_mps"):
            self.assert_float(getattr(r, name), e[name])

    def test_rmc(self):
        r = read_rmc(LOG, verify_checksum=True)[0]
        e = EXPECTED["rmc"]
        for name in ("talker_id", "utc_time", "status", "date_ddmmyy", "position_mode", "navigation_status", "checksum"):
            self.assertEqual(getattr(r, name), e[name])
        for name in ("utc_seconds_of_day", "latitude_deg", "longitude_deg", "speed_knots", "course_deg"):
            self.assert_float(getattr(r, name), e[name], places=9)


if __name__ == "__main__":
    unittest.main()
