function testValidateRealLog()
%TESTVALIDATEREALLOG Exercise real-log validation on the shared fixture.
here=fileparts(mfilename('fullpath')); root=fileparts(fileparts(here));
logFile=fullfile(root,'tests','fixtures','cross_language','sample.log');
outDir=[tempname '_gnss_validation']; mkdir(outDir);
cleanup=onCleanup(@() cleanupDir(outDir)); %#ok<NASGU>
summary=validateRealLog(logFile,'OutputDir',outDir,'VerifyCrc',true,'VerifyChecksum',true, ...
    'SampleFirst',5,'SampleLast',5,'SampleEvery',1000);
assert(summary.stats.total_lines==7 && summary.stats.unrelated_lines==1);
keys={'psrvel','range','inspva','bestpos','bestvel','rmc'};
for k=1:numel(keys)
    key=keys{k}; assert(summary.messages.(key).records==1); assert(summary.messages.(key).malformed==0);
    assert(exist(fullfile(outDir,[key '.csv']),'file')==2);
end
rangeText=fileread(fullfile(outDir,'range.csv'));
assert(contains(rangeText,'source_line_number') && contains(rangeText,'#RANGEA,'));
assert(contains(rangeText,',26,') && contains(rangeText,sprintf('%u',uint32(hex2dec('1810dc04')))));
decoded=jsondecode(fileread(fullfile(outDir,'summary.json')));
assert(strcmp(decoded.implementation,'matlab') && decoded.schema_version==1);
fprintf('testValidateRealLog: PASS\n');
end

function cleanupDir(path)
if exist(path,'dir'), rmdir(path,'s'); end
end
