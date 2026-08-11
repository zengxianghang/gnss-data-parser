function stats = scanNovatelRange(filename, callback, varargin)
%SCANNOVATELRANGE Stream RANGEA epochs from a mixed ASCII log.
if nargin < 2, callback = []; end
parser = @(line, verifyCrc) gnssparser.novatel.parseRangeLine(line, verifyCrc);
stats = gnssparser.common.scanTargetLines(filename, 'RANGEA', parser, callback, varargin{:});
end
