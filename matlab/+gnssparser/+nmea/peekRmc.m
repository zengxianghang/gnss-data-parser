function tf = peekRmc(line)
%PEEKRMC Cheaply identify a direct $xxRMC NMEA sentence.
if isstring(line), line = char(line); end
tf = ischar(line) && numel(line) >= 6 && line(1) == '$' && strcmp(line(4:6), 'RMC');
end
