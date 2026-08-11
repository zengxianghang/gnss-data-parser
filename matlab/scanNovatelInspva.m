function stats = scanNovatelInspva(filename, callback, varargin)
%SCANNOVATELINSPVA Stream INSPVAA records from a mixed ASCII log.
if nargin < 2, callback = []; end
parser = @(line, verifyCrc) gnssparser.novatel.parseInspvaLine(line, verifyCrc);
stats = gnssparser.common.scanTargetLines(filename, 'INSPVAA', parser, callback, varargin{:});
end
