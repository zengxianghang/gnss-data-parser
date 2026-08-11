function summary = validateRealLog(filename, varargin)
%VALIDATEREALLOG Validate real GNSS logs with one mixed-log scan.
%   SUMMARY = validateRealLog(FILE) writes <stem>_validation_matlab containing
%   summary.json plus deterministic per-message CSV samples. Full expanded
%   CSV output is opt-in with 'FullExport',true because RANGE can be huge.
%
%   Options: OutputDir, Messages, Strict, VerifyCrc, VerifyChecksum,
%   SampleFirst (5), SampleLast (5), SampleEvery (1000), FullExport (false).

opts = struct('OutputDir','','Messages',[],'Strict',false,'VerifyCrc',false, ...
    'VerifyChecksum',false,'SampleFirst',5,'SampleLast',5,'SampleEvery',1000,'FullExport',false);
if mod(numel(varargin),2)~=0, error('gnssparser:InvalidOptions','Options must be name/value pairs.'); end
for k=1:2:numel(varargin)
    name=varargin{k}; if isstring(name), name=char(name); end
    switch lower(name)
        case 'outputdir', opts.OutputDir=varargin{k+1};
        case 'messages', opts.Messages=varargin{k+1};
        case 'strict', opts.Strict=logical(varargin{k+1});
        case 'verifycrc', opts.VerifyCrc=logical(varargin{k+1});
        case 'verifychecksum', opts.VerifyChecksum=logical(varargin{k+1});
        case 'samplefirst', opts.SampleFirst=double(varargin{k+1});
        case 'samplelast', opts.SampleLast=double(varargin{k+1});
        case 'sampleevery', opts.SampleEvery=double(varargin{k+1});
        case 'fullexport', opts.FullExport=logical(varargin{k+1});
        otherwise, error('gnssparser:InvalidOptions','Unknown option: %s.',name);
    end
end
if isstring(filename), filename=char(filename); end
[folder,stem,ext]=fileparts(filename);
if isempty(opts.OutputDir), outDir=fullfile(folder,[stem '_validation_matlab']); else, outDir=opts.OutputDir; end
if isstring(outDir), outDir=char(outDir); end
if ~exist(outDir,'dir'), mkdir(outDir); end
selected=gnssparser.common.normalizeMessageSelection(opts.Messages);
states=struct(); handlers=struct();
for k=1:numel(selected)
    key=selected{k}; s=struct('count',0,'fixed',{{}},'last',{{}},'rows',0,'fid',-1,'first_time',[],'last_time',[]);
    if opts.FullExport
        s.fid=fopen(fullfile(outDir,[key '.csv']),'w');
        if s.fid<0, error('gnssparser:FileOpenError','Cannot create validation CSV.'); end
        gnssparser.validation.writeCsvRows(s.fid,{gnssparser.validation.columns(key)});
    end
    states.(key)=s; thisKey=key;
    handlers.(key)=@(record,source) consume(thisKey,record,source);
end
try
    stats=scanGnssLog(filename,handlers,'Messages',selected,'Strict',opts.Strict, ...
        'VerifyCrc',opts.VerifyCrc,'VerifyChecksum',opts.VerifyChecksum,'PassSourceInfo',true);
catch err
    closeAll(); rethrow(err);
end
for k=1:numel(selected)
    key=selected{k}; s=states.(key);
    if opts.FullExport
        fclose(s.fid); s.fid=-1;
    else
        path=fullfile(outDir,[key '.csv']); fid=fopen(path,'w');
        if fid<0, closeAll(); error('gnssparser:FileOpenError','Cannot create %s.',path); end
        gnssparser.validation.writeCsvRows(fid,{gnssparser.validation.columns(key)});
        entries=[s.fixed s.last];
        if ~isempty(entries)
            idx=zeros(1,numel(entries)); for j=1:numel(entries), idx(j)=entries{j}.index; end
            [~,order]=sort(idx); entries=entries(order); lastIndex=-1;
            for j=1:numel(entries)
                e=entries{j}; if e.index==lastIndex, continue; end
                rows=gnssparser.validation.flattenRecord(key,e.record,e.source,e.index);
                s.rows=s.rows+gnssparser.validation.writeCsvRows(fid,rows); lastIndex=e.index;
            end
        end
        fclose(fid);
    end
    states.(key)=s;
end
info=dir(filename); if isempty(info), error('gnssparser:FileOpenError','Cannot stat file: %s',filename); end
messages=struct();
for k=1:numel(selected)
    key=selected{k}; s=states.(key);
    messages.(key)=struct('target_lines',stats.target_lines.(key),'records',stats.records.(key), ...
        'malformed',stats.malformed.(key),'csv_file',[key '.csv'], ...
        'export_mode',ternary(opts.FullExport,'full','sample'),'exported_rows',s.rows, ...
        'first_time',s.first_time,'last_time',s.last_time);
end
summary=struct(); summary.schema_version=1; summary.implementation='matlab';
summary.source=struct('file_name',[stem ext],'size_bytes',info.bytes);
summary.options=struct('strict',opts.Strict,'verify_crc',opts.VerifyCrc,'verify_checksum',opts.VerifyChecksum, ...
    'sample_first',opts.SampleFirst,'sample_last',opts.SampleLast,'sample_every',opts.SampleEvery,'full_export',opts.FullExport);
summary.stats=stats; summary.messages=messages;
fid=fopen(fullfile(outDir,'summary.json'),'w');
if fid<0, error('gnssparser:FileOpenError','Cannot create summary.json.'); end
fprintf(fid,'%s\n',jsonencode(summary)); fclose(fid);
fprintf('validation output: %s\n',outDir);
for k=1:numel(selected)
    key=selected{k}; fprintf('%-8s records=%d malformed=%d exported_rows=%d\n',key,stats.records.(key),stats.malformed.(key),states.(key).rows);
end

    function consume(key,record,source)
        s=states.(key); s.count=s.count+1; index=s.count; marker=timeMarker(key,record);
        if isempty(s.first_time), s.first_time=marker; end; s.last_time=marker;
        entry=struct('index',index,'record',record,'source',source);
        if opts.FullExport
            rows=gnssparser.validation.flattenRecord(key,record,source,index);
            s.rows=s.rows+gnssparser.validation.writeCsvRows(s.fid,rows);
        else
            if index<=opts.SampleFirst || (opts.SampleEvery>0 && mod(index,opts.SampleEvery)==0)
                s.fixed{end+1}=entry;
            end
            if opts.SampleLast>0
                s.last{end+1}=entry;
                if numel(s.last)>opts.SampleLast, s.last(1)=[]; end
            end
        end
        states.(key)=s;
    end
    function closeAll()
        names=fieldnames(states);
        for q=1:numel(names), s=states.(names{q}); if s.fid>=0, fclose(s.fid); s.fid=-1; states.(names{q})=s; end; end
    end
end

function marker=timeMarker(key,record)
if strcmp(key,'rmc'), marker=struct('date_ddmmyy',record.date_ddmmyy,'utc_time',record.utc_time);
else, marker=struct('week',double(record.week),'sow',double(record.sow)); end
end
function value=ternary(condition,a,b)
if condition, value=a; else, value=b; end
end
