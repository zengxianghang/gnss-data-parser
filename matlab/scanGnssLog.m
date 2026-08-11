function stats = scanGnssLog(filename, handlers, varargin)
%SCANGNSSLOG Scan selected supported GNSS message types in one file pass.
%   STATS = scanGnssLog(FILE, HANDLERS) reads FILE exactly once and dispatches
%   each selected record to an optional callback in HANDLERS. Stable handler
%   field names are: psrvel, range, inspva, bestpos, bestvel, rmc.
%
%   Options: Messages, Strict, VerifyCrc, VerifyChecksum, PassSourceInfo.
%   PassSourceInfo=false preserves the original callback(record) API. When
%   true, callbacks receive callback(record, source), where source contains
%   line_number and raw_line for validation/debugging without a second scan.

if nargin < 2 || isempty(handlers), handlers = struct(); end
if ~isstruct(handlers), error('gnssparser:InvalidHandlers', 'Handlers must be a struct.'); end
opts = struct('Messages', [], 'Strict', false, 'VerifyCrc', false, ...
    'VerifyChecksum', false, 'PassSourceInfo', false);
messagesSpecified = false;
if mod(numel(varargin), 2) ~= 0, error('gnssparser:InvalidOptions', 'Options must be name/value pairs.'); end
for k = 1:2:numel(varargin)
    name = varargin{k}; if isstring(name), name = char(name); end
    if ~ischar(name), error('gnssparser:InvalidOptions', 'Option names must be text.'); end
    switch lower(name)
        case 'messages', opts.Messages = varargin{k+1}; messagesSpecified = true;
        case 'strict', opts.Strict = logical(varargin{k+1});
        case 'verifycrc', opts.VerifyCrc = logical(varargin{k+1});
        case 'verifychecksum', opts.VerifyChecksum = logical(varargin{k+1});
        case 'passsourceinfo', opts.PassSourceInfo = logical(varargin{k+1});
        otherwise, error('gnssparser:InvalidOptions', 'Unknown option: %s.', name);
    end
end
allKeys = {'psrvel','range','inspva','bestpos','bestvel','rmc'};
handlerNames = fieldnames(handlers);
for k = 1:numel(handlerNames)
    key = handlerNames{k};
    if ~any(strcmp(allKeys,key)), error('gnssparser:InvalidHandlers','Unsupported handler field: %s.',key); end
    callback = handlers.(key);
    if ~isempty(callback) && ~isa(callback,'function_handle')
        error('gnssparser:InvalidHandlers','Handler %s must be a function handle.',key);
    end
end
if messagesSpecified, selected = gnssparser.common.normalizeMessageSelection(opts.Messages);
elseif ~isempty(handlerNames), selected = gnssparser.common.normalizeMessageSelection(handlerNames);
else, selected = allKeys; end
if isstring(filename), filename = char(filename); end
fid = fopen(filename,'r'); if fid < 0, error('gnssparser:FileOpenError','Cannot open file: %s',filename); end
cleanup = onCleanup(@() fclose(fid)); %#ok<NASGU>
stats = struct('selected_messages',{selected},'total_lines',0,'unrelated_lines',0, ...
    'target_lines',zeroCounts(allKeys),'records',zeroCounts(allKeys),'malformed',zeroCounts(allKeys));
while true
    line = fgetl(fid); if ~ischar(line), break; end
    stats.total_lines = stats.total_lines + 1;
    key = gnssparser.common.identifyGnssLine(line);
    if isempty(key) || ~any(strcmp(selected,key))
        stats.unrelated_lines = stats.unrelated_lines + 1; continue;
    end
    stats.target_lines.(key) = stats.target_lines.(key) + 1;
    try
        record = parseByKey(key,line,opts.VerifyCrc,opts.VerifyChecksum);
        stats.records.(key) = stats.records.(key) + 1;
        if isfield(handlers,key) && ~isempty(handlers.(key))
            if opts.PassSourceInfo
                source = struct('line_number',stats.total_lines,'raw_line',line);
                handlers.(key)(record,source);
            else
                handlers.(key)(record);
            end
        end
    catch err
        stats.malformed.(key) = stats.malformed.(key) + 1;
        if opts.Strict, error('gnssparser:MixedParseError','Line %d (%s): %s',stats.total_lines,key,err.message); end
    end
end
end

function counts = zeroCounts(keys)
counts = struct(); for k=1:numel(keys), counts.(keys{k})=0; end
end
function record = parseByKey(key,line,verifyCrc,verifyChecksum)
switch key
    case 'psrvel', record=gnssparser.novatel.parsePsrvelLine(line,verifyCrc);
    case 'range', record=gnssparser.novatel.parseRangeLine(line,verifyCrc);
    case 'inspva', record=gnssparser.novatel.parseInspvaLine(line,verifyCrc);
    case 'bestpos', record=gnssparser.novatel.parseBestposLine(line,verifyCrc);
    case 'bestvel', record=gnssparser.novatel.parseBestvelLine(line,verifyCrc);
    case 'rmc', record=gnssparser.nmea.parseRmcLine(line,verifyChecksum);
    otherwise, error('gnssparser:UnsupportedMessage','Unregistered message key: %s.',key);
end
end
