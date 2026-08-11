function testRange()
%TESTRANGE Regression checks for MATLAB RANGE support.

sample = ['#RANGEA,USB1,0,54.0,FINESTEERING,2209,512449.000,' ...
    '02000020,5103,16809;1,26,0,24101771.233,0.199,' ...
    '-126655684.482618,0.012,2806.247,44.4,853.017,1810dc04*7c0c0139'];
r = gnssparser.novatel.parseRangeLine(sample, true);
assert(r.week == 2209);
assert(r.observation_count == 1);
obs = r.observations(1);
assert(obs.prn == 26);
assert(abs(obs.cn0_dbhz - 44.4) < 1e-12);
assert(abs(obs.doppler_hz - 2806.247) < 1e-12);
assert(obs.tracking.raw == uint32(hex2dec('1810DC04')));
assert(obs.tracking.tracking_state == 4);
assert(obs.tracking.phase_locked && obs.tracking.parity_known && obs.tracking.code_locked);
assert(strcmp(obs.tracking.satellite_system_name, 'GPS'));
assert(strcmp(obs.tracking.signal_name, 'L1CA'));
assert(obs.tracking.primary_l1 && obs.tracking.half_cycle_added);

value = bitor(bitshift(uint32(4), 16), bitshift(uint32(9), 21));
value = bitor(value, bitshift(uint32(1), 10));
value = bitor(value, bitshift(uint32(1), 12));
s = gnssparser.novatel.decodeTrackingStatus(value);
assert(strcmp(s.satellite_system_name, 'BEIDOU'));
assert(strcmp(s.signal_name, 'B2AP'));
assert(s.phase_locked && s.code_locked && ~s.parity_known);

fprintf('testRange: PASS\n');
end
