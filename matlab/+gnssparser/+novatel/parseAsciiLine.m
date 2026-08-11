function msg = parseAsciiLine(line, expectedMessage, verifyCrc)
%PARSEASCIILINE Parse one standard NovAtel OEM #...A ASCII message.
%   MSG = gnssparser.novatel.parseAsciiLine(LINE)
%   MSG = ...(..., EXPECTEDMESSAGE, VERIFYCRC)
%
%   The returned struct contains HEADER, FIELDS and CRC. EXPECTEDMESSAGE is
%   matched exactly. VERIFYCRC defaults to false for large-log performance.

if nargin < 2 || isempty(expectedMessage)
    expectedMessage = '';
end
if nargin < 3 || isempty(verifyCrc)
    verifyCrc = false;
end
if isstring(line), line = char(line); end
if isstring(expectedMessage), expectedMessage = char(expectedMessage); end
if ~ischar(line) || isempty(line) || line(1) ~= '#'
    error('gnssparser:NovatelAsciiParseError', ...
        'Standard ASCII message must start with #.');
end

while ~isempty(line) && (line(end) == char(10) || line(end) == char(13))
    line(end) = [];
end
star = find(line == '*', 1, 'last');
if isempty(star)
    error('gnssparser:NovatelAsciiParseError', 'Missing CRC delimiter *.');
end
crcText = line(star + 1:end);
if numel(crcText) ~= 8 || any(~isstrprop(crcText, 'xdigit'))
    error('gnssparser:NovatelAsciiParseError', ...
        'CRC must contain exactly 8 hexadecimal digits.');
end
crc = uint32(hex2dec(crcText));

content = line(2:star - 1);
semicolon = find(content == ';', 1, 'first');
if isempty(semicolon)
    error('gnssparser:NovatelAsciiParseError', ...
        'Missing header/data delimiter ;.');
end
headerFields = gnssparser.common.splitCsv(content(1:semicolon - 1));
if numel(headerFields) ~= 10
    error('gnssparser:NovatelAsciiParseError', ...
        'Standard ASCII header requires 10 fields, got %d.', numel(headerFields));
end

header = struct();
header.message = headerFields{1};
header.port = headerFields{2};
header.sequence = parseInteger(headerFields{3}, 10, 'sequence');
header.idle_time_pct = parseNumber(headerFields{4}, 'idle time');
header.time_status = headerFields{5};
header.week = parseInteger(headerFields{6}, 10, 'GPS week');
header.sow = parseNumber(headerFields{7}, 'GPS seconds of week');
header.receiver_status = uint32(parseInteger(headerFields{8}, 16, 'receiver status'));
header.reserved = uint32(parseInteger(headerFields{9}, 16, 'reserved header field'));
header.software_version = parseInteger(headerFields{10}, 10, 'software version');

if ~isempty(expectedMessage) && ~strcmp(header.message, expectedMessage)
    error('gnssparser:NovatelAsciiParseError', ...
        'Expected message %s, got %s.', expectedMessage, header.message);
end

if semicolon < numel(content)
    fields = gnssparser.common.splitCsv(content(semicolon + 1:end));
else
    fields = {''};
end

if verifyCrc
    calculated = gnssparser.novatel.crc32(content);
    if calculated ~= crc
        error('gnssparser:NovatelAsciiParseError', ...
            'CRC mismatch: expected %08X, calculated %08X.', crc, calculated);
    end
end

msg = struct('header', header, 'fields', {fields}, 'crc', crc);
end

function value = parseNumber(text, label)
value = str2double(text);
if ~isfinite(value)
    error('gnssparser:NovatelAsciiParseError', 'Invalid %s value: %s.', label, text);
end
end

function value = parseInteger(text, base, label)
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
    error('gnssparser:NovatelAsciiParseError', 'Invalid %s value: %s.', label, text);
end
end
