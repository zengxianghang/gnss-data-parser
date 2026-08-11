function value = checksum(payload)
%CHECKSUM Return the NMEA XOR checksum for text between $ and *.
if isstring(payload), payload = char(payload); end
if ~ischar(payload)
    error('gnssparser:InvalidInput', 'NMEA payload must be char or string.');
end
value = uint8(0);
for k = 1:numel(payload)
    if double(payload(k)) > 127
        error('gnssparser:NmeaParseError', 'NMEA checksum requires ASCII text.');
    end
    value = bitxor(value, uint8(payload(k)));
end
end
