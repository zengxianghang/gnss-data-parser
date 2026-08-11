function crc = crc32(data)
%CRC32 Calculate the NovAtel OEM CRC32 value.
%   CRC = gnssparser.novatel.crc32(DATA) accepts a character vector, string,
%   or uint8 byte vector. The implementation matches the OEM7 algorithm used
%   by the Python parser.

if isstring(data)
    data = char(data);
end
if ischar(data)
    if any(double(data) > 127)
        error('gnssparser:NonAsciiCrcInput', ...
            'CRC verification requires ASCII message bytes.');
    end
    bytes = uint8(data);
elseif isa(data, 'uint8')
    bytes = data;
else
    error('gnssparser:InvalidInput', 'CRC input must be char, string or uint8.');
end

crc = uint32(0);
poly = uint32(hex2dec('EDB88320'));
mask24 = uint32(hex2dec('00FFFFFF'));
for k = 1:numel(bytes)
    value = bitand(bitxor(crc, uint32(bytes(k))), uint32(255));
    for j = 1:8
        if bitand(value, uint32(1)) ~= 0
            value = bitxor(bitshift(value, -1), poly);
        else
            value = bitshift(value, -1);
        end
    end
    crc = bitxor(bitand(bitshift(crc, -8), mask24), value);
end
end
