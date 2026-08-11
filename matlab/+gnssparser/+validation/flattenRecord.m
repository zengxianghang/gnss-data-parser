function rows = flattenRecord(key, record, source, recordIndex)
%FLATTENRECORD Convert one parsed record to shared validation CSV rows.
base = {key, fmt(recordIndex), fmt(source.line_number), source.raw_line};
columns = gnssparser.validation.columns(key);
body = columns(5:end);
if ~strcmp(key,'range')
    row = base;
    for k = 1:numel(body)
        name = body{k};
        row{end+1} = fmt(record.(name)); %#ok<AGROW>
    end
    rows = {row};
    return;
end
rows = cell(1,record.observation_count);
for obsIndex = 1:record.observation_count
    obs = record.observations(obsIndex);
    row = base;
    for k = 1:numel(body)
        name = body{k};
        switch name
            case {'week','sow','time_status','observation_count','crc'}
                value = record.(name);
            case 'obs_index'
                value = obsIndex;
            case {'prn','glofreq','pseudorange_m','pseudorange_std_m','adr_cycles','adr_std_cycles','doppler_hz','cn0_dbhz','lock_time_s'}
                value = obs.(name);
            case 'tracking_raw'
                value = obs.tracking.raw;
            otherwise
                value = obs.tracking.(name);
        end
        row{end+1} = fmt(value); %#ok<AGROW>
    end
    rows{obsIndex} = row;
end
end

function text = fmt(value)
if isempty(value), text = ''; return; end
if isstring(value), value = char(value); end
if ischar(value), text = value; return; end
if islogical(value), text = sprintf('%d',value~=0); return; end
if isnumeric(value)
    if isscalar(value) && isnan(double(value)), text = ''; return; end
    text = sprintf('%.17g',double(value)); return;
end
text = char(string(value));
end
