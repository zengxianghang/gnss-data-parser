function [records, stats] = readUbloxRmc(filename, varargin)
%READUBLOXRMC Read all $xxRMC records into a struct array.
%   For multi-GB logs prefer scanUbloxRmc with a callback.
records = struct([]);
stats = scanUbloxRmc(filename, @collect, varargin{:});
    function collect(record)
        if isempty(records), records = record; else, records(end + 1) = record; end %#ok<AGROW>
    end
end
