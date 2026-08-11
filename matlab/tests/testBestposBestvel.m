function testBestposBestvel()
%TESTBESTPOSBESTVEL Regression checks for MATLAB BESTPOS/BESTVEL support.

bestpos = ['#BESTPOSA,USB1,0,58.5,FINESTEERING,2209,502061.000,' ...
    '02000020,cdba,16809;SOL_COMPUTED,PPP,51.15043706870,' ...
    '-114.03067882331,1097.3462,-17.0001,WGS84,0.0154,0.0139,' ...
    '0.0288,"TSTR",11.000,0.000,43,39,39,38,00,00,7f,37*52483ac5'];
p = gnssparser.novatel.parseBestposLine(bestpos, true);
assert(strcmp(p.sol_status, 'SOL_COMPUTED'));
assert(strcmp(p.pos_type, 'PPP'));
assert(abs(p.msl_height_m - 1097.3462) < 1e-12);
assert(abs(p.undulation_m + 17.0001) < 1e-12);
assert(strcmp(p.station_id, 'TSTR'));
assert(p.tracked_sv == 43 && p.used_sv == 39);
assert(p.gal_bds_signal_mask == uint32(hex2dec('7F')));
assert(p.gps_glo_signal_mask == uint32(hex2dec('37')));

bestvel = ['#BESTVELA,USB1,0,57.5,FINESTEERING,2209,502223.000,' ...
    '02000020,10a2,16809;SOL_COMPUTED,PPP,0.250,13.000,0.0025,' ...
    '28.358727,0.0021,0*e9418656'];
v = gnssparser.novatel.parseBestvelLine(bestvel, true);
assert(v.week == 2209);
assert(strcmp(v.vel_type, 'PPP'));
assert(abs(v.latency_s - 0.25) < 1e-12);
assert(abs(v.hor_speed_mps - 0.0025) < 1e-12);
assert(abs(v.vert_speed_mps - 0.0021) < 1e-12);

fprintf('testBestposBestvel: PASS\n');
end
