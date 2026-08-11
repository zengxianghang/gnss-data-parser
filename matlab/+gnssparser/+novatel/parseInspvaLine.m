function record = parseInspvaLine(line, verifyCrc)
%PARSEINSPVALINE Parse one exact #INSPVAA standard ASCII line.
if nargin < 2 || isempty(verifyCrc), verifyCrc = false; end
msg = gnssparser.novatel.parseAsciiLine(line, 'INSPVAA', verifyCrc);
if numel(msg.fields) ~= 12
    error('gnssparser:InspvaParseError', ...
        'INSPVAA requires 12 body fields, got %d.', numel(msg.fields));
end
f = msg.fields;
record = struct();
record.header = msg.header;
record.week = integer(f{1}, 'data-block GPS week');
record.sow = number(f{2}, 'data-block GPS seconds of week');
record.header_week = msg.header.week;
record.header_sow = msg.header.sow;
record.time_status = msg.header.time_status;
record.latitude_deg = number(f{3}, 'latitude');
record.longitude_deg = number(f{4}, 'longitude');
record.ellipsoidal_height_m = number(f{5}, 'ellipsoidal height');
record.vel_n_mps = number(f{6}, 'north velocity');
record.vel_e_mps = number(f{7}, 'east velocity');
record.vel_u_mps = number(f{8}, 'up velocity');
record.roll_deg = number(f{9}, 'roll');
record.pitch_deg = number(f{10}, 'pitch');
record.azimuth_deg = number(f{11}, 'azimuth');
record.ins_status = f{12};
record.crc = msg.crc;
end

function value = number(text, label)
value = str2double(text);
if ~isfinite(value)
    error('gnssparser:InspvaParseError', 'Invalid %s value: %s.', label, text);
end
end

function value = integer(text, label)
value = str2double(text);
if ~isfinite(value) || value ~= fix(value)
    error('gnssparser:InspvaParseError', 'Invalid %s value: %s.', label, text);
end
end
