%% analysis_get_and_parse_files

%   - load selected datafile 
%       - import to matlab if necessary
%   - parse header (PID gain, calibration tables)
%       - import calibration tables if necessary
%   - adjust PID (set baseline to zero, divide by gain)
%   - convert flow to sccm
%   - convert ctrl to voltage
%   - save .mat file

%%
clearvars
close all
%#ok<*SAGROW>
%#ok<*AGROW> 
%% config variables
c = struct();   % struct containing all config variables

% instrument names (for parsing from datafile)
c.instName_PID = 'pid';
c.instName_olfa = 'olfa';
c.instName_fsens = 'flow sensor';

% other variables
c.pid_gain = [];
c.this_exp_cal_tables = [];

a_this_note = '';

%% enter directory for this computer
a_dir_OlfaEngDropbox = 'C:\Users\Admin\Dropbox (NYU Langone Health)\OlfactometerEngineeringGroup (2)';
%a_dir_OlfaEngDropbox = 'C:\Users\SB13FLLT004\Dropbox (NYU Langone Health)\OlfactometerEngineeringGroup (2)';

a_dir_OlfaControlGUI = strcat(a_dir_OlfaEngDropbox,'\Control\a_software\OlfaControl_GUI');

%{
%% select shit to plot
plot_opts = struct();
% plot olfa as sccm or int
plot_opts.plot_sccm = 'no';
% **if datafile does not have calibration tables listed in header, plot will be in ints regardless

% pick one of these
plot_opts.pid = 'yes';
plot_opts.output_flow = 'no';
plot_opts.ctrl = 'no';
plot_opts.ctrl_as_voltage = 'no';
%}

%% enter data file name
%{
%a_thisfile_name = '2020-12-15_exp01_21';
%a_thisfile_name = '2020-12-16_exp01_22';
%a_thisfile_name = '2022-09-08_datafile_00';
%a_thisfile_name = '2022-09-07_datafile_01'; a_this_note = 'sensor calibration';
%a_thisfile_name = '2022-09-07_datafile_02'; a_this_note = 'sensor calibration';
%a_thisfile_name = '2022-09-07_datafile_03'; a_this_note = 'setpoint char 0-100 sccm';
%a_thisfile_name = '2022-09-07_datafile_04'; a_this_note = 'setpoint char 80, 90, 100 sccm';
%a_thisfile_name = '2022-09-07_datafile_05';
%}
%a_thisfile_name = '2022-09-06_datafile_11';

% 9/9/2022
    % setpoint characterization
%a_thisfile_name = '2022-09-09_datafile_00'; a_this_note = 'A2 at 100sccm';
a_thisfile_name = '2022-09-09_datafile_01'; a_this_note = 'A6 at 100sccm';
    % K values
%a_thisfile_name = '2022-09-09_datafile_02'; a_this_note = 'A6- Kp at .05, .04, .03, .01, .00, .08';
%a_thisfile_name = '2022-09-09_datafile_03'; a_this_note = 'A6- Kp at .010, .005, .010, .010,';
%a_thisfile_name = '2022-09-09_datafile_04'; a_this_note = 'A6- with A2 vial, Kp back at .05';
%a_thisfile_name = '2022-09-09_datafile_05'; a_this_note = 'A6- with A2 vial, Kp back at .05, with correct cal table';
%a_thisfile_name = '2022-09-09_datafile_06'; a_this_note = 'A6- with A2 vial, Kp at .10, .15, .05';
%a_thisfile_name = '2022-09-09_datafile_07'; a_this_note = 'A6- with A2 vial, Kp at .05, .04, .03, .02, .01';
%a_thisfile_name = '2022-09-09_datafile_08'; a_this_note = 'A6- Kp at .05, Ki at .0001, .0005, .0010';
    % additive
%a_thisfile_name = '2022-09-09_datafile_09'; a_this_note = 'A2 90cc, A6 10cc';
%a_thisfile_name = '2022-09-09_datafile_10'; a_this_note = 'A2 50cc, A6 50cc';
%a_thisfile_name = '2022-09-09_datafile_11'; a_this_note = 'A2 50cc, A6 50cc';
%a_thisfile_name = '2022-09-09_datafile_12'; a_this_note = 'A2 & A6 additive';
    % setpoint characterization
%a_thisfile_name = '2022-09-09_datafile_13'; a_this_note = 'A2 setpoint char';
%a_thisfile_name = '2022-09-09_datafile_14'; a_this_note = 'A6 setpoint char';
%a_thisfile_name = '2022-09-09_datafile_15'; a_this_note = 'A6 setpoint char';
    % flow calibration
%{
%a_thisfile_name = '2022-09-12_datafile_00'; a_this_note = 'A2 flow calibration (automated)';
%a_thisfile_name = '2022-09-13_datafile_00';
%a_this_note = '110 sccm auto calibration';
%a_this_note = '100 sccm auto calibration'; % def still decreasing
%a_this_note = '90 sccm auto calibration';  % a little bit decreasing
%a_this_note = '80 sccm auto calibration';  % still decreasing but so close
%a_this_note = '100 sccm';
%a_this_note = '90 sccm';
%}

%% set up directories
dir_data_files = [a_dir_OlfaControlGUI '\result_files\48-line olfa\'];

% make sure datafiles are on matlab path
addpath(genpath(dir_data_files));

%% load file
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

% get the .mat file
raw_wholeFile = import_datafile(a_thisfile_name,dir_this_data_file);
clearvars dir_*

%% parse header
h = struct();
h.header_goes_til = (find(strcmp(raw_wholeFile,'Time')))+1;
raw_header = raw_wholeFile(1:h.header_goes_til-2,:);

% get calibration table names from header
h.cal_tables_start_at = (find(strcmp(raw_header,'Calibration Tables:')))+1;
if ~isempty(h.cal_tables_start_at)
    c.this_exp_cal_tables = raw_header(h.cal_tables_start_at:end,:);
end

% get PID gain from header
h.PID_gain_line_idx = find(strcmp(raw_header,'PID gain:'));
if ~isempty(h.PID_gain_line_idx)
    c.pid_gain = raw_header{h.PID_gain_line_idx,2};
end

%% parse file
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
        %clearvars idx_*
        %
        % len_olfa_name = length(c.instName_olfa);
        %i_vial_num = i_inst(idx_olfa_start+len_olfa_name+1:end);
        
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
            d_olfa_flow(i_vial_idx).flow.flow_int = [d_olfa_flow(i_vial_idx).flow.flow_int;i_this_pair];
        
        % add to d_olfa_flow(v).ctrl.ctrl_int
        elseif strcmp(i_para,'Ctrl')
            d_olfa_flow(i_vial_idx).ctrl.ctrl_int = [d_olfa_flow(i_vial_idx).ctrl.ctrl_int;i_this_pair];
        
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
    
    end
end
clearvars i* n* matches idx_*
%% get calibration tables
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
%% adjust PID
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
%% convert olfa to sccm
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

%% save data
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
