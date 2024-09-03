%% analysis_get_and_parse_files

%   - load selected datafile 
%       - import to matlab if necessary
%   - parse header (PID gain, calibration tables)
%       - import calibration tables if necessary
%   - adjust PID (set baseline to zero, divide by gain)
%   - convert flow to sccm
%   - convert ctrl to voltage
%   - smooth PID (moving average)
%   - split into sections & calculate mean
%   - save .mat file

%%
clearvars
%close all
%#ok<*SAGROW>
%#ok<*AGROW> 
%% Config variables
c = struct();   % struct containing all config variables

% Instrument names (for parsing from datafile)
c.instName_PID = 'pid';
c.instName_olfa = 'olfa';
c.instName_fsens = 'flow sensor';

% Other variables
c.pid_gain = [];
c.this_exp_cal_tables = [];

a_this_note = '';
flow_inc = [];

%% Find OlfaControl_GUI directory (& add to path)

% Check if current directory contains 'OlfaControl_GUI'
c_current_dir = pwd;
c_str_to_find = 'OlfaControl_GUI';
c_idx_of_str = strfind(c_current_dir,c_str_to_find);

% If not, whole thing will fail (i don't feel like writing another try except statement rn)
if isempty(c_idx_of_str); disp(['Could not find ''' c_str_to_find,''' directory.']); end

% Get OlfaControl_GUI path
c_len_of_strToFind = length(c_str_to_find);
%a_dir_OlfaControlGUI = c_current_dir(1:c_idx_of_str+c_len_of_strToFind);
a_dir_OlfaControlGUI = c_current_dir(1:c_idx_of_str+c_len_of_strToFind-1);

% Make sure datafiles are on matlab path
dir_data_files = [a_dir_OlfaControlGUI '\result_files\48-line olfa\'];
addpath(genpath(dir_data_files));

clearvars c_*

%% Enter data file name & note
% ****Do not include '.csv' at end of file name****

% checking flow sensor reponse to pvalve open
%a_thisfile_name = '2024-02-07_datafile_00'; a_this_note = '100 sccm, ctrl 255';
%a_thisfile_name = '2024-02-07_datafile_01'; a_this_note = '100 sccm, ctrl 255';
%a_thisfile_name = '2024-02-07_datafile_02'; a_this_note = '80 sccm, ctrl 255';
%a_thisfile_name = '2024-02-07_datafile_03'; a_this_note = '80 sccm, ctrl 255';
%a_thisfile_name = '2024-02-07_datafile_04'; a_this_note = '60 sccm, ctrl 255';
%a_thisfile_name = '2024-02-07_datafile_05'; a_this_note = '60 sccm, ctrl 255';
%a_thisfile_name = '2024-02-07_datafile_06'; a_this_note = '40 sccm, ctrl 255';
%a_thisfile_name = '2024-02-07_datafile_07'; a_this_note = '40 sccm, ctrl 255';
%a_thisfile_name = '2024-02-07_datafile_08'; a_this_note = '20 sccm, ctrl 255';
%a_thisfile_name = '2024-02-07_datafile_09'; a_this_note = '20 sccm, ctrl 255';
%a_thisfile_name = '2024-02-07_datafile_10'; a_this_note = '0 sccm, ctrl 255';
%a_thisfile_name = '2024-02-07_datafile_11'; a_this_note = '0 sccm, ctrl 255';

%a_thisfile_name = '2024-02-07_datafile_12'; a_this_note = '100 sccm, ctrl 120';
%a_thisfile_name = '2024-02-07_datafile_13'; a_this_note = '100 sccm, ctrl 120';

% checking flow sensor response at ctrl=0,1,2,3,45V
%a_thisfile_name = '2024-02-08_datafile_00'; a_this_note = '100 sccm, ctrl 0';
%a_thisfile_name = '2024-02-08_datafile_01'; a_this_note = '100 sccm, ctrl 255';
%a_thisfile_name = '2024-02-08_datafile_02'; a_this_note = '100 sccm, ctrl 51';
%a_thisfile_name = '2024-02-08_datafile_03'; a_this_note = '100 sccm, ctrl 204';
%a_thisfile_name = '2024-02-08_datafile_04'; a_this_note = '100 sccm, ctrl 102';
%a_thisfile_name = '2024-02-08_datafile_05'; a_this_note = '100 sccm, ctrl 153';
%a_thisfile_name = '2024-02-08_datafile_06'; a_this_note = '100 sccm, watching if E4 gets hot';

%a_thisfile_name = '2024-02-09_datafile_00'; a_this_note = 'E4 at 100 sccm over time';
% flow sensor with multiple pvalves open
%a_thisfile_name = '2024-02-09_datafile_01'; a_this_note = '100 sccm, 0 pvalves open';
%a_thisfile_name = '2024-02-09_datafile_02'; a_this_note = '100 sccm, 1 pvalve open';
%a_thisfile_name = '2024-02-09_datafile_03'; a_this_note = '100 sccm, 2 pValves open';
%a_thisfile_name = '2024-02-09_datafile_04'; a_this_note = '100 sccm, 3 pValves open';
%a_thisfile_name = '2024-02-09_datafile_05'; a_this_note = '100 sccm, 4 pValves open';
%a_thisfile_name = '2024-02-09_datafile_06'; a_this_note = '100 sccm, 5 pValves open';
%a_thisfile_name = '2024-02-09_datafile_07'; a_this_note = '100 sccm, 6 pValves open';
%a_thisfile_name = '2024-02-09_datafile_08'; a_this_note = '100 sccm, 7 pValves open';
%a_thisfile_name = '2024-02-09_datafile_09'; a_this_note = '100 sccm, 8 pValves open';

%a_thisfile_name = '2024-02-13_datafile_00'; a_this_note = '100 sccm, watching if E4 gets hot';

% flow sensor with ctrl at 120,130,140,150,160,170,180,190,200,210,220
%a_thisfile_name = '2024-02-13_datafile_01'; a_this_note = '100 sccm, ctrl=220';
%a_thisfile_name = '2024-02-13_datafile_02'; a_this_note = '100 sccm, ctrl=210';
%a_thisfile_name = '2024-02-13_datafile_03'; a_this_note = '100 sccm, ctrl=200';
%a_thisfile_name = '2024-02-13_datafile_04'; a_this_note = '100 sccm, ctrl=190';
%a_thisfile_name = '2024-02-13_datafile_05'; a_this_note = '100 sccm, ctrl=180';
%a_thisfile_name = '2024-02-13_datafile_06'; a_this_note = '100 sccm, ctrl=170';
%a_thisfile_name = '2024-02-13_datafile_07'; a_this_note = '100 sccm, ctrl=160';
%a_thisfile_name = '2024-02-13_datafile_08'; a_this_note = '100 sccm, ctrl=150';
%a_thisfile_name = '2024-02-13_datafile_09'; a_this_note = '100 sccm, ctrl=140';
%a_thisfile_name = '2024-02-13_datafile_10'; a_this_note = '100 sccm, ctrl=130';
%a_thisfile_name = '2024-02-13_datafile_11'; a_this_note = '100 sccm, ctrl=120';

%a_thisfile_name = '2024-02-13_datafile_12'; a_this_note = '100 sccm, watching if E4 gets hot';

%a_thisfile_name = '2024-01-19_datafile_00';
%a_thisfile_name = '2024-08-27_datafile_00'; a_this_note = 'E1 (no vial) 100 sccm test';
%a_thisfile_name = '2024-08-28_datafile_test'; a_this_note = 'nothing';


%% Load file
% Loads datafile (*.csv) and saves a separate copy as a *.mat file 
%{
    % Before doing matlab processing, copies the file into this folder (as a .mat file). 
    % Processing will be done on this version of the file. 
    % (Speeds up matlab so it doesn't have to get the .csv everytime + a precaution 
    % against anything happening to the original files during analysis.)
%}
    
% Parse out file date
idx_underscore = strfind(a_thisfile_name,'_');
a_thisfile_date = a_thisfile_name(1:idx_underscore(1)-1);

% Get full directory for this file
dir_this_data_file = strcat(a_dir_OlfaControlGUI,'\result_files\48-line olfa\',a_thisfile_date,'\');

% Get the *.mat file
raw_wholeFile = import_datafile(a_thisfile_name,dir_this_data_file);

clearvars dir_* a_thisfile_date

%% Parse header
% Get calibration tabl names & PID gain from datafile header; add that information to config variables (struct)

h = struct();
h.header_goes_til = (find(strcmp(raw_wholeFile,'Time')))+1;
raw_header = raw_wholeFile(1:h.header_goes_til-2,:);

% Get calibration table names from header
h.cal_tables_start_at = (find(strcmp(raw_header,'Calibration Tables:')))+1;
if ~isempty(h.cal_tables_start_at)
    c.this_exp_cal_tables = raw_header(h.cal_tables_start_at:end,:);
end

% Get PID gain from header
h.PID_gain_row_idx = find(strcmp(raw_header,'PID gain:'));
if ~isempty(h.PID_gain_row_idx)
    c.pid_gain = raw_header{h.PID_gain_row_idx,2};
end

clearvars raw_header
%% Parse file

% Remove header
raw_data = raw_wholeFile(h.header_goes_til:end,:);
num_data = height(raw_data);
clearvars h

% Convert time into seconds
data_time_raw = raw_data(:,1);
data_time_raw = vertcat(data_time_raw{:});
data_time_raw = data_time_raw-data_time_raw(1);
data_time_raw = milliseconds(data_time_raw);
data_time_raw = data_time_raw/1000;
raw_data(:,1) = num2cell(data_time_raw);


% Parse into olfa, pid, event data

% Initialize empty data structures
data_pid_raw = [];
data_fsens_raw = [];
d_olfa_flow = [];
d_olfa_events = [];
d_olfa_events(1).all = [];
d_olfa_events(1).OV = [];
d_olfa_events(1).Sp = [];
d_olfa_vials_recorded = [];

% For each line of data:
for i=1:num_data
    % Get time, instrument, value
    i_time = raw_data{i,1};
    i_inst = raw_data{i,2};
    i_valu = raw_data{i,4};
    
    % If instrument name contains 'pid'
    if contains(i_inst,c.instName_PID)
        num_p = height(data_pid_raw) + 1;
        data_pid_raw(num_p,1) = i_time;
        data_pid_raw(num_p,2) = i_valu;
    end
    
    % If instrument name contains 'flow sensor'
    if contains(i_inst,c.instName_fsens)
        num_f = height(data_fsens_raw) + 1;
        data_fsens_raw(num_f,1) = i_time;
        data_fsens_raw(num_f,2) = i_valu;
    end
    
    % If instrument name contains 'olfactometer'
    if contains(i_inst,c.instName_olfa)
        i_para = raw_data{i,3};

        % Check which olfa name this datafile uses ('olfa prototype' was used in 4-line mixing chamber tests)
        if contains(i_inst,'olfactometer'); c.instName_olfa = 'olfactometer';
            else; c.instName_olfa = 'olfa prototype';
        end
        
        % Get the vial number
        idx_olfa_start = strfind(i_inst,c.instName_olfa);
        i_vial_num = i_inst(idx_olfa_start+length(c.instName_olfa)+1:end);
        
        if (length(i_vial_num) == 2)
            %% Single vial thing happened
            % If we don't have data for this vial yet, add a row for it to the structure (d_olfa_flow)
            matches = strfind(d_olfa_vials_recorded,i_vial_num);     % check if this vial is in vials recorded
            if isempty(matches)
                % Add to list of vials recorded
                d_olfa_vials_recorded = [d_olfa_vials_recorded i_vial_num];
                
                % Add it to the structures within 'd_olfa_flow'
                d_olfa_flow(length(d_olfa_flow)+1).vial_num = i_vial_num;
                d_olfa_flow(length(d_olfa_flow)).flow.flow_int = [];
                d_olfa_flow(length(d_olfa_flow)).flow.flow_sccm = [];
                d_olfa_flow(length(d_olfa_flow)).ctrl.ctrl_int = [];
                d_olfa_flow(length(d_olfa_flow)).ctrl.ctrl_volt = [];
                d_olfa_flow(length(d_olfa_flow)).events.OV = [];
                d_olfa_flow(length(d_olfa_flow)).events.Sp = [];
            
            end

            % Find out which struct row this vial is
            vial_list = {d_olfa_flow().vial_num};               % List of values in 'vial_num'
            i_vial_idx =  find(strcmp(vial_list,i_vial_num));   % Index of this vial
            
            % Data that's going to be added somewhere
            i_this_pair = [i_time i_valu];
            
            % Add FLOW value to 'd_olfa_flow(i_vial_idx).flow.flow_int'
            if strcmp(i_para,'FL')
                d_olfa_flow(i_vial_idx).flow.flow_int = [d_olfa_flow(i_vial_idx).flow.flow_int;i_this_pair];    % TODO speed this up
            
            % Add CTRL value to 'd_olfa_flow(v).ctrl.ctrl_int'
            elseif strcmp(i_para,'Ctrl')
                d_olfa_flow(i_vial_idx).ctrl.ctrl_int = [d_olfa_flow(i_vial_idx).ctrl.ctrl_int;i_this_pair];    % TODO speed this up
        
            % Add EVENT to structures
            else
                % Add event to 'd_olfa_events.all'
                num_e = length(d_olfa_events.all) + 1;
                d_olfa_events.all(num_e).time = i_time;
                d_olfa_events.all(num_e).vial = i_vial_num;
                d_olfa_events.all(num_e).event = i_para;
                d_olfa_events.all(num_e).value = i_valu;
                
                % Add OPEN VIAL event to 'd_olfa_events.OV'
                if strcmp(i_para,'OV')
                    num_e = length(d_olfa_events.OV) + 1;
                    d_olfa_events.OV(num_e).t_start = i_time;
                    d_olfa_events.OV(num_e).vial = i_vial_num;
                    d_olfa_events.OV(num_e).duration = i_valu;
                end
                % Add SETPOINT event to 'd_olfa_events.Sp'
                if strcmp(i_para,'Sp')
                    num_e = length(d_olfa_events.Sp) + 1;
                    d_olfa_events.Sp(num_e).time = i_time;
                    d_olfa_events.Sp(num_e).vial = i_vial_num;
                    d_olfa_events.Sp(num_e).value_int = i_valu;
                end
                
                % nope neither of those matter
                % but also let's add it to d_olfa_flow
                
                % Add OPEN VIAL event to 'd_olfa_flow(v).events.OV'
                if strcmp(i_para,'OV')
                    n = length(d_olfa_flow(i_vial_idx).events.OV) + 1;
                    d_olfa_flow(i_vial_idx).events.OV(n).time = i_time;
                    d_olfa_flow(i_vial_idx).events.OV(n).value = i_valu;
                    %{
                    % if you want to do it as a matrix instead of a struct:
                    %n = height(d_olfa_flow(i_vial_idx).events.OV) + 1;
                    %d_olfa_flow(i_vial_idx).events.OV(n,1) = i_time;
                    %d_olfa_flow(i_vial_idx).events.OV(n,2) = i_valu;
                    %}
                end
                % Add SETPOINT event to 'd_olfa_flow(v).events.Sp'
                if strcmp(i_para,'Sp')
                    n = length(d_olfa_flow(i_vial_idx).events.Sp) + 1;
                    d_olfa_flow(i_vial_idx).events.Sp(n).time = i_time;
                    d_olfa_flow(i_vial_idx).events.Sp(n).value = i_valu;
                    %{
                    % if you want to do it as a matrix instead of a struct:
                    n = height(d_olfa_flow(i_vial_idx).events.Sp) + 1;
                    d_olfa_flow(i_vial_idx).events.Sp(n,1) = i_time;
                    d_olfa_flow(i_vial_idx).events.Sp(n,2) = i_valu;
                    %}
                end
            end
        
        else
            %% Multiple vial thing happened
            % (This was an event that affected more than one vial) (Probably an OV event)
            slave_name = i_vial_num(1);
            vial_numbers = i_vial_num(2:end);
            num_vials_affected = length(vial_numbers);

            % For each vial in the string
            for v=1:num_vials_affected
                this_vial_num = vial_numbers(v);
                this_vial_full_num = [slave_name this_vial_num];
                
                % Find out which struct row this vial is (hopefully we have already collected data for this vial)
                vial_list = {d_olfa_flow().vial_num};                       % list of vial_num values
                i_vial_idx = find(strcmp(vial_list,this_vial_full_num));    % index of this vial

                % Add OPEN VIAL event to this vial's events
                if strcmp(i_para,'OV')
                    n = length(d_olfa_flow(i_vial_idx).events.OV) + 1;
                    d_olfa_flow(i_vial_idx).events.OV(n).time = i_time;
                    d_olfa_flow(i_vial_idx).events.OV(n).value = i_valu;
                end
            end

            % Add OPEN VIAL to 'd_olfa_events.OV'
            if strcmp(i_para,'OV')
                num_e = length(d_olfa_events.OV) + 1;
                d_olfa_events.OV(num_e).t_start = i_time;
                d_olfa_events.OV(num_e).vial = i_vial_num;
                d_olfa_events.OV(num_e).duration = i_valu;
            end
            
        end
    
    end
end
clearvars i* n* matches idx_* vial_list d_olfa_vials_recorded
%% Get calibration tables
dir_cal_tables = strcat(a_dir_OlfaControlGUI,'\calibration_tables\');

% For each vial that we have collected data for
for i=1:length(d_olfa_flow)
    i_this_vial = d_olfa_flow(i).vial_num;
    i_this_cal_table_name = [];
    d_olfa_flow(i).cal_table_name = [];
    
    % Get the cal table name
    for k=1:length(c.this_exp_cal_tables)
        if strcmp(i_this_vial,c.this_exp_cal_tables{k,1})
            i_this_cal_table_name = c.this_exp_cal_tables{k,2};  % find the vial in c.this_exp_cal_tables
            d_olfa_flow(i).cal_table_name = i_this_cal_table_name;
            %break;  % just to save time
        end
    end
    
    % Get the cal table data
    if ~isempty(i_this_cal_table_name)
        this_cal_file_data = import_cal_table(i_this_cal_table_name,dir_cal_tables);
        d_olfa_flow(i).cal_table = this_cal_file_data;
    end

end

clearvars cal_* dir_* this_cal_file_data k
%% Adjust PID
data_pid = data_pid_raw;
if ~isempty(data_pid)

    % If PID gain was in the header, divide by that value
    if ~isempty(c.pid_gain)
        PID_newstr = erase(c.pid_gain,'x');                     % remove the 'x'
        c.pid_gain_numeric = str2double(PID_newstr);            % convert to double
        data_pid(:,2) = data_pid(:,2) / c.pid_gain_numeric;     % divide data by gain
    end
    
    % Set baseline to zero
    if ~isempty(d_olfa_events.OV)
        
        % PID data up until first OV event
        t_begin = data_time_raw(1);
        t_end = d_olfa_events.OV(1).t_start;
        PID_sectionData = get_section_data(data_pid,t_begin,t_end);
        
        % Mean PID value during this period
        PID_baseline = mean(PID_sectionData(:,2));

        % Adjust all PID values
        data_pid(:,1) = data_pid(:,1);
        data_pid(:,2) = data_pid(:,2)-PID_baseline;

        clearvars t_* PID_*
    end
    
    % Convert from mV to V
    data_pid(:,2) = data_pid(:,2)/1000;

end
%% Convert olfa flow values to sccm
% For each vial
for i=1:length(d_olfa_flow)
    % If there are flow values
    if ~(isempty(d_olfa_flow(i).flow.flow_int))
        % If there is a cal table to use
        if ~isempty(d_olfa_flow(i).cal_table_name)
            % Use cal table to convert to sccm
            d_olfa_flow(i).flow.flow_sccm = int_to_SCCM(d_olfa_flow(i).flow.flow_int,d_olfa_flow(i).cal_table);
        end
    end
end

%% Convert ctrl values to voltage
% For each vial
for i=1:length(d_olfa_flow)
    % If there are ctrl values
    if ~(isempty(d_olfa_flow(i).ctrl.ctrl_int))
        % Convert to voltage
        i_ctrl_voltage = [];
        i_ctrl_voltage(:,1) = d_olfa_flow(i).ctrl.ctrl_int(:,1);
        i_ctrl_voltage(:,2) = (d_olfa_flow(i).ctrl.ctrl_int(:,2)/255)*5;
        d_olfa_flow(i).ctrl.ctrl_volt = i_ctrl_voltage;
    end
end

clearvars i*

%% Smooth PID data
% Get moving average (50ms windows)

if ~isempty(data_pid)
    p_mov_avg_window = .050;        % 50 ms window
    p_new_pid_data = removeDuplicates_(data_pid);   % Remove any data points with duplicate time values (or moving average won't work)
    p_sample_points = p_new_pid_data(:,1);
    p_input_array = p_new_pid_data(:,2);

    p_new_pid_data(:,1) = p_new_pid_data(:,1);
    p_new_pid_data(:,2) = movmean(p_input_array,p_mov_avg_window,'SamplePoints',p_sample_points);
    data_pid = p_new_pid_data;
    
    clearvars p_*
end


%% Split into sections
% Get flow/pid for each event section

% For each vial
for i=1:length(d_olfa_flow)
    these_events = d_olfa_flow(i).events.OV;
    this_flow_data_int = d_olfa_flow(i).flow.flow_int;
    this_flow_data_sccm = d_olfa_flow(i).flow.flow_sccm;

    this_vial_means_int = [];
    this_vial_means_sccm = [];
    e_new_event_struct = [];

    % For each event
    for e=1:length(these_events)
        e_t_start = these_events(e).time;
        e_duration = these_events(e).value;
        e_t_end = e_t_start + e_duration;
        
        % Ignore the event if the duration is less than 1 second
        if (e_duration >= 1)

            % Cut first 50ms
            e_t_start = e_t_start + 0.050;
            
            e_new_event_struct(e).t_event = these_events(e).time;   % actual time of OV
            e_new_event_struct(e).t_duration = these_events(e).value;
            e_new_event_struct(e).t_start = e_t_start;              % time to calculate shit from
            e_new_event_struct(e).t_end = e_t_end;

            % Get this vial flow data for this period
            this_section_data_int = get_section_data(this_flow_data_int,e_t_start,e_t_end);
            e_new_event_struct(e).data.flow_int = this_section_data_int;
            if ~isempty(this_flow_data_sccm)
                this_section_data_sccm = get_section_data(this_flow_data_sccm,e_t_start,e_t_end);
                e_new_event_struct(e).data.flow_sccm = this_section_data_sccm;
            end

            % Get PID data for this period (if no PID data collected, create matrix of zeroes)
            if ~isempty(data_pid)
                this_section_pid_data = get_section_data(data_pid,e_t_start,e_t_end);
                e_new_event_struct(e).data.pid = this_section_pid_data;
            else
                this_section_pid_data = zeros(length(this_section_data_int));
                e_new_event_struct(e).data.pid = this_section_pid_data;
            end

            % Calculate mean flow & pid
            e_new_event_struct(e).flow_mean_int = mean(this_section_data_int(:,2));
            e_new_event_struct(e).flow_mean_sccm = mean(this_section_data_sccm(:,2));
            e_new_event_struct(e).flow_std_int = std(this_section_data_int(:,2));
            e_new_event_struct(e).flow_std_sccm = std(this_section_data_sccm(:,2));
            e_new_event_struct(e).pid_mean = mean(this_section_pid_data(:,2));
            e_new_event_struct(e).pid_std = std(this_section_pid_data(:,2));

            % Add to matrix of (int_mean, pid_mean) for all events
            int_pair = [e_new_event_struct(e).flow_mean_int e_new_event_struct(e).pid_mean];
            sccm_pair = [e_new_event_struct(e).flow_mean_sccm e_new_event_struct(e).pid_mean];
            this_vial_means_int = [this_vial_means_int;int_pair];
            this_vial_means_sccm = [this_vial_means_sccm;sccm_pair];
            
        end
        
        d_olfa_flow(i).events.OV = e_new_event_struct;
        d_olfa_flow(i).int_means = this_vial_means_int;
        d_olfa_flow(i).sccm_means = this_vial_means_sccm;
    end
    d_olfa_flow(i).events.OV_keep = [];
end

% Remove empty rows: events longer than 1 sec go in 'd_olfa_flow.event.OV_keep'
for i=1:length(d_olfa_flow)
    these_events = d_olfa_flow(i).events.OV;
    for e=1:length(these_events)
        this_event = d_olfa_flow(i).events.OV(e);
        if ~isempty(d_olfa_flow(i).events.OV(e).t_event)
            next_idx = length(d_olfa_flow(i).events.OV_keep) + 1;
            d_olfa_flow(i).events.OV_keep(next_idx).t_event = this_event.t_event;
            d_olfa_flow(i).events.OV_keep(next_idx).t_duration = this_event.t_duration;
            d_olfa_flow(i).events.OV_keep(next_idx).t_start = this_event.t_start;
            d_olfa_flow(i).events.OV_keep(next_idx).t_end = this_event.t_end;
            d_olfa_flow(i).events.OV_keep(next_idx).data = this_event.data;
            d_olfa_flow(i).events.OV_keep(next_idx).flow_mean_int = this_event.flow_mean_int;
            d_olfa_flow(i).events.OV_keep(next_idx).flow_mean_sccm = this_event.flow_mean_sccm;
            d_olfa_flow(i).events.OV_keep(next_idx).pid_mean = this_event.pid_mean;
            d_olfa_flow(i).events.OV_keep(next_idx).pid_std = this_event.pid_std;
            d_olfa_flow(i).events.OV_keep(next_idx).flow_std_int = this_event.flow_std_int;
            d_olfa_flow(i).events.OV_keep(next_idx).flow_std_sccm = this_event.flow_std_sccm;
        end
    end
end

clearvars i e* these* this* next* *_pair

%% Create 'd_olfa_data_combined'

% For each vial in d_olfa_flow
for v=1:length(d_olfa_flow)
    % TODO fix this line, needs to specify which row of d_olfa_flow
    sourceStructArray = d_olfa_flow(v).events.OV_keep;          % Source (OV_keep events for this vial)
    fieldsToCopy = {'flow_mean_sccm', 'pid_mean','data'};       % Specify the field(s) you want to copy
    
    % Initialize the target struct array with the same structure as sourceStructArray
    numElements = numel(sourceStructArray);     % number of OV_keep events (rows)
    targetStructArray = repmat(struct('flow_mean_sccm', [], 'pid_mean', [],'data', []), 1, numElements);    % empty struct to copy everything into
    
    % Loop through each struct (each event) in the source struct array
    for i = 1:numElements
        sourceStruct = sourceStructArray(i);
        targetStruct = struct();            % Initialize empty target struct for this iteration (event)
        % Copy the specified fields and their values
        for j = 1:numel(fieldsToCopy)
            field = fieldsToCopy{j};
            if isfield(sourceStruct, field)
                targetStruct.(field) = sourceStruct.(field);
            end
        end
        targetStructArray(i) = targetStruct;    % Add just the copied fields to the target struct array
    end

    %% Sort events from lowest-->highest flow mean (create d_olfa_data_sorted)
    fieldName = 'flow_mean_sccm';
    fieldValues = {targetStructArray.(fieldName)};
    fieldValues = cell2mat(fieldValues);
    [~,sortedIndices] = sort(fieldValues,'ascend');
    d_olfa_data_sorted = targetStructArray(sortedIndices);
    
    clearvars field* source* target* i j sortedIndices
    
    %% Initialize the (blank) combined data structure
    d_olfa_data_combined = [];
    d_olfa_data_combined(1).flow_value = [];
    d_olfa_data_combined(1).pid_mean1 = [];
    d_olfa_data_combined(1).pid_mean2 = [];
    d_olfa_data_combined(1).data1 = [];
    d_olfa_data_combined(1).data2 = [];
    
    if isempty(flow_inc); disp('WARNING no flow_inc entered: using 5'); flow_inc = 5; end
    flow_value = flow_inc;
    num_iterations = 100/flow_inc;
    for i=1:num_iterations
        d_olfa_data_combined(i).flow_value = flow_value;
        flow_value = flow_value + flow_inc;
    end

    %% Add shit to the combined data structure (Add 'd_olfa_data_combined' to 'd_olfa_flow')
    
    % start from this starting index
    starting_idx = 1;
    % check the lengths of the structures: if there are zero values, then the lengths of these two structs will be different
    r = 0;
    r = rem(length(d_olfa_data_sorted),length(d_olfa_data_combined));
    % if there is a remainder, then start at idx 3
    if r ~= 0; starting_idx = r+1; end
    
    % For each event that happened
    for i=starting_idx:length(d_olfa_data_sorted)
        % Get the flow mean
        this_flow_value = d_olfa_data_sorted(i).flow_mean_sccm;
        % Get the index this flow mean should be at
        idx_to_use = round(this_flow_value / flow_inc);
    
        if idx_to_use ~= 0
            if isempty(d_olfa_data_combined(idx_to_use).pid_mean1)
                d_olfa_data_combined(idx_to_use).pid_mean1 = d_olfa_data_sorted(i).pid_mean;
                d_olfa_data_combined(idx_to_use).data1 = d_olfa_data_sorted(i).data;
            else
                d_olfa_data_combined(idx_to_use).pid_mean2 = d_olfa_data_sorted(i).pid_mean;
                d_olfa_data_combined(idx_to_use).data2 = d_olfa_data_sorted(i).data;
            end
        end
    end
    d_olfa_flow(v).d_olfa_data_combined = d_olfa_data_combined;
end
clearvars i* numElements *flow_value flow_inc r num_iterations starting_idx


%% Save data
clearvars a_dir*
mat_file_dir = strcat(pwd,'\','data (.mat files)\',a_thisfile_name,'.mat');
disp_file_dir = strcat('C:\..\data (.mat files)\',a_thisfile_name,'.mat');

if ~isfile(mat_file_dir)
    save(mat_file_dir);
    disp(['Saved file: ', disp_file_dir])
else
    delete(mat_file_dir);
    save(mat_file_dir);
    disp(['File already existed, rewrote: ', disp_file_dir])
end
