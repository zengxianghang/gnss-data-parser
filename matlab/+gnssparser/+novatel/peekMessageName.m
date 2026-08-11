function name = peekMessageName(line)
%PEEKMESSAGENAME Return exact #...A message name without full tokenization.

if isstring(line)
    line = char(line);
end
name = '';
if ~ischar(line) || isempty(line) || line(1) ~= '#'
    return;
end
comma = find(line == ',', 1, 'first');
semicolon = find(line == ';', 1, 'first');
idx = [comma semicolon];
idx = idx(idx > 0);
if isempty(idx)
    return;
end
stop = min(idx);
if stop > 2
    name = line(2:stop - 1);
end
end
