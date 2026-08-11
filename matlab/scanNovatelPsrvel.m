function stats = scanNovatelPsrvel(filename, callback, varargin)
%SCANNOVATELPSRVEL Stream PSRVELA records from a mixed ASCII log.
%   STATS = scanNovatelPsrvel(FILE, CALLBACK, 'Strict', false, ...
%       'VerifyCrc', false)
if nargin < 2, callback = []; end
parser = @(line, verifyCrc) gnssparser.novatel.parsePsrvelLine(line, verifyCrc);
stats = gnssparser.common.scanTargetLines(filename, 'PSRVELA', parser, ...
    callback, varargin{:});
end
