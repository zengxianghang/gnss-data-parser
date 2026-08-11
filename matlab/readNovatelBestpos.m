function [records, stats] = readNovatelBestpos(filename, varargin)
%READNOVATELBESTPOS Read all BESTPOSA records into a struct array.
records = struct([]);
stats = scanNovatelBestpos(filename, @collect, varargin{:});
    function collect(record)
        if isempty(records), records = record; else, records(end + 1) = record; end %#ok<AGROW>
    end
end
