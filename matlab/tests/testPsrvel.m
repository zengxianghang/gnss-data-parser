function testPsrvel()
%TESTPSRVEL Regression checks for MATLAB PSRVEL support.

sample = ['#PSRVELA,USB1,0,51.5,FINESTEERING,2209,511827.000,' ...
    '02000020,0dd6,16809;SOL_COMPUTED,WAAS,0.000,4.000,0.0175,' ...
    '290.743174,0.0309,0*3d24adcc'];
r = gnssparser.novatel.parsePsrvelLine(sample, true);
assert(r.week == 2209);
assert(abs(r.sow - 511827.0) < 1e-12);
assert(strcmp(r.sol_status, 'SOL_COMPUTED'));
assert(strcmp(r.vel_type, 'WAAS'));
assert(abs(r.hor_speed_mps - 0.0175) < 1e-12);
assert(abs(r.vert_speed_mps - 0.0309) < 1e-12);

noncomputed = ['#PSRVELA,COM1,0,0.0,FINESTEERING,2209,1.000,' ...
    '00000000,0000,16809;INSUFFICIENT_OBS,NONE,0,0,0,0,0,0*00000000'];
r2 = gnssparser.novatel.parsePsrvelLine(noncomputed, false);
assert(strcmp(r2.sol_status, 'INSUFFICIENT_OBS'));

file = [tempname '.log'];
fid = fopen(file, 'w');
assert(fid >= 0);
cleanup = onCleanup(@() cleanupFile(fid, file)); %#ok<NASGU>
fprintf(fid, 'noise\n%s\n', sample);
fclose(fid);
fid = -1;
[records, stats] = readNovatelPsrvel(file, 'VerifyCrc', true);
assert(numel(records) == 1);
assert(stats.records == 1 && stats.target_lines == 1);

fprintf('testPsrvel: PASS\n');
end

function cleanupFile(fid, file)
if fid >= 0, fclose(fid); end
if exist(file, 'file'), delete(file); end
end
