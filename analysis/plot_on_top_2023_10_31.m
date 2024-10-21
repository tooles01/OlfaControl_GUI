%Plot each sccm value , overlay all vials

%%
clear variables
set(0,'DefaultTextInterpreter','none')
%#ok<*NASGU>
%#ok<*AGROW>

%% Display variables
% TODO combine display variables and plot options - 10/21/24
a_title = '';
a_subtitle = '';

f = struct();   % struct containing all figure variables

f.x_lim = [-2 30];  % for individual plots
f.x_lim = [-2 10];

c = struct();
%{
%c.colors{1} = '#A2142F';
%c.colors{2} = '#77AC30';
%c.colors{3} = '#EDB120';
%c.colors{4} = 'm';
%c.colors{1} = [162 20 47];
%c.colors{2} = [119 172 48];
%c.colors{3} = [237 177 32];
%}
c.colors{1} = [0.6353   0.0784  0.1843];    % dark red
c.colors{2} = 'm';                          % magenta
c.colors{3} = [0.9294   0.6941  0.1255];    % orange
c.colors{4} = [0.4667   0.6745  0.1882];    % olive green
c.colors{5} = 'g';                          % green
c.colors{6} = 'r';                          % red
c.colors{7} = [0.3010   0.7450  0.9330];    % light blue
c.colors{8} = [0.4940   0.1840  0.5560];    % purple

c.flow_color = [0 .447 .741];
c.flow_width = 0.1;
c.pid_width = 2;
c.blue = [0 .447 .741];
c.yellow = [.929 .694 .125];
c.nidaq_freq = 0.01;    % collection frequency etc etc


% Figure positions

% F1: Individual flow plots
%f.f1_position = [166 210 1300 600];    % for PowerPoint
f.f1_position = [28 210 1300 600];

% F2: Flow v. PID
%f.f2_position = [260 210 650 600];      % for PowerPoint (1/2 size)
f.f2_position = [260 230 812 709];      % for PowerPoint (spt char)

% F3: Flow v. Ctrl
%f.f3_position = [1000 224 812 709];     % for PowerPoint (spt char)
f.f3_position = [1000 210 650 600];     % for PowerPoint (1/2 size)


%% Plot options
% Axis Limits
c.pid_lims = [0 5];
c.flow_lims = [0 105];
c.ctrl_lims = [0 260];

% Data Manipulation
c.round_to = 5;         % When getting flow means from file, round to the nearest (for plotting by individual flow rates)

c.time_to_cut = 6;

% Plot options
c.plot_by_flow = 'yes';     % plot each flow rate individually
c.plot_flow = 'yes';    % Plot flow values on left yaxis (8line olf)
c.plot_ctrl = 'no';     % Plot ctrl values on left yaxis (8line olf)

c.plot_error_bars = 'yes';
c.plot_by_vial = 'yes';      % colors based on vial #

% Data to show on plot
c.shorten_file_name = 'no';

%% Get datafile names
%a_files_to_plot;
%files__plot_on_top_2023_10_31;

% test: 10/09/2024
%{
file_names = {
    '2023-11-06_datafile_03'    % E1
    '2023-11-06_datafile_04'    % E3
    '2023-11-06_datafile_05'    % E4
    '2023-11-06_datafile_02_ethyltiglate'};
%c.plot_by_flow = 'yes';
c.plot_ctrl = 'no';
c.plot_flow = 'yes';
%}

%{
% 10/14/2024
file_names = {
    '2024-10-14_datafile_02'
    '2024-10-14_datafile_03'
    '2024-10-14_datafile_06'
    '2024-10-14_datafile_07'
    '2024-10-14_datafile_08'
    };
% when you plot just these two on top of each other, it seemed like 08 struggled more with PID
% so: try and keep pressure as low as possible
% (this could also just be coincidence because only two trials but idk)
file_names = {
    '2024-10-14_datafile_06'
    '2024-10-14_datafile_07'
    '2024-10-14_datafile_08'
    };
%c.plot_by_vial = 'no';
%c.plot_flow = 'no';
c.plot_ctrl = 'no';
c.pid_lims = [-.05 1];

% 10/16/2024
file_names = {
    '2023-11-06_datafile_03'    % E1
    '2023-11-06_datafile_04'    % E3
    '2023-11-06_datafile_05'    % E4
    };
c.pid_lims = [0 3.5];


a_title = '01-11-2024';
a_subtitle = 'Pinene (old vials)';
file_names = {
    '2024-01-11_datafile_00'    % A1
    '2024-01-11_datafile_10'
    '2024-01-11_datafile_01'    % A2
    '2024-01-11_datafile_02'    % A3
    '2024-01-11_datafile_11'
    '2024-01-11_datafile_03'    % A4
    };
c.pid_lims = [0 10.5];
%}


a_subtitle = 'Ethyl Tiglate (old vials)';
file_names = {
    '2024-01-11_datafile_04'    % A5
    '2024-01-11_datafile_09'
    '2024-01-11_datafile_05'    % A6
    '2024-01-11_datafile_06'    % A7
    '2024-01-11_datafile_07'    % A8
    '2024-01-11_datafile_08'
    };
c.pid_lims = [0 3];

c.plot_by_flow = 'no';
c.plot_by_vial = 'yes';
%{
a_title = '01-18-2024';
a_subtitle = 'Pinene';
file_names = {
    '2024-01-18_datafile_00'    % A1
    '2024-01-18_datafile_01'    % A2
    '2024-01-18_datafile_04'
    '2024-01-18_datafile_02'    % A3
    '2024-01-18_datafile_03'    % A4
    };
c.pid_lims = [0 7];
%c.plot_by_vial = 'no';

%}



%% Preallocate array
d = struct('file_name','', ...
    'd_olfa_data_combined','', ...
    'd_olfa_flow','', ...
    'data_pid','');
data(length(file_names)) = d;

%% Load these files into the array
for i=1:length(file_names)
    a_this_file_name = file_names{i};
    data(i).file_name = a_this_file_name;
    a = load(a_this_file_name,'d_olfa_data_combined','d_olfa_flow','data_pid','d_olfa_data_sorted');
    data(i).d_olfa_data_combined = a.d_olfa_data_combined;
    data(i).d_olfa_data_sorted = a.d_olfa_data_sorted;
    
    % In case there are standard olfa files
    try
        data(i).d_olfa_flow = a.d_olfa_flow;
        data(i).data_pid = a.data_pid;
    catch ME
        switch ME.identifier
            case 'MATLAB:nonExistentField'
                % this is a standard olfa file
                x=1;
            otherwise
                rethrow(ME)
        end
    end
end

flow_values = [];

%% Get list of flow values recorded in these files


% For each file
for r=1:length(data)
    %{
    a_this_file_name = data(r).file_name;
    shortened_file_name = extractAfter(a_this_file_name,11);
    shortened_file_name = erase(shortened_file_name,'.mat');
    %}
    
    % For each vial
    for j=1:length(data(r).d_olfa_flow)
        % Get the data from d_olfa_data_sorted
        this_file_flow_values = [data(r).d_olfa_data_sorted.flow_mean_sccm];
        this_file_flow_values = round(this_file_flow_values/c.round_to)*c.round_to;   % round to the nearest five
        this_file_flow_values = reshape(this_file_flow_values,length(this_file_flow_values),1);
        
        flow_values = [flow_values;this_file_flow_values];
    end
    
    % If it was a standard olfa file
    if isempty(data(r).d_olfa_flow)
        this_file_flow_values = [data(r).d_olfa_data_sorted.flow_value];
        this_file_flow_values = round(this_file_flow_values/c.round_to)*c.round_to;   % round to the nearest five
        this_file_flow_values = reshape(this_file_flow_values,length(this_file_flow_values),1);
        
        flow_values = [flow_values;this_file_flow_values];
    end
end

flow_values = sort(flow_values);        % sort the list
flow_values = unique(flow_values);      % remove duplicate values


%% Plot each flow value separately
if strcmp(c.plot_by_flow,'yes')
    
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
                this_file_flow_values = round(this_file_flow_values/c.round_to)*c.round_to;   % round to the nearest five
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
                        if strcmp(c.plot_ctrl,'yes')    % TODO: if plot_flow = yes, don't plot ctrl values
                            yyaxis left; ylabel('Ctrl (int)');
                            ylim([c.ctrl_lims]);
                            p_ctrl = plot(this_ctrl_data(:,1),this_ctrl_data(:,2));
                            p_ctrl.HandleVisibility = 'off';
                            if strcmp(c.plot_by_vial,'yes')
                                vial_num = str2double(this_vial_num(2));
                                p_ctrl.Color = c.colors{vial_num};
                            else
                                p_ctrl.Color = c.colors{r};
                            end
                            p_ctrl.LineStyle = '-';
                            p_ctrl.Marker = 'none';
                        end
                        %% Plot flow
                        if strcmp(c.plot_flow,'yes')
                            yyaxis left; ylabel('Flow (SCCM)')
                            ylim([c.flow_lims])
                            p_flow = plot(this_flow_data(:,1),this_flow_data(:,2));
                            p_flow.HandleVisibility = 'off';
                            p_flow.Color = c.flow_color;
                            p_flow.LineWidth = c.flow_width;
                            p_flow.LineStyle = '-';
                            p_flow.Marker = 'none';
                        end

                        %% Plot PID
                        if ~(strcmp(c.plot_ctrl,'no') && strcmp(c.plot_flow,'no'))      % If either flow or ctrl are plotted, put PID on the right yaxis
                            yyaxis right;
                        end
                        ylabel('PID (V)')
                        ylim([c.pid_lims]);
                        r_ax = gca; r_ax.YColor = 'k';
                        p_pid = plot(this_pid_data(:,1),this_pid_data(:,2));
                        if strcmp(c.shorten_file_name,'yes')
                            p_pid.DisplayName = this_vial_num + " " + shortened_file_name;
                        else
                            p_pid.DisplayName = this_vial_num + " " + a_this_file_name;
                        end
                        if (k>1); p_pid.HandleVisibility = 'off'; end
                        if strcmp(c.plot_by_vial,'yes')
                            vial_num = str2double(this_vial_num(2));    % figure out which color
                            p_pid.Color = c.colors{vial_num};
                        else
                            p_pid.Color = c.colors{r};
                        end
                        p_pid.LineWidth = c.pid_width;
                        p_pid.LineStyle = '-';
                        p_pid.Marker = 'none';
                        
                        xlim(f.x_lim);
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
                        if ~(strcmp(c.plot_ctrl,'no') && strcmp(c.plot_flow,'no'))
                            yyaxis right;
                        end
                        r_ax = gca; r_ax.YColor = 'k';
                        p_pid = plot(this_pid_data(:,1),this_pid_data(:,2));
                        if strcmp(c.shorten_file_name,'yes')
                            p_pid.DisplayName = shortened_file_name;
                        else
                            p_pid.DisplayName = a_this_file_name;
                        end
                        p_pid.LineWidth = c.pid_width;
                        p_pid.LineStyle = '-';
                        p_pid.Marker = 'none';
                        
                        % if there are two trials, make sure they plot as the same color
                        if (j==1)
                            this_file_color = p_pid.Color;
                        else
                            p_pid.Color = this_file_color;
                        end
                        if (j>1); p_pid.HandleVisibility = 'off'; end
                        
                        xlim(f.x_lim);
                    end
                end
            end
        
        end
    end
end
clearvars -except a_* c f data

%% Set up plots
% F2: Flow v. PID
f2 = figure; hold on;
f2.Name = ['FLOW v. PID: ', a_title];
f2.Position = f.f2_position;
ax2 = gca;
legend('Location','northwest','Interpreter','none');
xlabel('Flow (SCCM)')
xlim(c.flow_lims)
ylabel('PID (V)')
ylim(c.pid_lims)
title(a_title);
if ~isempty(a_subtitle); subtitle(a_subtitle); end

% F3: Flow v. ctrl
if strcmp(c.plot_ctrl,'yes')
    f3 = figure; hold on;
    f3.Position = f.f3_position;
    f3.Name = ['FLOW v. CTRL: ', a_title];
    ax3 = gca;
    legend('Location','northwest','Interpreter','none');
    xlabel('Flow (SCCM)')
    xlim(c.flow_lims)
    ylabel('Ctrl (int)')
    if ~isempty(c.ctrl_lims); ylim(c.ctrl_lims); end
    title(a_title);
    if ~isempty(a_subtitle); subtitle(a_subtitle); end
end

%% Plot flow v. PID for each file
% For each file
for r=1:length(data)
    a_this_file_name = data(r).file_name;
    shortened_file_name = extractAfter(a_this_file_name,11);
    shortened_file_name = erase(shortened_file_name,'.mat');

    %% 8-line olfa
    if ~isempty(data(r).d_olfa_flow)
        % For each vial
        for i=1:length(data(r).d_olfa_flow)
            
            % Get the mean flow & PID, after cutting c.time_to_cut

            this_vial_num = data(r).d_olfa_flow(i).vial_num;
            this_file_events = data(r).d_olfa_flow(i).events.OV_keep;
            
            % Initialize empty structures
            this_file_new_means = [];
            this_file_new_stds = [];
            this_file_ctrl_means = [];
            this_file_ctrl_stds = [];

            %% For each trial: Cut data & calculate stats, add into main data structure: data(r).new_means
            for e=1:length(this_file_events)
                this_event_start_time = this_file_events(e).t_event;
                this_event_end_time = this_file_events(e).t_end;
                this_event_cut_t_start = this_event_start_time + c.time_to_cut;
                this_event_cut_t_end = this_event_end_time;
                
                % Get data from this event
                this_event_flow_data = this_file_events(e).data.flow_sccm;
                this_event_pid_data = this_file_events(e).data.pid;
                this_event_ctrl_data = data(r).d_olfa_flow(i).ctrl.ctrl_int;
                
                % Cut off the first c.time_to_cut seconds
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

                % Add to new structure
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
                s = scatter(ax2,x_flow,y_pid,'filled');
                if strcmp(c.shorten_file_name,'yes')
                    s.DisplayName = this_vial_num + " " + shortened_file_name;
                else
                    s.DisplayName = this_vial_num + " " + a_this_file_name;
                end
                if strcmp(c.plot_by_vial,'yes')
                    vial_num = str2double(this_vial_num(2));    % figure out which color
                    s.MarkerFaceColor = c.colors{vial_num};
                end
            end
        
            %% Plot Flow v. Ctrl means (f3)
            if ~isempty(this_file_ctrl_means)
                if strcmp(c.plot_ctrl,'yes')
                    y_ctrl = this_file_ctrl_means;
                    s2 = scatter(ax3,x_flow,y_ctrl,'filled');
                    if strcmp(c.shorten_file_name,'yes')
                        s2.DisplayName = this_vial_num + " " + shortened_file_name;
                    else
                        s2.DisplayName = this_vial_num + " " + a_this_file_name;
                    end
                    if strcmp(c.plot_by_vial,'yes')
                        vial_num = str2double(this_vial_num(2));    % figure out which color
                        s2.MarkerFaceColor = c.colors{vial_num};
                    end
                end
            end
            
            %% Plot error bars
            if ~isempty(x_flow)
                if strcmp(c.plot_error_bars,'yes')
                    % Initialize empty data structures
                    xneg = zeros(length(this_file_new_stds),1);
                    xpos = zeros(length(this_file_new_stds),1);
                    yneg = zeros(length(this_file_new_stds),1);
                    ypos = zeros(length(this_file_new_stds),1);
                    yneg_ctrl = zeros(length(this_file_new_stds),1);
                    ypos_ctrl = zeros(length(this_file_new_stds),1);
                    % For each event
                    for e=1:length(this_file_new_stds)
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
                    if strcmp(c.plot_ctrl,'yes')
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
            
            % Get the mean PID, after cutting c.time_to_cut
            this_event_start_time = this_file_events(e).data(1,1);
            this_event_end_time = this_file_events(e).data(end,1);
            this_event_cut_t_start = this_event_start_time + c.time_to_cut;
            
            this_event_pid_data = this_file_events(e).data;
            
            %% Calculate mean PID value

            % Start at c.time_to_cut seconds into the trial
            idx_of_start_time = (c.time_to_cut/c.nidaq_freq) + 1;
            new_pid_data = this_event_pid_data(idx_of_start_time:end,:);
            
            % Give it 2 seconds to get up there a little bit
            c.time_to_get_up_there = 2;
            if (c.time_to_cut < c.time_to_get_up_there)
                new_pid_data_1 = get_section_data(new_pid_data,c.time_to_get_up_there,new_pid_data(end,1));
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
                % if PID started below 0.1 (aka this was a 0 sccm trial), just make it a 4 second trial
                end_time = 4;
                end_idx = find(new_pid_data(:,1) <= end_time,1,'last');
                str = ['this was a 0 sccm trial (', num2str(this_event_flow_mean),' sccm, i=', num2str(i), ')'];
                disp(str)
            end

            % Get all the data for this period
            this_event_cut_pid_data = new_pid_data(1:end_idx,:);
            
            % Calculate the mean value
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
            s = scatter(ax2,x_flow,y_pid,'filled');
            if strcmp(c.shorten_file_name,'yes')
                s.DisplayName =  "standard olfa: " + shortened_file_name;
            else
                s.DisplayName =  "standard olfa: " + a_this_file_name;
            end
        end

        %% Plot error bars
        if ~isempty(x_flow)
            if strcmp(c.plot_error_bars,'yes')
                xneg = zeros(length(this_file_new_stds),1);
                xpos = zeros(length(this_file_new_stds),1);
                yneg = zeros(length(this_file_new_stds),1);
                ypos = zeros(length(this_file_new_stds),1);
                % For each event
                for e=1:length(this_file_new_stds)
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
                try e.Color = s.MarkerFaceColor;
                catch ME; e.Color = s.CData; end
            end
        end
    
    end
end
clearvars -except a_* c f data
