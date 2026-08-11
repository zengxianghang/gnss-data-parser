function status = decodeTrackingStatus(value)
%DECODETRACKINGSTATUS Decode OEM7 RANGE 32-bit channel tracking status.
value = uint32(value);
system = double(bitand(bitshift(value, -16), uint32(7)));
signal = double(bitand(bitshift(value, -21), uint32(31)));
status = struct();
status.raw = value;
status.tracking_state = double(bitand(value, uint32(31)));
status.sv_channel = double(bitand(bitshift(value, -5), uint32(31)));
status.phase_locked = hasBit(value, 10);
status.parity_known = hasBit(value, 11);
status.code_locked = hasBit(value, 12);
status.correlator_type = double(bitand(bitshift(value, -13), uint32(7)));
status.satellite_system = system;
status.satellite_system_name = systemName(system);
status.grouped = hasBit(value, 20);
status.signal_type = signal;
status.signal_name = signalName(system, signal);
status.primary_l1 = hasBit(value, 27);
status.half_cycle_added = hasBit(value, 28);
status.digital_filter = hasBit(value, 29);
status.prn_locked_out = hasBit(value, 30);
status.forced_assignment = hasBit(value, 31);
end

function tf = hasBit(value, bit)
tf = bitand(value, bitshift(uint32(1), bit)) ~= 0;
end

function name = systemName(system)
names = {'GPS','GLONASS','SBAS','GALILEO','BEIDOU','QZSS','NAVIC','OTHER'};
if system >= 0 && system < numel(names)
    name = names{system + 1};
else
    name = sprintf('SYSTEM_%d', system);
end
end

function name = signalName(system, signal)
name = sprintf('SIGNAL_%d', signal);
switch system
    case 0
        codes = [0 5 9 14 16 17]; labels = {'L1CA','L2P','L2P_Y','L5Q','L1CP','L2CM'};
    case 1
        codes = [0 1 5 6]; labels = {'L1CA','L2CA','L2P','L3Q'};
    case 2
        codes = [0 6]; labels = {'L1CA','L5I'};
    case 3
        codes = [2 6 7 12 17 20]; labels = {'E1C','E6B','E6C','E5AQ','E5BQ','E5ALTBOCQ'};
    case 4
        codes = [0 1 2 4 5 6 7 9 11]; labels = {'B1I_D1','B2I_D1','B3I_D1','B1I_D2','B2I_D2','B3I_D2','B1CP','B2AP','B2BI'};
    case 5
        codes = [0 14 16 17 27 28]; labels = {'L1CA','L5Q','L1CP','L2CM','L6P','L6D'};
    case 6
        codes = 0; labels = {'L5SPS'};
    case 7
        codes = 19; labels = {'LBAND'};
    otherwise
        codes = []; labels = {};
end
idx = find(codes == signal, 1, 'first');
if ~isempty(idx), name = labels{idx}; end
end
