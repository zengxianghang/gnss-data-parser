function fields = splitCsv(text)
%SPLITCSV Split one comma-delimited ASCII payload, honoring double quotes.
%   FIELDS = gnssparser.common.splitCsv(TEXT) returns a 1-by-N cell array
%   of character vectors. Double quotes are removed; doubled quotes inside
%   a quoted field are decoded to a single quote character.

if isstring(text)
    text = char(text);
end
if ~ischar(text)
    error('gnssparser:InvalidInput', 'CSV input must be char or string.');
end

fields = {};
buf = '';
inQuote = false;
i = 1;
while i <= numel(text)
    ch = text(i);
    if ch == '"'
        if inQuote && i < numel(text) && text(i + 1) == '"'
            buf(end + 1) = '"'; %#ok<AGROW>
            i = i + 2;
            continue;
        end
        inQuote = ~inQuote;
    elseif ch == ',' && ~inQuote
        fields{end + 1} = buf; %#ok<AGROW>
        buf = '';
    else
        buf(end + 1) = ch; %#ok<AGROW>
    end
    i = i + 1;
end

if inQuote
    error('gnssparser:CsvParseError', 'Unterminated quoted CSV field.');
end
fields{end + 1} = buf;
end
