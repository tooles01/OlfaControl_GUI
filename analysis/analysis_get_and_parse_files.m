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

% instrument names (for parsing from datafile)
c.instName_PID = 'pid';
c.instName_olfa = 'olfa';
c.instName_fsens = 'flow sensor';

% other variables
c.pid_gain = [];
c.this_exp_cal_tables = [];

a_this_note = '';
flow_inc = [];

%% Enter directory for this computer
%a_dir_OlfaEngDropbox = 'C:\Users\Admin\Dropbox (NYU Langone Health)\OlfactometerEngineeringGroup (2)';
%a_dir_OlfaEngDropbox = 'C:\Users\SB13FLLT004\Dropbox (NYU Langone Health)\OlfactometerEngineeringGroup (2)';
a_dir_OlfaEngDropbox = 'C:\Users\shann\Dropbox (NYU Langone Health)\OlfactometerEngineeringGroup (2)';

a_dir_OlfaControlGUI = strcat(a_dir_OlfaEngDropbox,'\Control\a_software\OlfaControl_GUI');

%{
%% popup box to select file name # TODO
default_date = '2023-03-02';

default_filename = '2023-03-02_datafile_02';

% get date from filename
idx_und = strfind(a_thisfile_name,'_');
idx_und = idx_und(1);
a_thisfile_date = a_thisfile_name(1:idx_und-1);

% full directory for this file
dir_this_data_file = strcat(a_dir_OlfaControlGUI,'\result_files\48-line olfa\',a_thisfile_date,'\');

%default_directory = 'C:\Users\Admin\Dropbox (NYU Langone Health)\OlfactometerEngineeringGroup (2)\Control\a_software\OlfaControl_GUI\result_files';
default_directory = strcat(a_dir_OlfaControlGUI,'\result_files');
uibox_title = 'Select datafile';
uibox_deffilename ='d';
file = uigetfile("*.csv",uibox_title);

%a_default_file_name = '2023-03-02_datafile_02';

%}

%% Enter data file name

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

a_thisfile_name = '2024-01-19_datafile_00';

%% Set up directories
dir_data_files = [a_dir_OlfaControlGUI '\result_files\48-line olfa\'];
%dir_data_files = [a_dir_OlfaControlGUI '\result_files\cheap olfa\'];

% make sure datafiles are on matlab path
addpath(genpath(dir_data_files));

%% Load file
% directory where raw data files are stored
%{
    % before doing matlab processing, copy the file into this folder (as
    % a .mat file). processing will be done on this version of the file.
    % (speeds up matlab so it doesn't have to get the .csv everytime & precaution
    % against things happening to the original files during analysis)
%}
    
% parse out file date
idx_und = strfind(a_thisfile_name,'_');
idx_und = idx_und(1);
a_thisfile_date = a_thisfile_name(1:idx_und-1);

% full directory for this file
dir_this_data_file = strcat(a_dir_OlfaControlGUI,'\result_files\48-line olfa\',a_thisfile_date,'\');
%dir_this_data_file = strcat(a_dir_OlfaControlGUI,'\result_files\cheap olfa\',a_thisfile_date,'\');


% get the .mat file
raw_wholeFile = import_datafile(a_thisfile_name,dir_this_data_file);
clearvars dir_* a_thisfile_date

%% Parse header
h = struct();
h.header_goes_til = (find(strcmp(raw_wholeFile,'Time')))+1;
raw_header = raw_wholeFile(1:h.header_goes_til-2,:);

% get calibration table names from header
h.cal_tables_start_at = (find(strcmp(raw_header,'Calibration Tables:')))+1;
if ~isempty(h.cal_tables_start_at)
    c.this_exp_cal_tables = raw_header(h.cal_tables_start_at:end,:);
end

% get PID gain from header
h.PID_gain_row_idx = find(strcmp(raw_header,'PID gain:'));
if ~isempty(h.PID_gain_row_idx)
    c.pid_gain = raw_header{h.PID_gain_row_idx,2};
end

clearvars raw_header
%% Parse file
raw_data = raw_wholeFile(h.header_goes_til:end,:);
clearvars h
num_data = height(raw_data);

% convert time to seconds
data_time_raw = raw_data(:,1);
data_time_raw = vertcat(data_time_raw{:});
data_time_raw = data_time_raw-data_time_raw(1);
data_time_raw = milliseconds(data_time_raw);
data_time_raw = data_time_raw/1000;
raw_data(:,1) = num2cell(data_time_raw);

% parse into olfa, pid, event data
data_pid_raw = [];
data_fsens_raw = [];
% olfa
d_olfa_flow = [];
d_olfa_events = [];
d_olfa_events(1).all = [];
d_olfa_events(1).OV = [];
d_olfa_events(1).Sp = [];
d_olfa_vials_recorded = [];

% for each line of data:
for i=1:num_data
    i_time = raw_data{i,1};     % get time, instrument, value
    i_inst = raw_data{i,2};
    i_valu = raw_data{i,4};
    
    % if instrument name contains 'pid'
    if contains(i_inst,c.instName_PID)
        num_p = height(data_pid_raw) + 1;
        data_pid_raw(num_p,1) = i_time;
        data_pid_raw(num_p,2) = i_valu;
    end
    
    % if instrument name contains 'flow sensor'
    if contains(i_inst,c.instName_fsens)
        num_f = height(data_fsens_raw) + 1;
        data_fsens_raw(num_f,1) = i_time;
        data_fsens_raw(num_f,2) = i_valu;
    end
    
    % if instrument name contains 'olfactometer'
    if contains(i_inst,c.instName_olfa)
        i_para = raw_data{i,3};

        % check which olfa name this datafile uses ('olfa prototype' was used in 4-line mixing chamber tests')
        if contains(i_inst,'olfactometer')
            c.instName_olfa = 'olfactometer';
        else
            c.instName_olfa = 'olfa prototype';
        end
        
        % get the vial number
        idx_olfa_start = strfind(i_inst,c.instName_olfa);
        i_vial_num = i_inst(idx_olfa_start+length(c.instName_olfa)+1:end);

        if (length(i_vial_num) == 2)
            % single vial thing happened
        
            % if we don't have data for this vial yet, add a row for it to the structures
            matches = strfind(d_olfa_vials_recorded,i_vial_num);     % check if this vial is in vials recorded
            if isempty(matches)
                % add to vials recorded
                d_olfa_vials_recorded = [d_olfa_vials_recorded i_vial_num];
                
                % add it to the structures
                d_olfa_flow(length(d_olfa_flow)+1).vial_num = i_vial_num;
                d_olfa_flow(length(d_olfa_flow)).flow.flow_int = [];
                d_olfa_flow(length(d_olfa_flow)).flow.flow_sccm = [];
                d_olfa_flow(length(d_olfa_flow)).ctrl.ctrl_int = [];
                d_olfa_flow(length(d_olfa_flow)).ctrl.ctrl_volt = [];
                d_olfa_flow(length(d_olfa_flow)).events.OV = [];
                d_olfa_flow(length(d_olfa_flow)).events.Sp = [];
            
            end

            % find out which struct row this vial is
            vial_list = {d_olfa_flow().vial_num};               % list of values under vial_num
            i_vial_idx =  find(strcmp(vial_list,i_vial_num));   % index of this vial
            
            i_this_pair = [i_time i_valu];
            
            % add to d_olfa_flow(i_vial_idx).flow.flow_int
            if strcmp(i_para,'FL')
                d_olfa_flow(i_vial_idx).flow.flow_int = [d_olfa_flow(i_vial_idx).flow.flow_int;i_this_pair];    % TODO speed this up
            
            % add to d_olfa_flow(v).ctrl.ctrl_int
            elseif strcmp(i_para,'Ctrl')
                d_olfa_flow(i_vial_idx).ctrl.ctrl_int = [d_olfa_flow(i_vial_idx).ctrl.ctrl_int;i_this_pair];    % TODO speed this up
        
            % add to events
            else
                % add to d_olfa_events.all
                num_e = length(d_olfa_events.all) + 1;
                d_olfa_events.all(num_e).time = i_time;
                d_olfa_events.all(num_e).vial = i_vial_num;
                d_olfa_events.all(num_e).event = i_para;
                d_olfa_events.all(num_e).value = i_valu;
                
                % add to d_olfa_events.OV
                if strcmp(i_para,'OV')
                    num_e = length(d_olfa_events.OV) + 1;
                    d_olfa_events.OV(num_e).t_start = i_time;
                    d_olfa_events.OV(num_e).vial = i_vial_num;
                    d_olfa_events.OV(num_e).duration = i_valu;
                end
                % add to d_olfa_events.Sp
                if strcmp(i_para,'Sp')
                    num_e = length(d_olfa_events.Sp) + 1;
                    d_olfa_events.Sp(num_e).time = i_time;
                    d_olfa_events.Sp(num_e).vial = i_vial_num;
                    d_olfa_events.Sp(num_e).value_int = i_valu;
                end
                
                % nope neither of those matter
                % but also let's add it to d_olfa_flow
                
                % add to d_olfa_flow(v).events.OV
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
                % add to d_olfa_flow(v).events.Sp
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
            % this was an event that affected more than one vial
            slave_name = i_vial_num(1);
            vial_numbers = i_vial_num(2:end);
            num_vials_affected = length(vial_numbers);

            % for each vial in the string
            for v=1:num_vials_affected
                this_vial_num = vial_numbers(v);
                this_vial_full_num = [slave_name this_vial_num];
                
                % find out which struct row this vial is (hopefully we have already collected data for this vial)
                vial_list = {d_olfa_flow().vial_num};                       % list of values under vial_num
                i_vial_idx = find(strcmp(vial_list,this_vial_full_num));    % index of this vial

                % add it to this vial's events
                if strcmp(i_para,'OV')
                    n = length(d_olfa_flow(i_vial_idx).events.OV) + 1;
                    d_olfa_flow(i_vial_idx).events.OV(n).time = i_time;
                    d_olfa_flow(i_vial_idx).events.OV(n).value = i_valu;
                end
            end

            % add to d_olfa_events.OV
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

% for each vial in olfa_data_flow
for i=1:length(d_olfa_flow)
    i_this_vial = d_olfa_flow(i).vial_num;
    i_this_cal_table_name = [];
    d_olfa_flow(i).cal_table_name = [];
    
    % get the cal table name
    for k=1:length(c.this_exp_cal_tables)
        if strcmp(i_this_vial,c.this_exp_cal_tables{k,1})
            i_this_cal_table_name = c.this_exp_cal_tables{k,2};  % find the vial in c.this_exp_cal_tables
            d_olfa_flow(i).cal_table_name = i_this_cal_table_name;
            %break;  % just to save time
        end
    end
    
    % get the cal table data
    if ~isempty(i_this_cal_table_name)
        this_cal_file_data = import_cal_table(i_this_cal_table_name,dir_cal_tables);
        d_olfa_flow(i).cal_table = this_cal_file_data;
    end

end

clearvars cal_* dir_* this_cal_file_data k
%% Adjust PID
data_pid = data_pid_raw;
if ~isempty(data_pid)

    % if PID gain was in the header, divide by that value
    if ~isempty(c.pid_gain)
        PID_newstr = erase(c.pid_gain,'x');                     % remove the 'x'
        c.pid_gain_numeric = str2double(PID_newstr);            % convert to double
        data_pid(:,2) = data_pid(:,2) / c.pid_gain_numeric; % divide data by gain
    end
    
    % set baseline to zero
    if ~isempty(d_olfa_events.OV)
        
        % PID data up until first OV event
        t_begin = data_time_raw(1);
        t_end = d_olfa_events.OV(1).t_start;
        PID_sectionData = get_section_data(data_pid,t_begin,t_end);
        
        % mean PID value during this period
        PID_baseline = mean(PID_sectionData(:,2));

        % adjust all PID values
        data_pid(:,1) = data_pid(:,1);
        data_pid(:,2) = data_pid(:,2)-PID_baseline;

        clearvars t_* PID_*
    end
    
    % convert from mV to V
    data_pid(:,2) = data_pid(:,2)/1000;

end
%% Convert olfa to sccm
% for each vial
for i=1:length(d_olfa_flow)
    % if there are flow values
    if ~(isempty(d_olfa_flow(i).flow.flow_int))
        % if there is a cal table to use
        if ~isempty(d_olfa_flow(i).cal_table_name)
            % use cal table to convert to sccm
            d_olfa_flow(i).flow.flow_sccm = int_to_SCCM(d_olfa_flow(i).flow.flow_int,d_olfa_flow(i).cal_table);
        end
    end
end

%% convert ctrl to voltage
% for each vial
for i=1:length(d_olfa_flow)
    if ~(isempty(d_olfa_flow(i).ctrl.ctrl_int))
        % convert to voltage
        i_ctrl_voltage = [];
        i_ctrl_voltage(:,1) = d_olfa_flow(i).ctrl.ctrl_int(:,1);
        i_ctrl_voltage(:,2) = (d_olfa_flow(i).ctrl.ctrl_int(:,2)/255)*5;
        d_olfa_flow(i).ctrl.ctrl_volt = i_ctrl_voltage;
    end
end

clearvars i*

%% Smooth PID
% get moving average (50ms windows)

if ~isempty(data_pid)    
    p_og_pid_data = data_pid;
    p_mov_avg_window = .050;        % 50 ms window
    %p_new_pid_data = data_pid;
    p_new_pid_data = removeDuplicates_(data_pid);
    p_sample_points = p_new_pid_data(:,1);
    p_input_array = p_new_pid_data(:,2);

    p_new_pid_data(:,1) = p_new_pid_data(:,1);
    p_new_pid_data(:,2) = movmean(p_input_array,p_mov_avg_window,'SamplePoints',p_sample_points);
    data_pid = p_new_pid_data;
    p_index = find(data_pid~=p_new_pid_data);
    
    clearvars p_*
end


%% Split into sections
% get flow/pid for each event section

% for each vial
for i=1:length(d_olfa_flow)
    these_events = d_olfa_flow(i).events.OV;
    this_flow_data_int = d_olfa_flow(i).flow.flow_int;
    this_flow_data_sccm = d_olfa_flow(i).flow.flow_sccm;

    this_vial_means_int = [];
    this_vial_means_sccm = [];
    e_new_event_struct = [];

    % for each event
    for e=1:length(these_events)
        e_t_start = these_events(e).time;
        e_duration = these_events(e).value;
        e_t_end = e_t_start + e_duration;
        
        % ignore the event if the duration is less than 5.3 seconds
        if (e_duration >= 1)
        %if (e_duration >= 5.3)

            % cut first 50ms
            e_t_start = e_t_start + 0.050;
            
            e_new_event_struct(e).t_event = these_events(e).time;   % actual time of OV
            e_new_event_struct(e).t_duration = these_events(e).value;
            e_new_event_struct(e).t_start = e_t_start;              % time to calculate shit from
            e_new_event_struct(e).t_end = e_t_end;

            % get this vial flow data for this period
            this_section_data_int = get_section_data(this_flow_data_int,e_t_start,e_t_end);
            e_new_event_struct(e).data.flow_int = this_section_data_int;
            if ~isempty(this_flow_data_sccm)
                this_section_data_sccm = get_section_data(this_flow_data_sccm,e_t_start,e_t_end);
                e_new_event_struct(e).data.flow_sccm = this_section_data_sccm;
            end

            % get PID data for this period
            this_section_pid_data = get_section_data(data_pid,e_t_start,e_t_end);
            e_new_event_struct(e).data.pid = this_section_pid_data;

            % calculate mean flow & pid
            e_new_event_struct(e).flow_mean_int = mean(this_section_data_int(:,2));
            e_new_event_struct(e).flow_mean_sccm = mean(this_section_data_sccm(:,2));
            e_new_event_struct(e).pid_mean = mean(this_section_pid_data(:,2));
            e_new_event_struct(e).pid_std = std(this_section_pid_data(:,2));
            e_new_event_struct(e).flow_std_int = std(this_section_data_int(:,2));
            e_new_event_struct(e).flow_std_sccm = std(this_section_data_sccm(:,2));

            % add to matrix of (int_mean, pid_mean) for all events
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

% remove empty rows
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

%% Create d_olfa_data_combined
% for each vial in d_olfa_flow
for v=1:length(d_olfa_flow)
    sourceStructArray = d_olfa_flow(v).events.OV_keep;  % TODO fix this, needs to specify which row of d_olfa_flow
    fieldsToCopy = {'flow_mean_sccm', 'pid_mean','data'};       % Specify the field(s) you want to copy
    
    % Initialize the target struct array with the same structure as sourceStructArray
    numElements = numel(sourceStructArray);
    targetStructArray = repmat(struct('flow_mean_sccm', [], 'pid_mean', [],'data', []), 1, numElements);
    
    % Loop through each struct in the source struct array
    for i = 1:numElements
        sourceStruct = sourceStructArray(i);
        targetStruct = struct();            % Initialize the target struct for this iteration
        % Copy the specified fields and their values
        for j = 1:numel(fieldsToCopy)
            field = fieldsToCopy{j};
            if isfield(sourceStruct, field)
                targetStruct.(field) = sourceStruct.(field);
            end
        end
        targetStructArray(i) = targetStruct;            % Assign the target struct to the target struct array
    end

    %% Sort by flow mean (create d_olfa_data_sorted)
    fieldName = 'flow_mean_sccm';
    fieldValues = {targetStructArray.(fieldName)};
    fieldValues = cell2mat(fieldValues);
    [~,sortedIndices] = sort(fieldValues,'ascend');
    d_olfa_data_sorted = targetStructArray(sortedIndices);
    
    clearvars field* source* target* i j sortedIndices
    
    %% Initialize the combined data structure
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

    %% Add shit to the combined data structure
    
    % start from this starting index
    starting_idx = 1;
    % check the lengths of the structures: if there are zero values, then the lengths of these two structs will be different
    r = 0;
    r = rem(length(d_olfa_data_sorted),length(d_olfa_data_combined));
    % if there is a remainder, then start at idx 3
    if r ~= 0; starting_idx = r+1; end
    
    for i=starting_idx:length(d_olfa_data_sorted)
        this_flow_value = d_olfa_data_sorted(i).flow_mean_sccm;
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
