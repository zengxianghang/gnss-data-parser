function [records, stats] = readNovatelPsrvel(filename, varargin)
%READNOVATELPSRVEL Read all PSRVELA records into a struct array.
%   For multi-GB logs prefer scanNovatelPsrvel with a callback.

records = struct([]);
stats = scanNovatelPsrvel(filename, @collect, varargin{:});

    function collect(record)
        if isempty(records)
            records = record;
        else
            records(end + 1) = record; %#ok<AGROW>
        end
    end
end
