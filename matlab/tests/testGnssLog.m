function testGnssLog()
%TESTGNSSLOG Validate single-pass mixed readers against individual readers.

here = fileparts(mfilename('fullpath'));
root = fileparts(fileparts(here));
logFile = fullfile(root, 'tests', 'fixtures', 'cross_language', 'sample.log');

[data, stats] = readGnssLog(logFile, 'VerifyCrc', true, 'VerifyChecksum', true);
assert(isequaln(data.psrvel, readNovatelPsrvel(logFile, 'VerifyCrc', true)));
assert(isequaln(data.range, readNovatelRange(logFile, 'VerifyCrc', true)));
assert(isequaln(data.inspva, readNovatelInspva(logFile, 'VerifyCrc', true)));
assert(isequaln(data.bestpos, readNovatelBestpos(logFile, 'VerifyCrc', true)));
assert(isequaln(data.bestvel, readNovatelBestvel(logFile, 'VerifyCrc', true)));
assert(isequaln(data.rmc, readUbloxRmc(logFile, 'VerifyChecksum', true)));

assert(stats.total_lines == 7);
assert(stats.unrelated_lines == 1);
keys = {'psrvel', 'range', 'inspva', 'bestpos', 'bestvel', 'rmc'};
for k = 1:numel(keys)
    key = keys{k};
    assert(stats.target_lines.(key) == 1);
    assert(stats.records.(key) == 1);
    assert(stats.malformed.(key) == 0);
end

[subset, subsetStats] = readGnssLog(logFile, 'Messages', {'RANGEA', 'RMC'});
assert(numel(subset.range) == 1 && numel(subset.rmc) == 1);
assert(isempty(subset.psrvel) && isempty(subset.inspva));
assert(subsetStats.total_lines == 7 && subsetStats.unrelated_lines == 5);
assert(isequal(subsetStats.selected_messages, {'range', 'rmc'}));

seenRange = 0;
handlers = struct('range', @countRange);
streamStats = scanGnssLog(logFile, handlers);
assert(seenRange == 1);
assert(isequal(streamStats.selected_messages, {'range'}));
assert(streamStats.records.range == 1);

caught = false;
try
    readGnssLog(logFile, 'Messages', {'GGA'});
catch err
    caught = strcmp(err.identifier, 'gnssparser:UnsupportedMessage');
end
assert(caught, 'Unsupported message selection must fail explicitly.');

fprintf('testGnssLog: PASS\n');

    function countRange(~)
        seenRange = seenRange + 1;
    end
end
