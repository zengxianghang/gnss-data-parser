function testInspva()
%TESTINSPVA Regression checks for MATLAB INSPVA support.

sample = ['#INSPVAA,USB1,0,67.5,FINESTEERING,2209,490558.000,' ...
    '02000020,18bc,16809;2209,490558.000000000,51.15043714042,' ...
    '-114.03067871718,1080.3548,0.0051,-0.0014,-0.0012,' ...
    '-0.296402993,0.311887972,157.992156267,INS_SOLUTION_GOOD*cc698020'];
r = gnssparser.novatel.parseInspvaLine(sample, true);
assert(r.week == 2209);
assert(abs(r.sow - 490558.0) < 1e-12);
assert(r.header_week == 2209);
assert(abs(r.header_sow - 490558.0) < 1e-12);
assert(abs(r.vel_n_mps - 0.0051) < 1e-12);
assert(abs(r.vel_u_mps + 0.0012) < 1e-12);
assert(strcmp(r.ins_status, 'INS_SOLUTION_GOOD'));

different = ['#INSPVAA,USB1,0,1,FINESTEERING,2209,490558.100,' ...
    '00000000,0000,1;2209,490558.000000000,1,2,3,4,5,6,7,8,9,' ...
    'INS_SOLUTION_GOOD*00000000'];
r2 = gnssparser.novatel.parseInspvaLine(different, false);
assert(abs(r2.header_sow - 490558.1) < 1e-9);
assert(abs(r2.sow - 490558.0) < 1e-9);

fprintf('testInspva: PASS\n');
end
