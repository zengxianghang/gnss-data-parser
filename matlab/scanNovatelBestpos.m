function stats = scanNovatelBestpos(filename, callback, varargin)
%SCANNOVATELBESTPOS Stream BESTPOSA records from a mixed ASCII log.
if nargin < 2, callback = []; end
parser = @(line, verifyCrc) gnssparser.novatel.parseBestposLine(line, verifyCrc);
stats = gnssparser.common.scanTargetLines(filename, 'BESTPOSA', parser, callback, varargin{:});
end
