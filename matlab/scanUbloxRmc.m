function stats = scanUbloxRmc(filename, callback, varargin)
%SCANUBLOXRMC Stream $xxRMC sentences from a mixed text log.
%   Options: 'Strict' (false), 'VerifyChecksum' (false).
if nargin < 2, callback = []; end
opts = struct('Strict', false, 'VerifyChecksum', false);
if mod(numel(varargin), 2) ~= 0, error('gnssparser:InvalidOptions', 'Options must be name/value pairs.'); end
for k = 1:2:numel(varargin)
    name = varargin{k}; if isstring(name), name = char(name); end
    if ~ischar(name) || ~isfield(opts, name), error('gnssparser:InvalidOptions', 'Unknown option.'); end
    opts.(name) = logical(varargin{k + 1});
end
if isstring(filename), filename = char(filename); end
fid = fopen(filename, 'r');
if fid < 0, error('gnssparser:FileOpenError', 'Cannot open file: %s', filename); end
cleanup = onCleanup(@() fclose(fid)); %#ok<NASGU>
stats = struct('total_lines', 0, 'target_lines', 0, 'records', 0, 'malformed', 0);
while true
    line = fgetl(fid); if ~ischar(line), break; end
    stats.total_lines = stats.total_lines + 1;
    if ~gnssparser.nmea.peekRmc(line), continue; end
    stats.target_lines = stats.target_lines + 1;
    try
        record = gnssparser.nmea.parseRmcLine(line, opts.VerifyChecksum);
        stats.records = stats.records + 1;
        if ~isempty(callback), callback(record); end
    catch err
        stats.malformed = stats.malformed + 1;
        if opts.Strict
            error('gnssparser:RmcTargetParseError', 'Line %d: %s', stats.total_lines, err.message);
        end
    end
end
end
