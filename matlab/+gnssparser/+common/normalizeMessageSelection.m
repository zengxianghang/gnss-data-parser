function keys = normalizeMessageSelection(messages)
%NORMALIZEMESSAGESELECTION Normalize aliases to stable parser keys.
%   KEYS = gnssparser.common.normalizeMessageSelection(MESSAGES)
%   accepts canonical keys or vendor-style names such as RANGE/RANGEA.

allKeys = {'psrvel', 'range', 'inspva', 'bestpos', 'bestvel', 'rmc'};
if nargin < 1 || isempty(messages)
    keys = allKeys;
    return;
end
if ischar(messages)
    messages = {messages};
elseif isstring(messages)
    messages = cellstr(messages(:));
elseif ~iscell(messages)
    error('gnssparser:InvalidMessageSelection', ...
        'Messages must be a character vector, string array, or cell array.');
end

keys = {};
for k = 1:numel(messages)
    value = messages{k};
    if isstring(value), value = char(value); end
    if ~ischar(value)
        error('gnssparser:InvalidMessageSelection', 'Message names must be text.');
    end
    alias = lower(strtrim(value));
    switch alias
        case {'psrvel', 'psrvela'}
            key = 'psrvel';
        case {'range', 'rangea'}
            key = 'range';
        case {'inspva', 'inspvaa'}
            key = 'inspva';
        case {'bestpos', 'bestposa'}
            key = 'bestpos';
        case {'bestvel', 'bestvela'}
            key = 'bestvel';
        case {'rmc', 'xxrmc', '$xxrmc'}
            key = 'rmc';
        otherwise
            error('gnssparser:UnsupportedMessage', ...
                'Unsupported message type: %s.', value);
    end
    if ~any(strcmp(keys, key))
        keys{end + 1} = key; %#ok<AGROW>
    end
end
end
