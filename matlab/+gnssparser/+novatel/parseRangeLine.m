function record = parseRangeLine(line, verifyCrc)
%PARSERANGELINE Parse one exact #RANGEA standard ASCII line.
if nargin < 2 || isempty(verifyCrc), verifyCrc = false; end
msg = gnssparser.novatel.parseAsciiLine(line, 'RANGEA', verifyCrc);
if isempty(msg.fields)
    error('gnssparser:RangeParseError', 'RANGEA body is empty.');
end
count = integer(msg.fields{1}, 10, 'observation count');
if count < 0
    error('gnssparser:RangeParseError', 'Observation count cannot be negative.');
end
fieldsPerObs = 10;
expected = 1 + count * fieldsPerObs;
if numel(msg.fields) ~= expected
    error('gnssparser:RangeParseError', ...
        'RANGEA declares %d observations but has %d observation fields; expected %d.', ...
        count, numel(msg.fields) - 1, count * fieldsPerObs);
end

observations = struct([]);
for k = 1:count
    base = 2 + (k - 1) * fieldsPerObs;
    f = msg.fields(base:base + fieldsPerObs - 1);
    obs = struct();
    obs.prn = integer(f{1}, 10, 'PRN');
    obs.glofreq = integer(f{2}, 10, 'GLONASS frequency');
    obs.pseudorange_m = number(f{3}, 'pseudorange');
    obs.pseudorange_std_m = number(f{4}, 'pseudorange std');
    obs.adr_cycles = number(f{5}, 'ADR');
    obs.adr_std_cycles = number(f{6}, 'ADR std');
    obs.doppler_hz = number(f{7}, 'Doppler');
    obs.cn0_dbhz = number(f{8}, 'C/N0');
    obs.lock_time_s = number(f{9}, 'lock time');
    raw = uint32(integer(f{10}, 16, 'tracking status'));
    obs.tracking = gnssparser.novatel.decodeTrackingStatus(raw);
    if isempty(observations)
        observations = obs;
    else
        observations(end + 1) = obs; %#ok<AGROW>
    end
end

record = struct();
record.header = msg.header;
record.week = msg.header.week;
record.sow = msg.header.sow;
record.time_status = msg.header.time_status;
record.observation_count = count;
record.observations = observations;
record.crc = msg.crc;
end

function value = number(text, label)
value = str2double(text);
if ~isfinite(value)
    error('gnssparser:RangeParseError', 'Invalid %s value: %s.', label, text);
end
end

function value = integer(text, base, label)
if base == 10
    value = str2double(text);
else
    if isempty(text) || any(~isstrprop(text, 'xdigit'))
        value = NaN;
    else
        value = hex2dec(text);
    end
end
if ~isfinite(value) || value ~= fix(value)
    error('gnssparser:RangeParseError', 'Invalid %s value: %s.', label, text);
end
end
