function testCrossLanguageConsistency()
%TESTCROSSLANGUAGECONSISTENCY Validate MATLAB readers against shared manifest.
% Requires jsondecode (MATLAB R2016b+). Parser functions themselves do not
% depend on jsondecode; this requirement applies only to this regression test.

here = fileparts(mfilename('fullpath'));
root = fileparts(fileparts(here));
fixtureDir = fullfile(root, 'tests', 'fixtures', 'cross_language');
logFile = fullfile(fixtureDir, 'sample.log');
expected = jsondecode(fileread(fullfile(fixtureDir, 'expected.json')));

p = readNovatelPsrvel(logFile, 'VerifyCrc', true); p = p(1); e = expected.psrvel;
assert(p.week == e.week && strcmp(p.sol_status, e.sol_status) && strcmp(p.vel_type, e.vel_type));
closeEnough(p.sow, e.sow); closeEnough(p.latency_s, e.latency_s); closeEnough(p.age_s, e.age_s);
closeEnough(p.hor_speed_mps, e.hor_speed_mps); closeEnough(p.track_deg, e.track_deg); closeEnough(p.vert_speed_mps, e.vert_speed_mps);

rr = readNovatelRange(logFile, 'VerifyCrc', true); rr = rr(1); e = expected.range;
assert(rr.week == e.week && rr.observation_count == e.observation_count); closeEnough(rr.sow, e.sow);
o = rr.observations(1);
assert(o.prn == e.prn && o.glofreq == e.glofreq);
closeEnough(o.pseudorange_m, e.pseudorange_m); closeEnough(o.pseudorange_std_m, e.pseudorange_std_m);
closeEnough(o.adr_cycles, e.adr_cycles); closeEnough(o.adr_std_cycles, e.adr_std_cycles);
closeEnough(o.doppler_hz, e.doppler_hz); closeEnough(o.cn0_dbhz, e.cn0_dbhz); closeEnough(o.lock_time_s, e.lock_time_s);
assert(double(o.tracking.raw) == e.tracking_raw);
assert(o.tracking.tracking_state == e.tracking_state);
assert(strcmp(o.tracking.satellite_system_name, e.satellite_system_name));
assert(strcmp(o.tracking.signal_name, e.signal_name));
assert(o.tracking.phase_locked == e.phase_locked && o.tracking.parity_known == e.parity_known && o.tracking.code_locked == e.code_locked);

i = readNovatelInspva(logFile, 'VerifyCrc', true); i = i(1); e = expected.inspva;
assert(i.week == e.week && i.header_week == e.header_week && strcmp(i.ins_status, e.ins_status));
closeEnough(i.sow, e.sow); closeEnough(i.header_sow, e.header_sow);
closeEnough(i.latitude_deg, e.latitude_deg); closeEnough(i.longitude_deg, e.longitude_deg); closeEnough(i.ellipsoidal_height_m, e.ellipsoidal_height_m);
closeEnough(i.vel_n_mps, e.vel_n_mps); closeEnough(i.vel_e_mps, e.vel_e_mps); closeEnough(i.vel_u_mps, e.vel_u_mps);
closeEnough(i.roll_deg, e.roll_deg); closeEnough(i.pitch_deg, e.pitch_deg); closeEnough(i.azimuth_deg, e.azimuth_deg);

bp = readNovatelBestpos(logFile, 'VerifyCrc', true); bp = bp(1); e = expected.bestpos;
assert(bp.week == e.week && strcmp(bp.sol_status, e.sol_status) && strcmp(bp.pos_type, e.pos_type));
assert(strcmp(bp.datum, e.datum) && strcmp(bp.station_id, e.station_id));
assert(bp.tracked_sv == e.tracked_sv && bp.used_sv == e.used_sv && bp.used_l1_sv == e.used_l1_sv && bp.used_multi_sv == e.used_multi_sv);
closeEnough(bp.sow, e.sow); closeEnough(bp.latitude_deg, e.latitude_deg); closeEnough(bp.longitude_deg, e.longitude_deg);
closeEnough(bp.msl_height_m, e.msl_height_m); closeEnough(bp.undulation_m, e.undulation_m);
closeEnough(bp.lat_std_m, e.lat_std_m); closeEnough(bp.lon_std_m, e.lon_std_m); closeEnough(bp.hgt_std_m, e.hgt_std_m);
assert(double(bp.gal_bds_signal_mask) == e.gal_bds_signal_mask && double(bp.gps_glo_signal_mask) == e.gps_glo_signal_mask);

bv = readNovatelBestvel(logFile, 'VerifyCrc', true); bv = bv(1); e = expected.bestvel;
assert(bv.week == e.week && strcmp(bv.sol_status, e.sol_status) && strcmp(bv.vel_type, e.vel_type));
closeEnough(bv.sow, e.sow); closeEnough(bv.latency_s, e.latency_s); closeEnough(bv.age_s, e.age_s);
closeEnough(bv.hor_speed_mps, e.hor_speed_mps); closeEnough(bv.track_deg, e.track_deg); closeEnough(bv.vert_speed_mps, e.vert_speed_mps);

r = readUbloxRmc(logFile, 'VerifyChecksum', true); r = r(1); e = expected.rmc;
assert(strcmp(r.talker_id, e.talker_id) && strcmp(r.utc_time, e.utc_time) && strcmp(r.status, e.status));
assert(strcmp(r.date_ddmmyy, e.date_ddmmyy) && strcmp(r.position_mode, e.position_mode) && strcmp(r.navigation_status, e.navigation_status));
assert(double(r.checksum) == e.checksum);
closeEnough(r.utc_seconds_of_day, e.utc_seconds_of_day); closeEnough(r.latitude_deg, e.latitude_deg);
closeEnough(r.longitude_deg, e.longitude_deg); closeEnough(r.speed_knots, e.speed_knots); closeEnough(r.course_deg, e.course_deg);

fprintf('testCrossLanguageConsistency: PASS\n');
end

function closeEnough(actual, expected)
tol = 1e-9 * max(1, abs(expected));
assert(abs(actual - expected) <= tol, 'Value mismatch: actual %.15g expected %.15g', actual, expected);
end
