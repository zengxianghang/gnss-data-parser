function testNovatelAscii()
%TESTNOVATELASCII Basic regression checks for MATLAB common NovAtel layer.

sample = ['#PSRVELA,USB1,0,51.5,FINESTEERING,2209,511827.000,' ...
    '02000020,0dd6,16809;SOL_COMPUTED,WAAS,0.000,4.000,0.0175,' ...
    '290.743174,0.0309,0*3d24adcc'];

msg = gnssparser.novatel.parseAsciiLine(sample, 'PSRVELA', true);
assert(strcmp(msg.header.message, 'PSRVELA'));
assert(strcmp(msg.header.port, 'USB1'));
assert(msg.header.week == 2209);
assert(abs(msg.header.sow - 511827.0) < 1e-12);
assert(msg.header.receiver_status == uint32(hex2dec('02000020')));
assert(msg.header.reserved == uint32(hex2dec('0DD6')));
assert(msg.header.software_version == 16809);
assert(msg.crc == uint32(hex2dec('3D24ADCC')));
assert(strcmp(gnssparser.novatel.peekMessageName(sample), 'PSRVELA'));
assert(strcmp(gnssparser.novatel.peekMessageName('#PSRVEL2A,COM1,0;1*00000000'), ...
    'PSRVEL2A'));
assert(isempty(gnssparser.novatel.peekMessageName('$GPRMC,1')));

failed = false;
try
    gnssparser.novatel.parseAsciiLine(sample, 'PSRVEL', false);
catch
    failed = true;
end
assert(failed, 'Exact message-name mismatch should raise an error.');

fprintf('testNovatelAscii: PASS\n');
end
