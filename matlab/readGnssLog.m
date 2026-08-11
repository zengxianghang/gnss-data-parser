function [data, stats] = readGnssLog(filename, varargin)
%READGNSSLOG Collect multiple supported GNSS message types in one file pass.
%   [DATA, STATS] = readGnssLog(FILE) reads all currently supported message
%   types. Use 'Messages' to select a subset. DATA always contains stable fields
%   psrvel, range, inspva, bestpos, bestvel, and rmc; unselected fields are empty.
%
%   This convenience API retains parsed records in memory. For multi-GB logs,
%   prefer scanGnssLog with callbacks so records can be consumed incrementally.

keys = {'psrvel', 'range', 'inspva', 'bestpos', 'bestvel', 'rmc'};
data = struct();
handlers = struct();
for k = 1:numel(keys)
    key = keys{k};
    data.(key) = struct([]);
    handlers.(key) = @(record) collectRecord(key, record);
end

stats = scanGnssLog(filename, handlers, varargin{:});

    function collectRecord(key, record)
        if isempty(data.(key))
            data.(key) = record;
        else
            data.(key)(end + 1) = record; %#ok<AGROW>
        end
    end
end
