function key = identifyGnssLine(line)
%IDENTIFYGNSSLINE Return stable key for a supported GNSS text line.
%   Returns '' for unsupported or unrelated lines. No body parsing is done.

if isstring(line), line = char(line); end
key = '';
if isempty(line)
    return;
end
if line(1) == '#'
    name = gnssparser.novatel.peekMessageName(line);
    switch name
        case 'PSRVELA'
            key = 'psrvel';
        case 'RANGEA'
            key = 'range';
        case 'INSPVAA'
            key = 'inspva';
        case 'BESTPOSA'
            key = 'bestpos';
        case 'BESTVELA'
            key = 'bestvel';
    end
elseif gnssparser.nmea.peekRmc(line)
    key = 'rmc';
end
end
