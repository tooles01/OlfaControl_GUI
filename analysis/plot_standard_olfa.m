%% plot file from olfa calibration

% get standard olfa datafile, plot & save
%%
clear variables
%close all
set(0,'DefaultTextInterpreter','none')
%#ok<*AGROW>
%#ok<*NASGU>
%#ok<*SAGROW>

%% set up directories
% enter directory for this computer
a_dir_OlfaEngDropbox = 'C:\Users\Admin\Dropbox (NYU Langone Health)\OlfactometerEngineeringGroup (2)';
%a_dir_OlfaEngDropbox = 'C:\Users\SB13FLLT004\Dropbox (NYU Langone Health)\OlfactometerEngineeringGroup (2)';

a_dir_OlfaControlGUI = strcat(a_dir_OlfaEngDropbox,'\Control\a_software\OlfaControl_GUI');
dir_data_files = [a_dir_OlfaControlGUI '\result_files\standard olfa\'];

% make sure datafiles are on matlab path
addpath(genpath(dir_data_files));

%% select shit to plot
plot_opts = struct();

plot_opts.individual_trials = 'no';  % plot each trial by itself
plot_opts.x_lines = 'yes';           % x lines of where the mean was calculated from

%% display variables
a_this_note = '';
flow_inc = [];

f = struct();   % struct containing all figure variables
f.dot_size = 60;
f.PID_color = [.4667 .6745 .1882];
f.pid_lims = [];

%f.f_position = [166 210 1300 600];      % for PowerPoint
f.f_position = [166 210 650 600];       % for PowerPoint (1/2 size)
%f.f_position = [-1895 575 650 600];     % left side display

f.f2_position = [260 230 812 709];

c = struct();   % struct containing all config variables
c.nidaq_freq = 0.01;  % collection frequency etc etc
c.time_to_cut = 2.00;  % don't look at any data before this time

%% enter data file name
%a_thisfile_name = '2023-10-02_datafile_00_shannon.csv';
%a_thisfile_name = '2023-10-04_datafile_00_standard_olfa.csv'; %a_this_note = '5s on, 5s off'; f.pid_lims = [-0.1 3.6];
%a_thisfile_name = '2023-10-04_datafile_01_standard_olfa.csv'; %a_this_note = '5s on, 5s off'; f.pid_lims = [-0.1 3.6];
%a_thisfile_name = '2023-10-04_datafile_02_standard_olfa.csv'; %a_this_note ='5s on, 10s off'; f.pid_lims = [-0.1 3.6];
%a_thisfile_name = '2023-10-04_datafile_03_standard_olfa.csv'; a_this_note ='10s on, 10s off'; f.pid_lims = [-0.1 3.6];
%a_thisfile_name = '2023-10-05_datafile_00_standard_olfa.csv'; a_this_note ='Ethyl Tiglate 10s on, 20s off'; f.pid_lims = [-0.1 3.6];
a_thisfile_name = '2023-10-09_acetophenone.csv'; plot_opts.all_points = 'yes';
%a_thisfile_name = '2023-10-09_mixed.csv';  plot_opts.individual_trials = 'no'; plot_opts.all_points = 'yes';
%a_thisfile_name = '2023-10-09_ethyl tiglate pure.csv'; a_this_note ='Ethyl Tiglate Pure - 8s on, 20s off'; f.pid_lims = [-0.1 3];
%a_thisfile_name = '2023-10-10_datafile_01.csv'; a_this_note ='Ethyl Tiglate Pure - 8s on, 20s off'; %f.pid_lims = [-0.1 3];
%a_thisfile_name = '2023-10-10_datafile_02.csv'; a_this_note ='Ethyl Tiglate Pure - 8s on, 20s off'; f.pid_lims = [0 3];
%a_thisfile_name = '2023-10-10_datafile_03.csv'; a_this_note ='Ethyl Tiglate Pure - 15s on, 20s off'; f.pid_lims = [0 3];
%a_thisfile_name = '2023-10-11_datafile_00.csv'; a_this_note ='Ethyl Tiglate Pure - 15s on, 20s off'; f.pid_lims = [0 3];
%a_thisfile_name= '2023-10-17_olf21_datafile01.csv'; a_this_note = 'olf_21 vial 10: Ethyl Tiglate Pure - 8s on, 20s off';
%a_thisfile_name= '2023-10-17_olf62_datafile01.csv'; a_this_note = 'olfa_62 vial 5: Ethyl Tiglate Pure - 8s on, 20s off';
%a_thisfile_name= '2023-10-17_olf62_datafile02.csv'; a_this_note = 'olfa_62 vial 8: Ethyl Tiglate Pure - 8s on, 20s off';
%f.pid_lims = [0 3.3];
%a_thisfile_name= '2023-10-20_datafile00_acetophenone.csv'; a_this_note = 'Acetophenone vial 11 - 8s on, 20s off';
%f.pid_lims = [0 1.2];

%a_thisfile_name= '2023-11-06_datafile_00_ethyltiglate.csv'; a_this_note = 'Ethyl Tiglate vial 10 - 10s on, 30s off';
%a_thisfile_name= '2023-11-06_datafile_01_ethyltiglate.csv'; a_this_note = 'Ethyl Tiglate vial 10 - 10s on, 30s off';
%a_thisfile_name = '2023-11-06_datafile_02_ethyltiglate.csv'; a_this_note = 'Ethyl Tiglate vial 10 - 10s on, 30s off';
%a_thisfile_name = '2023-11-07_datafile_00_ethyltiglate_B.csv'; a_this_note = 'Ethyl Tiglate vial 9 - 10s on, 30s off';
%f.pid_lims = [0 3];

%a_thisfile_name = '2023-11-10_datafile_00_vialC'; a_this_note = 'Pinene vial 12 - 8s on, 20s off';
%a_thisfile_name = '2023-11-10_datafile_02_vialF'; a_this_note = 'Pinene vial 12 - 8s on, 20s off (no suction)';
%a_thisfile_name = '2023-11-13_datafile_00_v11_A'; a_this_note = 'Pinene vial 11 - 8s on, 20s off (suction on)';
%a_thisfile_name = '2023-11-13_datafile_01_v12_B'; a_this_note = 'Pinene vial 12 - 8s on, 20s off (suction on)';
%a_thisfile_name = '2023-11-13_datafile_02_v11_A'; a_this_note = 'Pinene vial 11 - 8s on, 20s off (suction off)';
a_thisfile_name = '2023-11-13_datafile_03_v12_B'; a_this_note = 'Pinene vial 12 - 8s on, 20s off (suction off)'; flow_inc = 20;

f.pid_lims = [0 8];
%c.time_to_cut = 2;
c.time_to_cut = 0;
plot_opts.individual_trials = 'no';

%% load file

% full directory for this file
dir_this_data_file = strcat(dir_data_files,a_thisfile_name);
a_thisfile = readcell(dir_this_data_file);
a_thisfile_name = erase(a_thisfile_name,'.csv');

%% cut out header stuff
% skip down to the third row
header_goes_til = 3;
a_raw_file = a_thisfile(header_goes_til:end,:);

% cut out the first column
a_raw_file = a_raw_file(:,2:end);

clearvars header_goes_til

%% get PID baseline value

% set baseline to zero
pid_values = a_raw_file(1,2:end);

% remove missing cells
last_index = length(pid_values);
while ismissing(pid_values{last_index})
    last_index = last_index - 1;
end
pid_values = pid_values(1:last_index);

% get pid adjustment value
pid_values = cell2mat(pid_values);
pid_adjustment_value = min(pid_values);

clearvars last*
%% smooth PID   % TODO maybe

%%
if strcmp(plot_opts.individual_trials,'yes'); close all; end

%% initialize data structures

d_olfa_data = [];   % TODO change to d_olfa_data_combined
d_olfa_data(1).flow_value = [];
d_olfa_data(1).pid_mean = [];
d_olfa_data(1).pid_std = [];
d_olfa_data(1).data = [];

%% calculate stuff
% for each trial (each row of the file)
for i=1:height(a_raw_file)
    sccm_value = a_raw_file(i,1);
    pid_values = a_raw_file(i,2:end);

    this_sccm_value = sccm_value{1};
    
    %% adjust PID
    % remove missing cells
    last_index = length(pid_values);
    while ismissing(pid_values{last_index})
        last_index = last_index - 1;
    end
    pid_values = pid_values(1:last_index);

    % make array of time values
    number_of_data = length(pid_values);
    last_time_value = number_of_data * c.nidaq_freq;
    last_time_value = last_time_value - c.nidaq_freq;
    time_data = 0:c.nidaq_freq:last_time_value;
    
    % shift the pid values up to 0
    pid_values = cell2mat(pid_values);
    pid_values = pid_values - pid_adjustment_value;

    pid_data = [];
    pid_data(:,1) = time_data;
    pid_data(:,2) = pid_values;
    
    %% calculate mean PID value

    % start at c.time_to_cut seconds into the trial
    idx_of_start_time = (c.time_to_cut/c.nidaq_freq) + 1;
    new_pid_data = pid_data(idx_of_start_time:end,:);
    
    % give it .5 seconds to get up there a little bit
    if (c.time_to_cut < 0.5)
        new_pid_data_1 = get_section_data(new_pid_data,.5,new_pid_data(end,1));
    else
        new_pid_data_1 = new_pid_data;
    end
    
    idx_below_threshold = find(new_pid_data_1(:,2) < 0.1,1);   % find where PID drops below 0.1
    time_below_threshold = new_pid_data_1(idx_below_threshold,1);
    if ~(idx_below_threshold == 1)
        % end time is 0.1s before PID drops below 0.1
        end_time = time_below_threshold - .1;
        end_idx = find(new_pid_data(:,1) <= end_time,1,'last');
    else
        % if PID started below 0.1 (aka this was a 0 sccm trial), just make it a 3 second trial
        end_time = 3;
        end_idx = find(new_pid_data(:,1) <= end_time,1);
        disp('this was a 0 sccm trial')
    end
    
    % get all the data for this period
    this_pid_data = new_pid_data(1:end_idx,:);
    
    % calculate the mean value
    mean_pid = mean(this_pid_data(:,2));
    std_pid = std(this_pid_data(:,2));
    
    %% plot this trial by itself
    if strcmp(plot_opts.individual_trials,'yes')
        f1 = figure(i+1); hold on;
        f1.Position = f.f_position;
        f1_subtitle = [num2str(this_sccm_value) ' sccm'];
        subtitle(f1_subtitle);
        title(a_thisfile_name)
        xlabel('Time (s)');
        ylabel('PID (V)');
        xlim([-.5 last_time_value])
        if ~isempty(f.pid_lims); ylim(f.pid_lims); end
        p = plot(time_data,pid_values);
        p.LineWidth = 2;
        p.Color = f.PID_color;
        
        % draw xlines
        if strcmp(plot_opts.x_lines,'yes')
            xline(this_pid_data(1,1));
            xline(end_time);
        end
    end
    
    %% add it to the data structure
    % reshape data
    d_time_data = reshape(time_data,length(time_data),1);
    d_pid_data = reshape(pid_values,length(pid_values),1);
    d_olfa_data(i).flow_value = this_sccm_value;
    d_olfa_data(i).pid_mean = mean_pid;
    d_olfa_data(i).pid_std = std_pid;
    d_olfa_data(i).data = [d_time_data d_pid_data];
    
end
clearvars -except a_* c d_olfa_data dir_* f flow_inc pid_adjustment_value plot_opts

%% sort the data structure (create d_olfa_data_sorted)
fieldName = 'flow_value';
fieldValues = {d_olfa_data.(fieldName)};
fieldValues = cell2mat(fieldValues);
[~,sortedIndices] = sort(fieldValues,'ascend');
d_olfa_data_sorted = d_olfa_data(sortedIndices);

%% initialize the combined data structure (create d_olfa_data_combined)
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

%% add shit to the combined data structure

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

%% save the data structure
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

%% spt char figure
f2 = figure; hold on;
legend('Location','northwest');
f2.Position = f.f2_position;
f2.NumberTitle = 'off';
f2.Name = a_thisfile_name;
\title(a_thisfile_name)
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

