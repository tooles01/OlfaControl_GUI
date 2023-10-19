%% plot file from olfa calibration

clear variables
close all
set(0,'DefaultTextInterpreter','none')
%#ok<*AGROW>
%#ok<*NASGU>

%% set up directories
% enter directory for this computer
%a_dir_OlfaEngDropbox = 'C:\Users\Admin\Dropbox (NYU Langone Health)\OlfactometerEngineeringGroup (2)';
a_dir_OlfaEngDropbox = 'C:\Users\SB13FLLT004\Dropbox (NYU Langone Health)\OlfactometerEngineeringGroup (2)';

a_dir_OlfaControlGUI = strcat(a_dir_OlfaEngDropbox,'\Control\a_software\OlfaControl_GUI');
dir_data_files = [a_dir_OlfaControlGUI '\result_files\standard olfa\'];

% make sure datafiles are on matlab path
addpath(genpath(dir_data_files));


%% display variables
a_this_note = '';

PID_color = [.4667 .6745 .1882];
f = struct();
f.pid_lims = [];
f.fig1_position = [960 210 780 686];
f.dot_size = 60;


plot_individual_trials = 'no';     % plot each trial by itself
plot_all_points = 'no';            % plot all the points on a single graph
plot_x_lines = 'no';        % x lines of where the mean was calculated from
plot_cheap_olfa = 'no';

%f_position = [166 210 1300 600];    % for PowerPoint
f_position = [166 210 650 600];    % for PowerPoint (1/2 size)

c = struct();   % struct containing all config variables
c.nidaq_freq = 0.01;  % collection frequency etc etc
c.start_time = 2.00;  % don't look at any data before this time


%% enter file name
%a_thisfile_name = '2023-10-02_datafile_00_shannon.csv';
%a_thisfile_name = '2023-10-04_datafile_00_standard_olfa.csv'; %a_this_note = '5s on, 5s off'; f.pid_lims = [-0.1 3.6];
%a_thisfile_name = '2023-10-04_datafile_01_standard_olfa.csv'; %a_this_note = '5s on, 5s off'; f.pid_lims = [-0.1 3.6];
%a_thisfile_name = '2023-10-04_datafile_02_standard_olfa.csv'; %a_this_note ='5s on, 10s off'; f.pid_lims = [-0.1 3.6];
%a_thisfile_name = '2023-10-04_datafile_03_standard_olfa.csv'; a_this_note ='10s on, 10s off'; f.pid_lims = [-0.1 3.6];
%a_thisfile_name = '2023-10-05_datafile_00_standard_olfa.csv'; a_this_note ='Ethyl Tiglate 10s on, 20s off'; f.pid_lims = [-0.1 3.6];
%plot_cheap_olfa = 'yes';

%a_thisfile_name = '2023-10-09_acetophenone.csv'; plot_all_points = 'yes';
%a_thisfile_name = '2023-10-09_mixed.csv';  plot_individual_trials = 'no'; plot_all_points = 'yes';
%a_thisfile_name = '2023-10-09_ethyl tiglate pure.csv'; a_this_note ='Ethyl Tiglate Pure - 8s on, 20s off'; f.pid_lims = [-0.1 3];
%a_thisfile_name = '2023-10-10_datafile_01.csv'; a_this_note ='Ethyl Tiglate Pure - 8s on, 20s off'; %f.pid_lims = [-0.1 3];
%a_thisfile_name = '2023-10-10_datafile_02.csv'; a_this_note ='Ethyl Tiglate Pure - 8s on, 20s off'; f.pid_lims = [0 3];
%a_thisfile_name = '2023-10-10_datafile_03.csv'; a_this_note ='Ethyl Tiglate Pure - 15s on, 20s off'; f.pid_lims = [0 3];
%a_thisfile_name = '2023-10-11_datafile_00.csv'; a_this_note ='Ethyl Tiglate Pure - 15s on, 20s off'; f.pid_lims = [0 3];
%c.start_time = 5;
a_thisfile_name= '2023-10-17_olf21_datafile01.csv'; a_this_note = 'olf_21 vial 10: Ethyl Tiglate Pure - 8s on, 20s off';
%a_thisfile_name= '2023-10-17_olf62_datafile01.csv'; a_this_note = 'olfa_62 vial 5: Ethyl Tiglate Pure - 8s on, 20s off';
%a_thisfile_name= '2023-10-17_olf62_datafile02.csv'; a_this_note = 'olfa_62 vial 8: Ethyl Tiglate Pure - 8s on, 20s off';
c.start_time = 5;
f.pid_lims = [0 3.3];

plot_all_points = 'no';
plot_individual_trials = 'no';
plot_x_lines = 'yes';


%% get file
thisfile = readcell(a_thisfile_name);

%% cut out header stuff
% skip down to the third row
header_goes_til = 3;
raw_file = thisfile(header_goes_til:end,:);

% cut out the first column
raw_file = raw_file(:,2:end);


%% create main figure
if strcmp(plot_all_points,'yes')
    figure(1); hold on;
    figTitle = a_thisfile_name;
    if ~strcmp(a_this_note, ''); figTitle = append(figTitle, ': ',  a_this_note); end
    title(figTitle)
    xlabel('Flow (sccm)')
    ylabel('PID (V)')
    xlim([0 100])
    if ~isempty(f.pid_lims); ylim(f.pid_lims); end
    fig1 = gcf;
    fig1.Position = f.fig1_position;
    %fig1.Position = [166 210 1300 600];    % for PowerPoint
end

standard_olfa_data = [];

%% plot each sccm value by itself
for i=1:height(raw_file)
    sccm_value = raw_file(i,1);
    pid_values = raw_file(i,2:end);

    this_sccm_value = sccm_value{1};
    
    %% adjust data
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
    pid_adjustment_value = min(pid_values);
    pid_values = pid_values - pid_adjustment_value;

    
    %% calculate mean PID value

    % start at 2 seconds into the trial
    %start_time = 2.00;  % don't look at any data before this
    idx_of_start_time = (c.start_time/c.nidaq_freq) + 1;
    new_time_data = time_data(idx_of_start_time:end);
    new_pid_data = pid_values(idx_of_start_time:end);

    % find where PID drops below 0.1
    idx_below_threshold = find(new_pid_data < 0.1,1);

    % as long as we're not starting out at a PID of 0.1 (aka this was a 0 sccm trial)
    if ~(idx_below_threshold == 1)
        % go back 0.25 seconds from that point
        end_idx = idx_below_threshold - (round(0.25/c.nidaq_freq));
    else
        % end index is 3 seconds later
        idx_of_3_sec_later = (3.0/c.nidaq_freq) + 1;
        end_idx = idx_of_3_sec_later;
    end
    
    % get all the data for this period
    this_time_data = new_time_data(1:end_idx);
    this_pid_data = new_pid_data(1:end_idx);

    % calculate the mean value
    mean_pid = mean(this_pid_data);
    
    %% plot this trial by itself
    if strcmp(plot_individual_trials,'yes')
        f1 = figure(i+1); hold on;
        f1.Position = f_position;
        f1_title = [num2str(sccm_value{1}) ' sccm'];
        subtitle(f1_title);
        title(a_thisfile_name)
        xlabel('Time (s)');
        ylabel('PID (V)');
        xlim([-.5 last_time_value])
        if ~isempty(f.pid_lims); ylim(f.pid_lims); end
        p = plot(time_data,pid_values);
        p.LineWidth = 2;
        p.Color = PID_color;
        
        % draw xlines
        if strcmp(plot_x_lines,'yes')
            xline(this_time_data(1));
            xline(this_time_data(end));
        end
    end
    
    %% add to figure 1
    if strcmp(plot_all_points,'yes')
        figure(1);
        x = this_sccm_value * (ones(1,length(this_pid_data)));
        s = scatter(x,this_pid_data,'filled');
        s.SizeData = 4;
    end    

    % save just the mean value
    this_pair = [this_sccm_value mean_pid];
    standard_olfa_data = [standard_olfa_data; this_pair]; 
    
end


%% manually plot cheap olfa data on top
f2 = figure; hold on; legend('Location','northwest');
f2.Position = [260 230 812 709];
f2.NumberTitle = 'off';
f2.Name = a_thisfile_name;
title(a_this_note);

xlabel('Flow (SCCM)')
ylabel("PID (V)");
if ~isempty(f.pid_lims); ylim(f.pid_lims); end
xlim([0 100]);

% 2023-10-05_datafile_00_cheap_olfa
%{
cheap_olfa_data = [100 2.3971
    90 1.8394
    80 1.5337
    70 1.3182
    60 1.1607
    50 .9504
    40 .7865
    30 .5580
    20 .3719
    10 .1779
    0 -.0073];
%}
% after removing the zero adjustment
cheap_olfa_data = [100 -1.0075
    90 -1.5651
    80 -1.8708
    70 -2.0864
    60 -2.2438
    50 -2.4541
    40 -2.6361
    30 -2.8465
    20 -3.0326
    10 -3.2266
    0 -3.4114];

cheap_olfa_adjusted(:,1) = cheap_olfa_data(:,1);
cheap_olfa_adjusted(:,2) = cheap_olfa_data(:,2) - pid_adjustment_value;

blue_color = [0 .4470 .7410];
green_color = PID_color;

if strcmp(plot_cheap_olfa,'yes')
    c = scatter(cheap_olfa_adjusted(:,1),cheap_olfa_adjusted(:,2),'filled');
    c.MarkerFaceColor = green_color;
    c.DisplayName = 'cheap olfa';
end

s = scatter(standard_olfa_data(:,1),standard_olfa_data(:,2),f.dot_size,'filled');
s.MarkerFaceColor = blue_color;
s.DisplayName = 'standard olfa';



