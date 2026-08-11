function stats = scanTargetLines(filename, targetMessage, parserFcn, callback, varargin)
%SCANTARGETLINES Stream a mixed ASCII log and process one exact message type.
%   STATS = gnssparser.common.scanTargetLines(FILE, TARGET, PARSER, CALLBACK)
%   scans line by line and does not load the file into memory.
%
%   PARSER is called as PARSER(line, verifyCrc). CALLBACK is called once for
%   each successfully parsed record. Name/value options:
%     'Strict'    - false (default): skip malformed target records
%     'VerifyCrc' - false (default): opt-in CRC/checksum work

opts = struct('Strict', false, 'VerifyCrc', false);
if mod(numel(varargin), 2) ~= 0
    error('gnssparser:InvalidOptions', 'Options must be name/value pairs.');
end
for k = 1:2:numel(varargin)
    name = varargin{k};
    if isstring(name), name = char(name); end
    if ~ischar(name) || ~isfield(opts, name)
        error('gnssparser:InvalidOptions', 'Unknown option.');
    end
    opts.(name) = logical(varargin{k + 1});
end

if isstring(filename), filename = char(filename); end
if isstring(targetMessage), targetMessage = char(targetMessage); end
fid = fopen(filename, 'r');
if fid < 0
    error('gnssparser:FileOpenError', 'Cannot open file: %s', filename);
end
cleanup = onCleanup(@() fclose(fid)); %#ok<NASGU>

stats = struct('total_lines', 0, 'target_lines', 0, ...
    'records', 0, 'malformed', 0);
while true
    line = fgetl(fid);
    if ~ischar(line)
        break;
    end
    stats.total_lines = stats.total_lines + 1;
    if ~strcmp(gnssparser.novatel.peekMessageName(line), targetMessage)
        continue;
    end
    stats.target_lines = stats.target_lines + 1;
    try
        record = parserFcn(line, opts.VerifyCrc);
        stats.records = stats.records + 1;
        if ~isempty(callback)
            callback(record);
        end
    catch err
        stats.malformed = stats.malformed + 1;
        if opts.Strict
            error('gnssparser:TargetParseError', 'Line %d: %s', ...
                stats.total_lines, err.message);
        end
    end
end
end
