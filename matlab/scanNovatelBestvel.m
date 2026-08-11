function stats = scanNovatelBestvel(filename, callback, varargin)
%SCANNOVATELBESTVEL Stream BESTVELA records from a mixed ASCII log.
if nargin < 2, callback = []; end
parser = @(line, verifyCrc) gnssparser.novatel.parseBestvelLine(line, verifyCrc);
stats = gnssparser.common.scanTargetLines(filename, 'BESTVELA', parser, callback, varargin{:});
end
