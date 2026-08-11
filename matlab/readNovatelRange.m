function [records, stats] = readNovatelRange(filename, varargin)
%READNOVATELRANGE Read all RANGEA epochs into a struct array.
%   For multi-GB logs prefer scanNovatelRange with a callback.
records = struct([]);
stats = scanNovatelRange(filename, @collect, varargin{:});
    function collect(record)
        if isempty(records)
            records = record;
        else
            records(end + 1) = record; %#ok<AGROW>
        end
    end
end
