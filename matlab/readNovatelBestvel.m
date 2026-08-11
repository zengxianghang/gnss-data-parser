function [records, stats] = readNovatelBestvel(filename, varargin)
%READNOVATELBESTVEL Read all BESTVELA records into a struct array.
records = struct([]);
stats = scanNovatelBestvel(filename, @collect, varargin{:});
    function collect(record)
        if isempty(records), records = record; else, records(end + 1) = record; end %#ok<AGROW>
    end
end
