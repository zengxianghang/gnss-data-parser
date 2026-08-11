function testRmc()
%TESTRMC Regression checks for MATLAB u-blox/NMEA RMC support.

known = 'GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W';
assert(gnssparser.nmea.checksum(known) == uint8(hex2dec('6A')));

sample = '$GPRMC,083559.00,A,4717.11437,N,00833.91522,E,0.004,77.52,091202,,,A,V*2D';
r = gnssparser.nmea.parseRmcLine(sample, true);
assert(strcmp(r.talker_id, 'GP'));
assert(strcmp(r.status, 'A'));
assert(abs(r.utc_seconds_of_day - (8 * 3600 + 35 * 60 + 59)) < 1e-12);
assert(abs(r.latitude_deg - (47 + 17.11437 / 60)) < 1e-12);
assert(abs(r.longitude_deg - (8 + 33.91522 / 60)) < 1e-12);
assert(abs(r.speed_knots - 0.004) < 1e-12);
assert(strcmp(r.date_ddmmyy, '091202'));
assert(strcmp(r.position_mode, 'A'));
assert(strcmp(r.navigation_status, 'V'));

payload = 'GNRMC,120000.00,V,,,,,,,110826,,,,N';
sentence = sprintf('$%s*%02X', payload, gnssparser.nmea.checksum(payload));
r2 = gnssparser.nmea.parseRmcLine(sentence, true);
assert(strcmp(r2.talker_id, 'GN') && strcmp(r2.status, 'V'));
assert(isnan(r2.latitude_deg) && isnan(r2.longitude_deg) && isnan(r2.speed_knots));

fprintf('testRmc: PASS\n');
end
