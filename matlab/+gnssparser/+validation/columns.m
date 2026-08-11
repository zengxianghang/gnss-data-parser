function columns = columns(key)
%COLUMNS Shared real-log validation CSV column order.
common = {'message_type','record_index','source_line_number','raw_line'};
switch key
    case 'psrvel'
        body = {'week','sow','time_status','sol_status','vel_type','latency_s','age_s','hor_speed_mps','track_deg','vert_speed_mps','reserved','crc'};
    case 'range'
        body = {'week','sow','time_status','observation_count','obs_index','prn','glofreq','pseudorange_m','pseudorange_std_m','adr_cycles','adr_std_cycles','doppler_hz','cn0_dbhz','lock_time_s','tracking_raw','tracking_state','sv_channel','phase_locked','parity_known','code_locked','correlator_type','satellite_system','satellite_system_name','grouped','signal_type','signal_name','primary_l1','half_cycle_added','digital_filter','prn_locked_out','forced_assignment','crc'};
    case 'inspva'
        body = {'week','sow','header_week','header_sow','time_status','latitude_deg','longitude_deg','ellipsoidal_height_m','vel_n_mps','vel_e_mps','vel_u_mps','roll_deg','pitch_deg','azimuth_deg','ins_status','crc'};
    case 'bestpos'
        body = {'week','sow','time_status','sol_status','pos_type','latitude_deg','longitude_deg','msl_height_m','undulation_m','datum','lat_std_m','lon_std_m','hgt_std_m','station_id','diff_age_s','sol_age_s','tracked_sv','used_sv','used_l1_sv','used_multi_sv','reserved','ext_sol_status','gal_bds_signal_mask','gps_glo_signal_mask','crc'};
    case 'bestvel'
        body = {'week','sow','time_status','sol_status','vel_type','latency_s','age_s','hor_speed_mps','track_deg','vert_speed_mps','reserved','crc'};
    case 'rmc'
        body = {'talker_id','utc_time','utc_seconds_of_day','status','latitude_deg','longitude_deg','speed_knots','course_deg','date_ddmmyy','magnetic_variation_deg','magnetic_variation_ew','position_mode','navigation_status','checksum'};
    otherwise
        error('gnssparser:UnsupportedMessage','Unsupported validation key: %s.',key);
end
columns = [common body];
end
