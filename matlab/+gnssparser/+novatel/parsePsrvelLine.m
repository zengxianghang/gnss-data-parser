function record = parsePsrvelLine(line, verifyCrc)
%PARSEPSRVELLINE Parse one exact #PSRVELA standard ASCII line.
if nargin < 2 || isempty(verifyCrc), verifyCrc = false; end
msg = gnssparser.novatel.parseAsciiLine(line, 'PSRVELA', verifyCrc);
if numel(msg.fields) ~= 8
    error('gnssparser:PsrvelParseError', ...
        'PSRVELA requires 8 body fields, got %d.', numel(msg.fields));
end
f = msg.fields;
record = struct();
record.header = msg.header;
record.week = msg.header.week;
record.sow = msg.header.sow;
record.time_status = msg.header.time_status;
record.sol_status = f{1};
record.vel_type = f{2};
record.latency_s = number(f{3}, 'latency');
record.age_s = number(f{4}, 'differential age');
record.hor_speed_mps = number(f{5}, 'horizontal speed');
record.track_deg = number(f{6}, 'track angle');
record.vert_speed_mps = number(f{7}, 'vertical speed');
record.reserved = number(f{8}, 'reserved');
record.crc = msg.crc;
end

function value = number(text, label)
value = str2double(text);
if ~isfinite(value)
    error('gnssparser:PsrvelParseError', 'Invalid %s value: %s.', label, text);
end
end
