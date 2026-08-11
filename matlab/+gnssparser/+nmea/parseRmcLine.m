function record = parseRmcLine(line, verifyChecksum)
%PARSER MCLINE Parse one direct $xxRMC NMEA sentence.
if nargin < 2 || isempty(verifyChecksum), verifyChecksum = false; end
if isstring(line), line = char(line); end
while ~isempty(line) && (line(end) == char(10) || line(end) == char(13)), line(end) = []; end
if ~gnssparser.nmea.peekRmc(line)
    error('gnssparser:NmeaParseError', 'Expected $xxRMC sentence.');
end
star = find(line == '*', 1, 'last');
if isempty(star)
    error('gnssparser:NmeaParseError', 'Missing NMEA checksum delimiter *.');
end
checksumText = line(star + 1:end);
if numel(checksumText) ~= 2 || any(~isstrprop(checksumText, 'xdigit'))
    error('gnssparser:NmeaParseError', 'NMEA checksum must be two hexadecimal digits.');
end
checksumValue = uint8(hex2dec(checksumText));
payload = line(2:star - 1);
if verifyChecksum
    calculated = gnssparser.nmea.checksum(payload);
    if calculated ~= checksumValue
        error('gnssparser:NmeaParseError', ...
            'NMEA checksum mismatch: expected %02X, calculated %02X.', ...
            checksumValue, calculated);
    end
end
fields = gnssparser.common.splitCsv(payload);
if numel(fields) < 10
    error('gnssparser:NmeaParseError', ...
        'RMC requires at least 10 comma fields including message ID, got %d.', numel(fields));
end
if numel(fields) > 14
    error('gnssparser:NmeaParseError', 'RMC has unexpected extra fields: %d total.', numel(fields));
end
while numel(fields) < 14, fields{end + 1} = ''; end %#ok<AGROW>
messageId = fields{1};
if numel(messageId) ~= 5 || ~strcmp(messageId(3:5), 'RMC')
    error('gnssparser:NmeaParseError', 'Invalid RMC message ID: %s.', messageId);
end
talker = messageId(1:2);
if any(~isstrprop(talker, 'alphanum'))
    error('gnssparser:NmeaParseError', 'Invalid RMC talker ID: %s.', talker);
end
status = fields{3};
if ~isempty(status) && ~strcmp(status, 'A') && ~strcmp(status, 'V')
    error('gnssparser:NmeaParseError', 'Invalid RMC status: %s.', status);
end
lat = coordinate(fields{4}, fields{5}, true);
lon = coordinate(fields{6}, fields{7}, false);
mag = optionalNumber(fields{11}, 'magnetic variation');
magEw = fields{12};
if ~isempty(magEw) && ~strcmp(magEw, 'E') && ~strcmp(magEw, 'W')
    error('gnssparser:NmeaParseError', 'Invalid magnetic variation direction: %s.', magEw);
end
if ~isnan(mag) && strcmp(magEw, 'W'), mag = -mag; end
record = struct();
record.talker_id = talker;
record.utc_time = fields{2};
record.utc_seconds_of_day = utcSeconds(fields{2});
record.status = status;
record.latitude_deg = lat;
record.longitude_deg = lon;
record.speed_knots = optionalNumber(fields{8}, 'speed over ground');
record.course_deg = optionalNumber(fields{9}, 'course over ground');
record.date_ddmmyy = fields{10};
record.magnetic_variation_deg = mag;
record.magnetic_variation_ew = magEw;
record.position_mode = fields{13};
record.navigation_status = fields{14};
record.checksum = checksumValue;
end

function value = optionalNumber(text, label)
if isempty(text), value = NaN; return; end
value = str2double(text);
if ~isfinite(value), error('gnssparser:NmeaParseError', 'Invalid %s: %s.', label, text); end
end

function value = utcSeconds(text)
if isempty(text), value = NaN; return; end
if numel(text) < 6, error('gnssparser:NmeaParseError', 'RMC UTC time must be hhmmss[.sss].'); end
h = str2double(text(1:2)); m = str2double(text(3:4)); s = str2double(text(5:end));
if any(~isfinite([h m s])) || h < 0 || h > 23 || m < 0 || m > 59 || s < 0 || s >= 60
    error('gnssparser:NmeaParseError', 'RMC UTC time out of range: %s.', text);
end
value = h * 3600 + m * 60 + s;
end

function result = coordinate(text, hemisphere, isLatitude)
if isempty(text)
    if ~isempty(hemisphere), error('gnssparser:NmeaParseError', 'Hemisphere present while coordinate is empty.'); end
    result = NaN; return;
end
value = str2double(text);
if ~isfinite(value), error('gnssparser:NmeaParseError', 'Invalid NMEA coordinate: %s.', text); end
degrees = floor(value / 100); minutes = value - degrees * 100;
if minutes < 0 || minutes >= 60, error('gnssparser:NmeaParseError', 'Coordinate minutes out of range.'); end
if isLatitude
    if (~strcmp(hemisphere, 'N') && ~strcmp(hemisphere, 'S')) || degrees > 90
        error('gnssparser:NmeaParseError', 'Invalid latitude hemisphere/range.');
    end
    signValue = 1; if strcmp(hemisphere, 'S'), signValue = -1; end
    limit = 90;
else
    if (~strcmp(hemisphere, 'E') && ~strcmp(hemisphere, 'W')) || degrees > 180
        error('gnssparser:NmeaParseError', 'Invalid longitude hemisphere/range.');
    end
    signValue = 1; if strcmp(hemisphere, 'W'), signValue = -1; end
    limit = 180;
end
result = signValue * (degrees + minutes / 60);
if abs(result) > limit, error('gnssparser:NmeaParseError', 'Coordinate out of range.'); end
end
