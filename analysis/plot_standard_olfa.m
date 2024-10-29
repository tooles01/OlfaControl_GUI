%% Plot file from olfa calibration

% get standard olfa datafile, plot & save

clear variables
%close all
set(0,'DefaultTextInterpreter','none')
%#ok<*AGROW>
%#ok<*NASGU>
%#ok<*SAGROW>

%% Find OlfaControl_GUI directory (& add to path)

% Check if current directory contains 'OlfaControl_GUI'
c_current_dir = pwd;
c_str_to_find = 'OlfaControl_GUI';
c_idx_of_str = strfind(c_current_dir,c_str_to_find);
c_len_of_strToFind = length(c_str_to_find);
if isempty(c_idx_of_str); disp([c_str_to_find ' is not within current directory.']); end

% Get full path to 'OlfaControl_GUI' folder
a_dir_OlfaControlGUI = c_current_dir(1:c_idx_of_str+c_len_of_strToFind-1);

% Make sure datafiles are on matlab path
dir_data_files = [a_dir_OlfaControlGUI '\result_files\standard olfa\'];
addpath(genpath(dir_data_files));
% Make sure functions are on matlab path
dir_functions = [a_dir_OlfaControlGUI '\analysis\functions'];
addpath(genpath(dir_functions));

clearvars c_*

%% Display variables
a_this_note = '';
flow_inc = [];

plot_opts = struct();
plot_opts.individual_trials = 'no';  % plot each trial by itself
plot_opts.x_lines = 'yes';           % x lines of where the mean was calculated from

f = struct();   % struct containing all figure variables
f.dot_size = 60;
f.PID_color = [.4667 .6745 .1882];
f.pid_lims = [];

%f.f_position = [166 210 1300 600];      % for PowerPoint
f.f_position = [166 210 650 600];       % for PowerPoint (1/2 size)
%f.f_position = [-1895 575 650 600];     % left side display

f.f2_position = [260 230 812 709];

c = struct();           % struct containing all config variables
c.nidaq_freq = 0.01;    % collection frequency etc etc      % NOTE: only used here and in plot_on_top ; why do we use this
c.time_to_cut = 2.00;   % don't look at any data before this time

%% Enter data file name

%a_thisfile_name= '2023-11-06_datafile_00_ethyltiglate.csv'; a_this_note = 'Ethyl Tiglate vial 10 - 10s on, 30s off';
%a_thisfile_name= '2023-11-06_datafile_01_ethyltiglate.csv'; a_this_note = 'Ethyl Tiglate vial 10 - 10s on, 30s off';
a_thisfile_name = '2023-11-06_datafile_02_ethyltiglate.csv'; a_this_note = 'Ethyl Tiglate vial 10 - 10s on, 30s off'; flow_inc = 10;
%a_thisfile_name = '2023-11-07_datafile_00_ethyltiglate_B.csv'; a_this_note = 'Ethyl Tiglate vial 9 - 10s on, 30s off';
%f.pid_lims = [0 3];

f.pid_lims = [0 8];
%c.time_to_cut = 2;
c.time_to_cut = 0;
%plot_opts.individual_trials = 'yes';


% 10/28/24
a_thisfile_name = '2023-11-06_datafile_02_ethyltiglate_copy.csv'; a_this_note = 'Ethyl Tiglate vial 10 - 10s on, 30s off'; flow_inc = 10;
c.time_to_cut = 1;
%plot_opts.individual_trials = 'yes';
plot_opts.x_lines = 'yes';
f.pid_lims = [0 3];
%a_thisfile_name = '2023-11-13_datafile_03_v12_B_copy'; a_this_note = 'Pinene vial 12 - 8s on, 20s off (suction off)'; flow_inc = 20;

%% Load file
% TODO change this so we don't have to include .csv
% TODO also mimic import_datafile: check if file exists already before loading it in (pos unnecessary tho because these files are not as large as 8line olfa files)

% Get full directory for this file
dir_this_data_file = strcat(dir_data_files,a_thisfile_name);
% Read the file in
a_thisfile = readcell(dir_this_data_file);
% Remove .csv from file name
a_thisfile_name = erase(a_thisfile_name,'.csv');


%% Cut out header stuff
% TODO change a_thisfile to raw_wholeFile (and a_raw_file to something else)
% Skip down to the third row
header_goes_til = 3;
a_raw_file = a_thisfile(header_goes_til:end,:);

% Cut out the first column (vial number)
a_raw_file = a_raw_file(:,2:end);

clearvars header_goes_til

%% Get PID baseline value

% Get all PID values recorded in the first trial (row 1)
pid_values = a_raw_file(1,2:end);

% Remove missing cells
last_index = length(pid_values);
while ismissing(pid_values{last_index})
    last_index = last_index - 1;
end
pid_values = pid_values(1:last_index);

% Get minimum value from this trial (PID adjustment value)
pid_values = cell2mat(pid_values);
pid_adjustment_value = min(pid_values);

clearvars last*
%% smooth PID   % TODO maybe

%%
if strcmp(plot_opts.individual_trials,'yes'); close all; end% TODO move this later

%% Initialize data structures

d_olfa_data = [];   % TODO change to d_olfa_data_combined
d_olfa_data(1).flow_value = [];
d_olfa_data(1).pid_mean = [];
d_olfa_data(1).pid_std = [];
d_olfa_data(1).data = [];

%% Calculate stuff
% For each trial (each row of the file)
for i=1:height(a_raw_file)
    
    % Get data
    sccm_value = a_raw_file(i,1);
    this_sccm_value = sccm_value{1};    % Convert from cell to double
    pid_values = a_raw_file(i,2:end);
    
    %% Adjust PID
    % Remove missing cells
    last_index = length(pid_values);
    while ismissing(pid_values{last_index})
        last_index = last_index - 1;
    end
    pid_values = pid_values(1:last_index);

    % Create array of time values
    number_of_data = length(pid_values);
    last_time_value = number_of_data * c.nidaq_freq;
    last_time_value = last_time_value - c.nidaq_freq;
    time_data = 0:c.nidaq_freq:last_time_value;
    
    % Shift the pid values up to 0
    pid_values = cell2mat(pid_values);
    pid_values = pid_values - pid_adjustment_value;
    
    pid_data = [];
    pid_data(:,1) = time_data;
    pid_data(:,2) = pid_values;
    
    %% Calculate mean PID value

    % Cut from the beginning of the trial
    
    % Get data starting at c.time_to_cut seconds into the trial
    idx_of_start_time = (c.time_to_cut/c.nidaq_freq) + 1;   % Index of c.time_to_cut seconds
    new_pid_data = pid_data(idx_of_start_time:end,:);
    
    % Cut off 2 seconds anyways (to let it get up there a little bit)
    if (c.time_to_cut < 2)
        new_pid_data_1 = get_section_data(new_pid_data,2,new_pid_data(end,1));
    else
        new_pid_data_1 = new_pid_data;
    end
    
    % Cut from the end of the trial

    % Find what time the PID drops below threshold (0.1V)
    idx_below_threshold = find(new_pid_data_1(:,2) < 0.1,1);
    time_below_threshold = new_pid_data_1(idx_below_threshold,1);
    
    % Get the time value 0.1s before it drops

    % If this was a normal trial, make the end time 0.1s before the PID drops below threshold (0.1V)
    if ~(idx_below_threshold == 1)
        end_time = time_below_threshold - .1;
    % If PID started below 0.1V (aka this was a 0 sccm trial), just make it a 4 second trial
    else
        end_time = 4;
        str = ['this was a 0 sccm trial (', num2str(this_sccm_value),' sccm, i=', num2str(i), ')'];
        disp(str)
    end
    end_idx = find(new_pid_data_1(:,1) <= end_time,1,'last');     % Index of where end_time happens
    
    % Get all the data for this period
    this_pid_data = new_pid_data_1(1:end_idx,:);
    
    % Calculate mean/std
    mean_pid = mean(this_pid_data(:,2));
    std_pid = std(this_pid_data(:,2));
    
    %% Plot this trial by itself
    if strcmp(plot_opts.individual_trials,'yes')
        f1 = figure(i+1); hold on; legend;
        f1.Position = f.f_position;
        f1_subtitle = [num2str(this_sccm_value) ' sccm'];
        subtitle(f1_subtitle);
        title(a_thisfile_name)
        xlabel('Time (s)');
        ylabel('PID (V)');
        xlim([-.5 last_time_value])
        if ~isempty(f.pid_lims); ylim(f.pid_lims); end
        p = plot(time_data,pid_values);
        p.DisplayName = ['PID mean: ' num2str(round(mean_pid,2)) ' V'];
        p.LineWidth = 2;
        p.Color = f.PID_color;
        
        % draw xlines
        if strcmp(plot_opts.x_lines,'yes')
            xline1 = xline(this_pid_data(1,1),'HandleVisibility','off');
            xline2 = xline(end_time,'HandleVisibility','off');
        end
    end
    
    %% Add it to the data structure
    % Reshape data
    d_time_data = reshape(time_data,length(time_data),1);
    d_pid_data = reshape(pid_values,length(pid_values),1);
    % Add to d_olfa_data
    d_olfa_data(i).flow_value = this_sccm_value;
    d_olfa_data(i).pid_mean = mean_pid;
    d_olfa_data(i).pid_std = std_pid;
    d_olfa_data(i).data = [d_time_data d_pid_data];
    
end
clearvars -except a_* c d_olfa_data dir_* f flow_inc pid_adjustment_value plot_opts

%% Sort the data structure (create d_olfa_data_sorted)
fieldName = 'flow_value';
fieldValues = {d_olfa_data.(fieldName)};
fieldValues = cell2mat(fieldValues);
[~,sortedIndices] = sort(fieldValues,'ascend');
d_olfa_data_sorted = d_olfa_data(sortedIndices);

%% Initialize the combined data structure (d_olfa_data_combined)
d_olfa_data_combined = [];
d_olfa_data_combined(1).flow_value = [];
d_olfa_data_combined(1).pid_mean1 = [];
d_olfa_data_combined(1).pid_mean2 = [];
d_olfa_data_combined(1).data1 = [];
d_olfa_data_combined(1).data2 = [];
if isempty(flow_inc); disp('WARNING no flow_inc entered: using 10'); flow_inc = 10; end
flow_value = flow_inc;
num_iterations = 100/flow_inc;
for i=1:num_iterations
    d_olfa_data_combined(i).flow_value = flow_value;
    flow_value = flow_value + flow_inc;
end

% Add shit to d_olfa_data_combined
for i=1:length(d_olfa_data_sorted)
    this_flow_value = d_olfa_data_sorted(i).flow_value;
    idx_to_use = this_flow_value / flow_inc;
    
    % check if the first slot has been used yet
    if isempty(d_olfa_data_combined(idx_to_use).pid_mean1)
        d_olfa_data_combined(idx_to_use).pid_mean1 = d_olfa_data_sorted(i).pid_mean;
        d_olfa_data_combined(idx_to_use).data1 = d_olfa_data_sorted(i).data;
    else
        d_olfa_data_combined(idx_to_use).pid_mean2 = d_olfa_data_sorted(i).pid_mean;
        d_olfa_data_combined(idx_to_use).data2 = d_olfa_data_sorted(i).data;
    end
end

clearvars -except a_* c d* f pid_adjustment_value plot_opts

%% Save the data structure
mat_file_dir = strcat(pwd,'\','data (.mat files)\',a_thisfile_name,'.mat');
disp_file_dir = strcat('C:\..\data (.mat files)\',a_thisfile_name,'.mat');

if ~isfile(mat_file_dir)
    save(mat_file_dir,"d_olfa_data_sorted","d_olfa_data_combined");
    disp(['Saved file: ', disp_file_dir])
else
    delete(mat_file_dir);
    save(mat_file_dir,"d_olfa_data_sorted","d_olfa_data_combined");
    disp(['File already existed, rewrote: ', disp_file_dir])
end

%% Spt char figure
f2 = figure; hold on;
legend('Location','northwest');
f2.Position = f.f2_position;
f2.NumberTitle = 'off';
f2.Name = a_thisfile_name;
title(a_thisfile_name)
if ~strcmp(a_this_note,''); subtitle(a_this_note); end

xlabel('Flow (SCCM)')
ylabel("PID (V)");
xlim([0 100]);
if ~isempty(f.pid_lims); ylim(f.pid_lims); end

blue_color = [0 .4470 .7410];

s = scatter([d_olfa_data.flow_value],[d_olfa_data.pid_mean],'filled');
s.MarkerFaceColor = blue_color;
s.DisplayName = 'standard olfa';

% if error bars on etc etc TODO

clearvars *_color last_* disp* number_of_data plot_* i *flow_value*

