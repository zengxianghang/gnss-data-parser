function [records, stats] = readNovatelInspva(filename, varargin)
%READNOVATELINSPVA Read all INSPVAA records into a struct array.
%   For multi-GB logs prefer scanNovatelInspva with a callback.
records = struct([]);
stats = scanNovatelInspva(filename, @collect, varargin{:});
    function collect(record)
        if isempty(records)
            records = record;
        else
            records(end + 1) = record; %#ok<AGROW>
        end
    end
end
