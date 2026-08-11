function count = writeCsvRows(fid, rows)
%WRITECSVROWS Write normalized validation rows with RFC-style CSV quoting.
count = 0;
for r = 1:numel(rows)
    row = rows{r};
    for c = 1:numel(row)
        if c > 1, fprintf(fid,','); end
        fprintf(fid,'%s',escapeCsv(row{c}));
    end
    fprintf(fid,'\n');
    count = count + 1;
end
end

function out = escapeCsv(text)
if isstring(text), text = char(text); end
if isempty(text), out = ''; return; end
text = strrep(text,'"','""');
if any(text==',') || any(text=='"') || any(text==char(10)) || any(text==char(13))
    out = ['"' text '"'];
else
    out = text;
end
end
