function record = parseBestposLine(line, verifyCrc)
%PARSEBESTPOSLINE Parse one exact #BESTPOSA standard ASCII line.
if nargin < 2 || isempty(verifyCrc), verifyCrc = false; end
msg = gnssparser.novatel.parseAsciiLine(line, 'BESTPOSA', verifyCrc);
if numel(msg.fields) ~= 21
    error('gnssparser:BestposParseError', ...
        'BESTPOSA requires 21 body fields, got %d.', numel(msg.fields));
end
f = msg.fields;
record = struct();
record.header = msg.header;
record.week = msg.header.week;
record.sow = msg.header.sow;
record.time_status = msg.header.time_status;
record.sol_status = f{1};
record.pos_type = f{2};
record.latitude_deg = number(f{3}, 'latitude');
record.longitude_deg = number(f{4}, 'longitude');
record.msl_height_m = number(f{5}, 'MSL height');
record.undulation_m = number(f{6}, 'undulation');
record.datum = f{7};
record.lat_std_m = number(f{8}, 'latitude std');
record.lon_std_m = number(f{9}, 'longitude std');
record.hgt_std_m = number(f{10}, 'height std');
record.station_id = f{11};
record.diff_age_s = number(f{12}, 'differential age');
record.sol_age_s = number(f{13}, 'solution age');
record.tracked_sv = integer(f{14}, 10, 'tracked SV count');
record.used_sv = integer(f{15}, 10, 'used SV count');
record.used_l1_sv = integer(f{16}, 10, 'used L1 SV count');
record.used_multi_sv = integer(f{17}, 10, 'used multi-frequency SV count');
record.reserved = uint32(integer(f{18}, 16, 'reserved')); 
record.ext_sol_status = uint32(integer(f{19}, 16, 'extended solution status'));
record.gal_bds_signal_mask = uint32(integer(f{20}, 16, 'Galileo/BeiDou signal mask'));
record.gps_glo_signal_mask = uint32(integer(f{21}, 16, 'GPS/GLONASS signal mask'));
record.crc = msg.crc;
end

function value = number(text, label)
value = str2double(text);
if ~isfinite(value)
    error('gnssparser:BestposParseError', 'Invalid %s value: %s.', label, text);
end
end

function value = integer(text, base, label)
if base == 10
    value = str2double(text);
else
    if isempty(text) || any(~isstrprop(text, 'xdigit')), value = NaN; else, value = hex2dec(text); end
end
if ~isfinite(value) || value ~= fix(value)
    error('gnssparser:BestposParseError', 'Invalid %s value: %s.', label, text);
end
end
