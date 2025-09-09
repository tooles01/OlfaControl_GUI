%Plot each sccm value , overlay all vials
%
%Required Input:
%   file_names  - cell array of file names to plot
%   a_title
%   a_subtitle
%
%Plot Options:
%   pid_lims            - Axis limits for PID
%   flow_lims           - Axis limits for Olfa flow
%   ctrl_lims           - Axis limits for Olfa ctrl
%
%   round_to
%   time_to_cut
%
%   plot_by_flow
%
%   fig_position
%   plot_error_bars
%   plot_by_vial
%   shorten_file_name
%
%   plot_flow
%   plot_ctrl
%   x_lim


%%
%#ok<*NASGU>
%#ok<*AGROW>
 
function a_plot_on_top(file_names,a_title,a_subtitle,plot_opts)

arguments
    file_names  (:,1) cell
    
    a_title     (1,1) string = ''
    %a_title     (1,:) char = ''
    a_subtitle  (1,1) string = ''

    % Axis Limits
    plot_opts.pid_lims          (1,:) double = [0 3]
    plot_opts.flow_lims         (1,:) double = [0 105]
    plot_opts.ctrl_lims         (1,:) double = [0 260]

    % Data Manipulation
    plot_opts.round_to          (1,:) double = 5    % When getting flow means from file, round to the nearest (for plotting by individual flow rates)
    plot_opts.time_to_cut       (1,:) double = 0
    
    % Additional Figures
    plot_opts.plot_by_flow      (1,1) string = 'no'     % Plot each flow rate individually
    % change to "plot all" bc this is confusing

    % Plot options
    plot_opts.fig_position      (1,:) double = [925 230 812 709]    % position for flow v. PID plot
    plot_opts.plot_error_bars   (1,1) string = 'yes'
    plot_opts.plot_by_vial      (1,1) string = 'yes'    % colors based on vial #
    plot_opts.shorten_file_name (1,1) string = 'yes'
    
    % For individual event plots
    plot_opts.plot_flow         (1,1) string = 'no'     % Show flow data on individual flow rate plots
    plot_opts.plot_ctrl         (1,1) string = 'no'     % Show ctrl data on individual flow rate plots; Show Flow v. Ctrl plot
    plot_opts.x_lim             (1,:) double = [-2 10]  % timescale for "by flow" plots
end

%%
set(0,'DefaultTextInterpreter','none')

%% Display Variables
f = struct();   % struct containing all figure variables
f.dot_size = 60;

%c = struct();
c.colors{1} = [0.6353   0.0784  0.1843];    % dark red
c.colors{2} = 'm';                          % magenta
c.colors{3} = [0.9294   0.6941  0.1255];    % orange
c.colors{4} = [0.4667   0.6745  0.1882];    % olive green
c.colors{5} = 'g';                          % green
c.colors{6} = 'r';                          % red
c.colors{7} = [0.3010   0.7450  0.9330];    % light blue
c.colors{8} = [0.4940   0.1840  0.5560];    % purple

colors = lines(7);      % MATLAB's default "lines" color order

c.flow_color = [0 .447 .741];
c.flow_width = 1.5;
c.pid_width = 2;
c.blue = [0 .447 .741];
c.yellow = [.929 .694 .125];
c.nidaq_freq = 0.01;    % collection frequency etc etc

% Figure positions

% F1: Individual flow plots

%f.f1_position = [166 210 1300 600];    % for PowerPoint
f.f1_position = [28 210 881 600];

% F2: Flow v. PID
%f.f2_position = [260 210 650 600];      % for PowerPoint (1/2 size)
f.f2_position = plot_opts.fig_position;

% F3: Flow v. Ctrl
f.f3_position = [1000 224 812 709];     % for PowerPoint (spt char)
%f.f3_position = [1000 210 650 600];     % for PowerPoint (1/2 size)

%% Find OlfaControl_GUI directory (& add to path)

% Check if current directory contains 'OlfaControl_GUI'
c_current_dir = pwd;
c_str_to_find = 'OlfaControl_GUI';
c_idx_of_str = strfind(c_current_dir,c_str_to_find);
c_len_of_strToFind = length(c_str_to_find);
if isempty(c_idx_of_str); disp([c_str_to_find ' is not within current directory.']); end    % If not, whole thing will fail (i don't feel like writing another try except statement rn)

% Get full path to 'OlfaControl_GUI' folder
a_dir_OlfaControlGUI = c_current_dir(1:c_idx_of_str+c_len_of_strToFind-1);

% Make sure datafiles are on matlab path
dir_data_files = [a_dir_OlfaControlGUI '\analysis\data (.mat files)\'];
addpath(genpath(dir_data_files));   % genpath gets all folders/subfolders from 48-line olfa, addpath adds them to the top of the search path for the current session
% Make sure functions are on matlab path
dir_functions = [a_dir_OlfaControlGUI '\analysis\functions'];
addpath(genpath(dir_functions));

clearvars c_* dir_functions

%% Load *.mat files

% Preallocate array
d = struct('file_name','', ...
    'd_olfa_data_combined','', ...
    'd_olfa_flow','', ...
    'data_pid','');
data(length(file_names)) = d;

% Load files in
for i=1:length(file_names)
    a_this_file_name = file_names{i};
    data(i).file_name = a_this_file_name;
    a_this_full_file_name = [dir_data_files '\' a_this_file_name];
    warning('off','MATLAB:load:variableNotFound'); % ignore warnings about variable not found for standard olfa
    a = load(a_this_file_name,'d_olfa_data_combined','d_olfa_flow','data_pid','d_olfa_data_sorted','vial_number');
    data(i).d_olfa_data_combined = a.d_olfa_data_combined;
    data(i).d_olfa_data_sorted = a.d_olfa_data_sorted;
    data(i).color = [];
    
    % Get vial number
    try
        this_vial_number = a.vial_number{:} - 4;                % standard olf (convert it to 1-8)
    catch ME
        this_vial_number = str2num(a.d_olfa_flow.vial_num(2));  % 8channel olf
    end
    data(i).vial_number = this_vial_number;

    % In case there are standard olfa files
    try
        data(i).d_olfa_flow = a.d_olfa_flow;
        data(i).data_pid = a.data_pid;
    catch ME
        switch ME.identifier
            case 'MATLAB:nonExistentField'
                % this is a standard olfa file, just carry on
                x=1;
            otherwise
                rethrow(ME)
        end
    end
    
    % Assign a color to each file
    if strcmp(plot_opts.plot_by_vial,'yes')
        % assign based on vial number
        thisfile_color = c.colors{this_vial_number};
    end

    if strcmp(plot_opts.plot_by_vial,'no')
        if i==1
            % this is the first file: use the first color
            thisfile_color = colors(1,:);
            %thisfile_color = c.colors{1};
        else
            % check which colors are in use, pick something different
            colors_in_use = vertcat(data(1:i-1).color);
            %idx = find(~ismember(c.colors, colors_in_use, 'rows'), 1);
            idx = find(~ismember(colors, colors_in_use, 'rows'), 1);
            %thisfile_color = c.colors(idx,:);
            thisfile_color = colors(idx,:);
        end
    end
    data(i).color = thisfile_color;
end

clearvars x

%% Get list of flow values recorded in these files
flow_values = [];

% For each file
for r=1:length(data)
    %{
    a_this_file_name = data(r).file_name;
    shortened_file_name = extractAfter(a_this_file_name,11);
    shortened_file_name = erase(shortened_file_name,'.mat');
    %}
    
    % For each vial % --> fix this later, there should only be one vial in each file (and also this loop doesn't even account for multiple vials) - ST 3/18/25
    for j=1:length(data(r).d_olfa_flow)
        % Get the data from d_olfa_data_sorted
        this_file_flow_values = [data(r).d_olfa_data_sorted.flow_mean_sccm];
        this_file_flow_values = round(this_file_flow_values/plot_opts.round_to)*plot_opts.round_to;   % round to the nearest five
        this_file_flow_values = reshape(this_file_flow_values,length(this_file_flow_values),1);
        
        flow_values = [flow_values;this_file_flow_values];
    end
    
    % If it was a standard olfa file
    if isempty(data(r).d_olfa_flow)
        this_file_flow_values = [data(r).d_olfa_data_sorted.flow_value];
        this_file_flow_values = round(this_file_flow_values/plot_opts.round_to)*plot_opts.round_to;   % round to the nearest five
        this_file_flow_values = reshape(this_file_flow_values,length(this_file_flow_values),1);
        
        flow_values = [flow_values;this_file_flow_values];
    end
end

flow_values = sort(flow_values);        % sort the list
flow_values = unique(flow_values);      % remove duplicate values

clearvars r

%% Plot each flow value separately
if strcmp(plot_opts.plot_by_flow,'yes')
    
    % For each flow value
    for i=1:length(flow_values)
        this_flow_value = flow_values(i);

        %% Create figure
        f_0 = figure; hold on; f_0.Position = f.f1_position; legend('Interpreter','none');
        f_0.NumberTitle = 'off';
        f_0.Name = a_subtitle + " (" + this_flow_value + " sccm)";
        xlabel('Time (s)');
        this_flow_value = flow_values(i);
        title([num2str(this_flow_value) ' SCCM'])
        
        %% For each file
        for r=1:length(data)
            
            % Shorten file name (for legend)
            a_this_file_name = data(r).file_name;
            shortened_file_name = extractAfter(a_this_file_name,11);
            shortened_file_name = erase(shortened_file_name,'.mat');
            
            %% 8-line olfa
            % For each vial
            for j=1:length(data(r).d_olfa_flow)
                
                % Get all of the flow values we ran trials at
                this_file_flow_values = [data(r).d_olfa_data_sorted.flow_mean_sccm];
                this_file_flow_values = round(this_file_flow_values/plot_opts.round_to)*plot_opts.round_to;   % round to the nearest five
                this_file_flow_values = reshape(this_file_flow_values,length(this_file_flow_values),1);

                % Get indices of where this flow value is
                indices = find(ismember(this_file_flow_values,this_flow_value));
                
                % As long as shit didn't hit the fan
                if ~isempty(indices)
                    %% For each trial at this flow value
                    for k=1:length(indices)
                        this_idx = indices(k);

                        %% Get the data
                        this_vial_num = data(r).d_olfa_flow(j).vial_num;
                        this_flow_data = data(r).d_olfa_flow(j).flow.flow_sccm;
                        this_ctrl_data = data(r).d_olfa_flow(j).ctrl.ctrl_int;
                        this_pid_data = data(r).data_pid;

                        %% Shift all of this data to t=0
                        % if there are events for this vial
                        if ~isempty(data(r).d_olfa_flow(j).events.OV_keep)
                            % find the event that's closest to the first flow time
                            t_event_start_times = [data(r).d_olfa_flow(j).events.OV_keep.t_event];      % all event start times
                            t_flow_start = data(r).d_olfa_data_sorted(this_idx).data.flow_sccm(1,1);    % time of first value recorded (in this event)
                            % find the actual start time of this event
                            [val,idx] = min(abs(t_event_start_times-t_flow_start));                     % idx of the event closest to this time
                            this_t_event = data(r).d_olfa_flow(j).events.OV_keep(idx).t_event;          % actual event start time
    
                            % Shift the data to t=0
                            this_flow_data(:,1) = this_flow_data(:,1) - this_t_event;
                            this_ctrl_data(:,1) = this_ctrl_data(:,1) - this_t_event;
                            this_pid_data(:,1) = this_pid_data(:,1) - this_t_event;
                            
                            %% Plot ctrl
                            if strcmp(plot_opts.plot_ctrl,'yes')    % TODO: if plot_flow = yes, don't plot ctrl values
                                yyaxis left; ylabel('Ctrl (integer)');
                                ylim([plot_opts.ctrl_lims]);
                                p_ctrl = plot(this_ctrl_data(:,1),this_ctrl_data(:,2));
                                p_ctrl.HandleVisibility = 'off';
                                if strcmp(plot_opts.plot_by_vial,'yes')
                                    vial_num = str2double(this_vial_num(2));
                                    p_ctrl.Color = c.colors{vial_num};
                                else
                                    p_ctrl.Color = c.colors{r};
                                end
                                p_ctrl.LineStyle = '-';
                                p_ctrl.Marker = 'none';
                            end
                            %% Plot flow
                            if strcmp(plot_opts.plot_flow,'yes')
                                yyaxis left; ylabel('Odor flow rate (SCCM)')
                                ylim([plot_opts.flow_lims])
                                p_flow = plot(this_flow_data(:,1),this_flow_data(:,2));
                                p_flow.HandleVisibility = 'off';
                                p_flow.Color = data(r).color;
                                p_flow.LineWidth = c.flow_width;
                                p_flow.LineStyle = '-';
                                p_flow.Marker = 'none';
                            end
    
                            %% Plot PID
                            if ~(strcmp(plot_opts.plot_ctrl,'no') && strcmp(plot_opts.plot_flow,'no'))      % If either flow or ctrl are plotted, put PID on the right yaxis
                                yyaxis right;
                            end
                            ylabel('PID reading (V)')
                            ylim([plot_opts.pid_lims]);
                            r_ax = gca; r_ax.YColor = 'k';
                            p_pid = plot(this_pid_data(:,1),this_pid_data(:,2));
                            if strcmp(plot_opts.shorten_file_name,'yes')
                                p_pid.DisplayName = this_vial_num + " " + shortened_file_name;
                            else
                                p_pid.DisplayName = this_vial_num + " " + a_this_file_name;
                            end
                            if (k>1); p_pid.HandleVisibility = 'off'; end
                            p_pid.Color = data(r).color;
                            p_pid.LineWidth = c.pid_width;
                            p_pid.LineStyle = '-';
                            p_pid.Marker = 'none';
                            
                            xlim(plot_opts.x_lim);
                        else
                            disp('no events for this vial')
                        end
                    end
                end
            end

            %% Standard olfa
            if isempty(data(r).d_olfa_flow)

                % Get all of the flow values we ran trials at
                this_file_flow_values = [data(r).d_olfa_data_sorted.flow_value];
                this_file_flow_values = reshape(this_file_flow_values,length(this_file_flow_values),1);
                
                % Get indices of where this flow value is
                indices = find(ismember(this_file_flow_values,this_flow_value));

                % As long as shit didn't hit the fan
                if ~isempty(indices)
                    %% For each trial at this flow value
                    for j=1:length(indices)
                        this_idx = indices(j);
                        
                        % Get the PID data
                        this_pid_data = data(r).d_olfa_data_sorted(this_idx).data;

                        %% Plot PID
                        if ~(strcmp(plot_opts.plot_ctrl,'no') && strcmp(plot_opts.plot_flow,'no'))
                            yyaxis right;
                        end
                        ylabel('PID reading (V)')
                        ylim([plot_opts.pid_lims]);
                        r_ax = gca; r_ax.YColor = 'k';
                        p_pid = plot(this_pid_data(:,1),this_pid_data(:,2));
                        if strcmp(plot_opts.shorten_file_name,'yes')
                            p_pid.DisplayName = shortened_file_name;
                        else
                            p_pid.DisplayName = a_this_file_name;
                        end
                        p_pid.Color = data(r).color;
                        p_pid.LineWidth = c.pid_width;
                        p_pid.LineStyle = '-';
                        p_pid.Marker = 'none';
                        if (j>1); p_pid.HandleVisibility = 'off'; end
                        
                        xlim(plot_opts.x_lim);
                    end
                end
            end
        
        end
    end
end
clearvars -except a_* c plot_opts f data

%% Set up plots
% F2: Flow v. PID
f2 = figure; hold on;
f2.Name = 'FLOW v. PID';
f2.Position = f.f2_position;
ax2 = gca;
legend('Location','northwest','Interpreter','none');
xlabel('Odor flow rate (SCCM)')
xlim(plot_opts.flow_lims)
ylabel('Mean PID reading (V)')
if ~isempty(plot_opts.pid_lims); ylim(plot_opts.pid_lims); end
%ylim(plot_opts.pid_lims)
title(a_title);
if ~isempty(a_subtitle); subtitle(a_subtitle); end

% F3: Flow v. ctrl
if strcmp(plot_opts.plot_ctrl,'yes')
    f3 = figure; hold on;
    f3.Position = f.f3_position;
    f3.Name = 'FLOW v. CTRL: ';
    ax3 = gca;
    legend('Location','northwest','Interpreter','none');
    xlabel('Odor flow rate (SCCM)')
    xlim(plot_opts.flow_lims)
    ylabel('Ctrl (integer)')
    if ~isempty(plot_opts.ctrl_lims); ylim(plot_opts.ctrl_lims); end
    title(a_title);
    if ~isempty(a_subtitle); subtitle(a_subtitle); end
end

%% Plot Flow v. PID for each file
% For each file
for r=1:length(data)
    a_this_file_name = data(r).file_name;
    shortened_file_name = extractAfter(a_this_file_name,11);
    shortened_file_name = erase(shortened_file_name,'.mat');

    %% 8-line olfa
    if ~isempty(data(r).d_olfa_flow)
        % For each vial
        for i=1:length(data(r).d_olfa_flow)
            
            % Get the mean flow & PID, after cutting plot_opts.time_to_cut

            this_vial_num = data(r).d_olfa_flow(i).vial_num;
            this_file_events = data(r).d_olfa_flow(i).events.OV_keep;
            
            % Initialize empty data structures
            this_file_new_means = [];
            this_file_new_stds = [];
            this_file_ctrl_means = [];
            this_file_ctrl_stds = [];

            %% For each event: Cut data & calculate stats, add into main data structure: data(r).new_means
            for e=1:length(this_file_events)
                this_event_start_time = this_file_events(e).t_event;
                this_event_end_time = this_file_events(e).t_end;
                this_event_cut_t_start = this_event_start_time + plot_opts.time_to_cut;
                this_event_cut_t_end = this_event_end_time;
                
                % Get data from this event
                this_event_flow_data = this_file_events(e).data.flow_sccm;
                this_event_pid_data = this_file_events(e).data.pid;
                this_event_ctrl_data = data(r).d_olfa_flow(i).ctrl.ctrl_int;
                
                % Cut off the first plot_opts.time_to_cut seconds
                this_event_cut_flow_data = get_section_data(this_event_flow_data,this_event_cut_t_start,this_event_cut_t_end);
                this_event_cut_pid_data = get_section_data(this_event_pid_data,this_event_cut_t_start,this_event_cut_t_end);
                this_event_cut_ctrl_data = get_section_data(this_event_ctrl_data,this_event_cut_t_start,this_event_cut_t_end);

                % Calculate means
                this_event_flow_mean = mean(this_event_cut_flow_data(:,2));
                this_event_pid_mean = mean(this_event_cut_pid_data(:,2));
                this_event_ctrl_mean = mean(this_event_cut_ctrl_data(:,2));

                % Calculate standard deviations
                this_event_flow_std = std(this_event_cut_flow_data(:,2));
                this_event_pid_std = std(this_event_cut_pid_data(:,2));
                this_event_ctrl_std = std(this_event_cut_ctrl_data(:,2));

                % Add to data structure (all means/stds for this file)
                if this_event_flow_mean > .1
                %if this_event_flow_mean ~= 0    % JUST FOR THIS ONE TIME 11/1/2023 SINCE GUI BEING DUMB % IF YOU'RE DOING ZERO FLOW TRIALS THEN GET RID OF THIS
                    this_event_mean_pair = [this_event_flow_mean this_event_pid_mean];      % Flow mean, PID mean
                    this_event_std_pair = [this_event_flow_std this_event_pid_std];         % Flow std, PID std
                    this_file_new_means = [this_file_new_means;this_event_mean_pair];       % Array of Flow mean, PID mean (for all trials)
                    this_file_new_stds = [this_file_new_stds;this_event_std_pair];          % Array of Flow std, PID std (for all trials)
                    this_file_ctrl_means = [this_file_ctrl_means;this_event_ctrl_mean];     % Array of Ctrl mean (for all trials)
                    this_file_ctrl_stds = [this_file_ctrl_stds;this_event_ctrl_std];        % Array of Ctrl std (for all trials)
                end
            end
            clearvars this_event*
            
            %% Add flow/PID means to the big data struct
            data(r).new_means = this_file_new_means;    % Array of Flow mean, PID mean (for all trials)
            
            %% Plot Flow v. PID means (f2)
            x_flow = [];
            if ~isempty(this_file_new_means)
                x_flow = this_file_new_means(:,1);
                y_pid = this_file_new_means(:,2);
                s = scatter(ax2,x_flow,y_pid,f.dot_size,'filled');
                if strcmp(plot_opts.shorten_file_name,'yes'); s.DisplayName = this_vial_num + " " + shortened_file_name;
                else; s.DisplayName = this_vial_num + " " + a_this_file_name; end
                s.MarkerFaceColor = data(r).color;
            end
        
            %% Plot Flow v. Ctrl means (f3)
            if ~isempty(this_file_ctrl_means)
                if strcmp(plot_opts.plot_ctrl,'yes')
                    y_ctrl = this_file_ctrl_means;
                    s2 = scatter(ax3,x_flow,y_ctrl,f.dot_size,'filled');
                    if strcmp(plot_opts.shorten_file_name,'yes'); s2.DisplayName = this_vial_num + " " + shortened_file_name;
                    else; s2.DisplayName = this_vial_num + " " + a_this_file_name; end
                    s2.MarkerFaceColor = data(r).color;
                end
            end
            
            %% Plot error bars
            if ~isempty(x_flow)
                if strcmp(plot_opts.plot_error_bars,'yes')
                    
                    % Initialize empty data structures
                    xneg = zeros(length(this_file_new_stds),1);
                    xpos = zeros(length(this_file_new_stds),1);
                    yneg = zeros(length(this_file_new_stds),1);
                    ypos = zeros(length(this_file_new_stds),1);
                    yneg_ctrl = zeros(length(this_file_new_stds),1);
                    ypos_ctrl = zeros(length(this_file_new_stds),1);
                    
                    % For each event
                    for e=1:height(this_file_new_stds)
                        % Create array of values to plot as the error bars
                        % xneg and xpos will be 1/2 the std dev at each point
                        flow_std = this_file_new_stds(e,1);
                        pid_std = this_file_new_stds(e,2);
                        ctrl_std = this_file_ctrl_stds(e);
                        xneg(e,1) = flow_std/2;
                        xpos(e,1) = flow_std/2;
                        yneg(e,1) = pid_std/2;
                        ypos(e,1) = pid_std/2;
                        yneg_ctrl(e,1) = ctrl_std/2;
                        ypos_ctrl(e,1) = ctrl_std/2;
                    end
                    
                    % Plot Flow v. PID error bars
                    e = errorbar(ax2,x_flow,y_pid,yneg,ypos,xneg,xpos,'o');
                    e.HandleVisibility = 'off';
                    try e.Color = s.MarkerFaceColor;
                    catch ME; e.Color = s.CData; end
                    
                    % Plot Flow v. Ctrl error bars
                    if strcmp(plot_opts.plot_ctrl,'yes')
                        e_ctrl = errorbar(ax3,x_flow,y_ctrl,yneg_ctrl,ypos_ctrl,xneg,xpos,'o');
                        e_ctrl.HandleVisibility = 'off';
                        try e_ctrl.Color = s2.MarkerFaceColor;
                        catch ME; e_ctrl.Color = s2.CData; end
                    end
                end
            end
        end
    
    %% Standard olfa
    else
        this_file_new_means = [];
        this_file_new_stds = [];
        
        this_file_events = data(r).d_olfa_data_sorted;
        %% For each trial
        for e=1:length(this_file_events)
            
            this_event_flow_mean = this_file_events(e).flow_value;
            this_event_flow_std = 0;
            
            % Get the mean PID, after cutting plot_opts.time_to_cut
            this_event_start_time = this_file_events(e).data(1,1);
            this_event_end_time = this_file_events(e).data(end,1);
            this_event_cut_t_start = this_event_start_time + plot_opts.time_to_cut;
            
            this_event_pid_data = this_file_events(e).data;
            
            %% Calculate mean PID value

            % Get the section of PID values we will use to calculate the mean

            % 1) Make sure we cut at least 2 seconds from the beginning of the trial
            % Get data starting at plot_opts.time_to_cut seconds into the trial
            idx_of_start_time = (plot_opts.time_to_cut/c.nidaq_freq) + 1;   % Index of plot_opts.time_to_cut seconds
            new_pid_data = this_event_pid_data(idx_of_start_time:end,:);
            
            % Cut off 2 seconds anyways (to let it get up there a little bit)
            if (plot_opts.time_to_cut < 2)
                new_pid_data_1 = get_section_data(new_pid_data,2,new_pid_data(end,1));
            else
                new_pid_data_1 = new_pid_data;
            end
            
            % 2. Find time when vial closed: cut everything after that
            % (from the cut data) Find what time the PID drops below threshold (10% of max value during the trial) (this is based on nothing besides my own visualization)
            PID_end_threshold = .1*(max(this_event_pid_data(:,2)));   % 10% of the max value
            idx_below_threshold = find(new_pid_data_1(:,2) < PID_end_threshold,1);  % index of first time PID drops below threshold
            time_below_threshold = new_pid_data_1(idx_below_threshold,1);           % first time PID drops below threshold
    
            % Get the time value 0.1s before it drops
            % If this was a normal trial: make the end time 0.1s before the PID drops below threshold
            if ~(idx_below_threshold == 1)
                end_time = time_below_threshold - .1;
            % If PID started below 0.1V (aka this was a 0 sccm trial), just make it a 4 second trial
            else
                end_time = 4;
                str = ['this was a 0 sccm trial (', num2str(this_event_flow_mean),' sccm, e=', num2str(e), ', ',a_this_file_name, ')'];
                disp(str)
            end
            end_idx = find(new_pid_data_1(:,1) <= end_time,1,'last');     % Index of where end_time happens

            % Get all the data for this period (calculated time of the event)
            this_event_cut_pid_data = new_pid_data_1(1:end_idx,:);
            
            % Calculate the mean/std
            this_event_pid_mean = mean(this_event_cut_pid_data(:,2));
            this_event_pid_std = std(this_event_cut_pid_data(:,2));

            %% Add to new structure
            this_event_mean_pair = [this_event_flow_mean this_event_pid_mean];
            this_event_std_pair = [this_event_flow_std this_event_pid_std];
            this_file_new_means = [this_file_new_means;this_event_mean_pair];
            this_file_new_stds = [this_file_new_stds;this_event_std_pair];
        end
        clearvars this_event*
        %% Add means to the big data struct
        data(r).new_means = this_file_new_means;
        
        %% Add this to the plot
        x_flow = [];
        if ~isempty(this_file_new_means)
            x_flow = this_file_new_means(:,1);
            y_pid = this_file_new_means(:,2);
            s_standard = scatter(ax2,x_flow,y_pid,f.dot_size,'filled');
            if strcmp(plot_opts.shorten_file_name,'yes')
                s_standard.DisplayName =  "standard olfa: " + shortened_file_name;
            else
                s_standard.DisplayName =  "standard olfa: " + a_this_file_name;
            end
            s_standard.MarkerFaceColor = data(r).color;
            s_standard.MarkerEdgeColor = data(r).color;
        end

        %% Plot error bars
        if ~isempty(x_flow)
            if strcmp(plot_opts.plot_error_bars,'yes')
                xneg = zeros(length(this_file_new_stds),1);
                xpos = zeros(length(this_file_new_stds),1);
                yneg = zeros(length(this_file_new_stds),1);
                ypos = zeros(length(this_file_new_stds),1);
                % For each event
                for e=1:height(this_file_new_stds)
                    % xneg and xpos will be 1/2 the std dev at each point
                    flow_std = this_file_new_stds(e,1);
                    pid_std = this_file_new_stds(e,2);
                    xneg(e,1) = flow_std/2;
                    xpos(e,1) = flow_std/2;
                    yneg(e,1) = pid_std/2;
                    ypos(e,1) = pid_std/2;
                end
                e = errorbar(ax2,x_flow,y_pid,yneg,ypos,xneg,xpos,'o');
                e.HandleVisibility = 'off';
                e.Color = data(r).color;
            end
        end
    
    end
end

clearvars -except a_* c f data
