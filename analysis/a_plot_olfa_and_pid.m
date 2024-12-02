%Plot olfa flow & pid values over time
%  
%Required Input:
%   a_thisfile_name - file name
%
%Plot Options:
%   olfa_flow       - flow values on left yaxis
%   olfa_ctrl       - ctrl values on right yaxis
%   pid             - pid data on right yaxis
%   output_flow     - output flow sensor on right yaxis
%
%   flow_in_SCCM    - flow units in SCCM (default==yes) 
%   ctrl_in_V       - ctrl units in V (default=integers)
%   plot_in_minutes - timescale in minutes (default==seconds)
%
%   pid_ylims       - Axis limits for PID
%   flow_ylims      - Axis limits for Olfa flow
%   ctrl_ylims      - Axis limits for Olfa ctrl

%%
% --> this is a copy of the original file (last edited 09-23-2024),
% turning it into a function that I can call from the command line

%%

function a_plot_olfa_and_pid(a_thisfile_name,plot_opts)

    arguments
        a_thisfile_name         (1,1) string = '-'

        % Data to plot
        plot_opts.olfa_flow     (1,1) string = 'yes'
        plot_opts.olfa_ctrl     (1,1) string = 'no'
        plot_opts.pid           (1,1) string = 'yes'
        plot_opts.output_flow   (1,1) string = 'no'

        % Units
        plot_opts.flow_in_SCCM  (1,1) string = 'yes'
        plot_opts.ctrl_in_V     (1,1) string = 'no'
        plot_opts.plot_in_minutes   (1,1) string = 'no'

        % Axis Limits
        plot_opts.pid_lims      (1,:) double = [0 3]
        plot_opts.flow_lims     (1,:) double = [ ]
        plot_opts.ctrl_lims     (1,:) double = [-5 260]

        plot_opts.fig_position  (1,:) double = [166 210 1300 600]    % for PowerPoint
    end

%%
%close all
set(0,'DefaultTextInterpreter','none')

%% Display variables
f = struct();   % struct containing all figure variables
f.position = [30 200 1700 700];
f.flow_width = 1;
f.pid_width = 1;
f.x_lim = [];
f.calibration_value = [];
f.PID_color = '#77AC30';
f.scale_time = 'no';

% Vial colors
f.colors{1} = '#0072BD';    % blue
f.colors{2} = '#7E2F8E';    % purple
f.colors{3} = '#A2142F';    % dark red
f.colors{4} = '#D95319';    % orange
f.colors{5} = '#0072BD';    % blue
f.colors{6} = '#A2142F';    % dark red
f.colors{7} = '#D95319';    % orange
f.colors{8} = '#7E2F8E';    % purple
f.colors{9} = '#7E2F8E';    % purple
this_color = [];
% Ctrl colors
f.c_colors{1} = f.colors{7};    % orange
f.c_colors{2} = f.colors{6};    % dark red
f.c_colors{3} = f.colors{7};    % orange
f.c_colors{4} = f.colors{8};    % purple
f.c_colors{5} = f.colors{9};    % purple
f.c_colors{6} = f.colors{1};    % blue
f.c_colors{7} = f.colors{2};    % purple
f.c_colors{8} = f.colors{3};    % dark red
f.c_colors{9} = f.colors{4};    % orange


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

clearvars c_*

%% Enter data file name (& additional plot options)
% TODO get rid of this section

%f.position = [549 166 1353 684];
%f.position = [166 600 775 275];     % for OneNote
f.position = [166 210 1300 600];    % for PowerPoint
%f.position = [166 210 650 600];    % for PowerPoint (1/2 size)
f.pid_width = 1.5;

%% Load *.mat file

% Full directory for .mat file
dir_this_mat_file = strcat(a_dir_OlfaControlGUI,'\analysis\data (.mat files)\',a_thisfile_name,'.mat');

try
    load(dir_this_mat_file);    % TODO only load necessary variables to save time
    clearvars mat_* dir_*
    %{
    %% Plot: in sections (9/21/2022)
    % this is for spt characterization plots
    time_around_event = 3;  % time (sec) to show before & after the event
    for i=1:length(d_olfa_flow)
        this_vial = d_olfa_flow(i).vial_num;
    
        % Since i don't have setpoint data let's do it by OV events
        for e=1:length(d_olfa_flow(i).events.OV)
            % Get start & end time of event
            t_beg_event = d_olfa_flow(i).events.OV(e).time;
            t_end_event = d_olfa_flow(i).events.OV(e).time + d_olfa_flow(i).events.OV(e).value;
            t_beg_plot = t_beg_event - time_around_event;
            t_end_plot = t_end_event + time_around_event;
            
            % Create figure
            f1 = figure; f1.NumberTitle = 'off'; hold on; legend('Location','northwest');
            f1.Position = f.position;
            f1.WindowState = 'maximized';
            f1.Name = a_thisfile_name;
            f1_ax = gca;
            xlabel('Time (s)');
    
            % Plot olfa flow
            if strcmp(plot_opts.flow_in_SCCM,'yes')
                if ~isempty(d_olfa_flow(i).cal_table_name)
                    % Plot as SCCM
                    if ~isempty(d_olfa_flow(i).flow.flow_sccm)
                        ylabel('Olfa flow (SCCM)')
                        
                        % Shift so OV event happens at t=0
                        this_data_shifted = [];
                        this_data = d_olfa_flow(i).flow.flow_sccm;
                        this_data = get_section_data(this_data,t_beg_plot,t_end_plot);
                        this_data_shifted(:,1) = this_data(:,1) - t_beg_event;
                        this_data_shifted(:,2) = this_data(:,2);
                        
                        % Plot
                        p = plot(this_data_shifted(:,1),this_data_shifted(:,2));
                    end
                else
                    % Plot as integer
                    if ~isempty(d_olfa_flow(i).flow.flow_int)
                        ylabel('Olfa flow (integer values)')
                        p = plot(d_olfa_flow(i).flow.flow_int(:,1),d_olfa_flow(i).flow.flow_int(:,2));
                    end
                end
            else
                % Plot as integer
                if ~isempty(d_olfa_flow(i).flow.flow_int)
                    ylabel('Olfa flow (integer values)')
                    p = plot(d_olfa_flow(i).flow.flow_int(:,1),d_olfa_flow(i).flow.flow_int(:,2));
                end
            end
            p.LineWidth = f.flow_width;
            p.DisplayName = [d_olfa_flow(i).vial_num ' flow'];
            ylim([0 100]);
    
            % Plot PID
            if strcmp(plot_opts.pid,'yes')
                if ~isempty(data_pid)
                    yyaxis right; colororder('#77AC30');  f1_ax.YColor = '#77AC30';
                    ylabel('PID output (V)');

                    % Get data for this section
                    this_pid_data = get_section_data(data_pid,t_beg_plot,t_end_plot);

                    % Shift so OV event happens at t=0
                    this_pid_data_shifted = [];
                    this_pid_data_shifted(:,1) = this_pid_data(:,1) - t_beg_event;
                    this_pid_data_shifted(:,2) = this_pid_data(:,2);

                    % Plot
                    p2 = plot(this_pid_data_shifted(:,1),this_pid_data_shifted(:,2),'DisplayName','PID');
                    p2.LineWidth = f.pid_width;
                end
            end
    
            % set x lims
            xlim([-time_around_event this_data_shifted(end,1)])
            %xlim([t_beg_plot t_end_plot]);
            %pause
        end
    
    end
    %}
    %% Create figure
    figTitle = a_thisfile_name;
    if ~strcmp(a_this_note, ''); figTitle = append(figTitle, ': ',  a_this_note); end
    f1 = figure; f1.NumberTitle = 'off'; f1.Position = plot_opts.fig_position; hold on;
    f1.Name = a_thisfile_name;
    title(a_thisfile_name)
    subtitle(a_this_note)
    legend('Location','northwest');
    f1_ax = gca;
    
    % sccm lines for 2023-09-21_datafile_05
    %{
    yline1 = line([1.5 7.5],[50 50]);
    yline2 = line([11 17.2],[70 70]);
    yline3 = line([21.5 27.5],[100 100]);
    yline4 = line([31 37],[20 20]);
    yline1.LineStyle = '-.';
    yline2.LineStyle = '-.';
    yline3.LineStyle = '-.';
    yline4.LineStyle = '-.';
    yline1.LineWidth = 2;
    yline2.LineWidth = 2;
    yline3.LineWidth = 2;
    yline4.LineWidth = 2;
    yline1.Color = 'black';
    yline2.Color = 'black';
    yline3.Color = 'black';
    yline4.Color = 'black';
    set(get(get(yline1,'Annotation'),'LegendInformation'),'IconDisplayStyle','off');
    set(get(get(yline2,'Annotation'),'LegendInformation'),'IconDisplayStyle','off');
    set(get(get(yline3,'Annotation'),'LegendInformation'),'IconDisplayStyle','off');
    set(get(get(yline4,'Annotation'),'LegendInformation'),'IconDisplayStyle','off');
    %}
    
    % Set X axis label
    if strcmp(plot_opts.plot_in_minutes,'no');  xlabel('Time (s)');
    else;                                       xlabel('Time (min)'); end
    % Set X limits
    if ~isempty(f.x_lim)
        xlim(f.x_lim);
    else
        t_end = data_time_raw(end,1);
        if strcmp(plot_opts.plot_in_minutes,'no');  xlim([0 t_end]);
        else;                                       xlim([0 t_end/60]); end
    end
    
    %% Plot: Olfa flow
    if strcmp(plot_opts.olfa_flow,'yes')
        % For each vial
        for i=1:length(d_olfa_flow)
            this_color = f.colors{i};   % Color to plot this vial as
            d_olfa_flow_x = [];
            d_olfa_flow_y = [];

            % Get olfa flow data (SCCM or integer values)
            if strcmp(plot_opts.flow_in_SCCM,'yes')
                % Plot as SCCM
                if ~isempty(d_olfa_flow(i).flow.flow_sccm)
                    d_olfa_flow_x = d_olfa_flow(i).flow.flow_sccm(:,1);
                    d_olfa_flow_y = d_olfa_flow(i).flow.flow_sccm(:,2);
                    ylabel('Olfa flow (SCCM)')
                    if ~isempty(plot_opts.flow_lims); ylim(plot_opts.flow_lims)
                    else; ylim([-5 120]); end
                end
            else
                % Plot as integer
                if ~isempty(d_olfa_flow(i).flow.flow_int)
                    d_olfa_flow_x = d_olfa_flow(i).flow.flow_int(:,1);
                    d_olfa_flow_y = d_olfa_flow(i).flow.flow_int(:,2);
                    ylabel('Olfa flow (integer values)')
                    if ~isempty(plot_opts.flow_lims); ylim(plot_opts.flow_lims)
                    else; ylim([0 1024]); end
                end
            end
            
            % If selected: Scale time
            if strcmp(f.scale_time,'yes')
                if ~isempty(f.x_lim)
                    % scale time to zero
                    d_olfa_flow_x = d_olfa_flow_x - f.x_lim(1);
                    % readjust x limits
                    xlim([-.5 16]);                
                end
            end
            
            % If selected: Plot in minutes
            if strcmp(plot_opts.plot_in_minutes,'yes')
                d_olfa_flow_x = d_olfa_flow_x/60;
            end

            % Plot olfa flow data
            try
                p = plot(d_olfa_flow_x,d_olfa_flow_y);
                %p = scatter(d_olfa_flow_x,d_olfa_flow_y,'filled');
                p.LineWidth = f.flow_width;
                p.DisplayName = [d_olfa_flow(i).vial_num ' flow'];
                p.Color = this_color;
            % Error message in case no flow values available
            catch ME
                switch ME.identifier
                    case 'MATLAB:emptyObjectDotAssignment'
                        disp(['---> No flow values available to plot for ' d_olfa_flow(i).vial_num])
                    otherwise
                        rethrow(ME)
                end
            end

        end
    end
    
    %% Plot: Olfa ctrl
    if strcmp(plot_opts.olfa_ctrl,'yes')
        % For each vial
        for i=1:length(d_olfa_flow)
            this_color = f.c_colors{i};   % Color to plot this vial as
            d_ctrl_x = [];
            d_ctrl_y = [];

            % Get olfa ctrl data (integer or voltage values)
            if strcmp(plot_opts.ctrl_in_V,'yes')
                % Plot as voltage
                if ~isempty(d_olfa_flow(i).ctrl.ctrl_volt)
                    d_ctrl_x = d_olfa_flow(i).ctrl.ctrl_volt(:,1);
                    d_ctrl_y = d_olfa_flow(i).ctrl.ctrl_volt(:,2);
                    % If olfa flow is not plotted, put ctrl on left axis
                    if strcmp(plot_opts.olfa_flow,'no')
                        yyaxis left;
                    else
                        yyaxis right;
                    end
                    ylabel('Prop valve value (V)');
                    ylim([-0.1 5.1])
                end
            else
                % Plot as integer
                if ~isempty(d_olfa_flow(i).ctrl.ctrl_int)
                    d_ctrl_x = d_olfa_flow(i).ctrl.ctrl_int(:,1);
                    d_ctrl_y = d_olfa_flow(i).ctrl.ctrl_int(:,2);
                    % If olfa flow is not plotted, put ctrl on left axis
                    if strcmp(plot_opts.olfa_flow,'no')
                        yyaxis left;
                    else
                        yyaxis right;
                    end
                    ylabel('Prop valve value (int)')
                    ylim(plot_opts.ctrl_lims);
                end
            end

            % If selected: Scale time
            if strcmp(f.scale_time,'yes')
                % Scale time to zero
                d_ctrl_x = d_ctrl_x - f.x_lim(1);
                % Readjust x limits
                xlim([-.5 16]);
            end
            
            % If selected: Plot in minutes
            if strcmp(plot_opts.plot_in_minutes,'yes')
                d_ctrl_x = d_ctrl_x/60;
            end
            
            % Plot olfa ctrl data
            try
                p2 = plot(d_ctrl_x,d_ctrl_y);
                p2.DisplayName = [d_olfa_flow(i).vial_num ' ctrl'];
                %p2.HandleVisibility = 'off';
                p2.LineStyle = '--';
                p2.Color = this_color;
            % Error message in case no ctrl values available
            catch ME
                switch ME.identifier
                    case 'MATLAB:emptyObjectDotAssignment'
                        disp(['---> No ctrl values available to plot for ' d_olfa_flow(i).vial_num])
                    otherwise
                        rethrow(ME)
                end
            end     
        end
    end
    
    %% Plot: PID
    if strcmp(plot_opts.pid,'yes')
        
        if ~isempty(data_pid)
            if ~(strcmp(plot_opts.olfa_ctrl,'no') && strcmp(plot_opts.olfa_flow,'no'))      % If either flow or ctrl are plotted, put PID on the right yaxis
                yyaxis right;
            end
            d_pid_x = data_pid(:,1);
            d_pid_y = data_pid(:,2);
            f1_ax.YColor = f.PID_color;
            ylabel('PID output (V)');
            f1_ax.YLim = plot_opts.pid_lims;

            % If selected: scale time
            if strcmp(f.scale_time,'yes')
                if ~isempty(f.x_lim)
                    d_pid_x = data_pid(:,1) - f.x_lim(1);
                end
            end
            
            % If selected: Plot in minutes
            if strcmp(plot_opts.plot_in_minutes,'yes')
                d_pid_x = d_pid_x/60;
            end

            % Plot PID
            p2 = plot(d_pid_x,d_pid_y,'DisplayName','PID');
            p2.LineWidth = f.pid_width;
            p2.Color = f.PID_color;
        else
            disp('---> No PID data available to plot')
        end
    end
    
    %% Plot: Output flow sensor
    if strcmp(plot_opts.output_flow,'yes')
        if ~isempty(data_fsens_raw)
            yyaxis right;
            ylabel('Output flow sensor (integer values)')
            p2 = plot(data_fsens_raw(:,1),data_fsens_raw(:,2));
            p2.DisplayName = 'Flow sensor';
        else
            disp('---> No output flow sensor data available to plot')
        end
    end 
    
    %% Plot: Calibration value
    if ~isempty(f.calibration_value)
        yyaxis left;
        yline(f.calibration_value,'r','LineWidth',2);
    end

catch ME
    if strcmp(a_thisfile_name,'-')
        disp("---> No file name entered")
    else
        switch ME.identifier
            case 'MATLAB:load:couldNotReadFile'
                disp(['---> ' a_thisfile_name,' has not been parsed yet: run analysis_get_and_parse_files.m first'])
            otherwise
                rethrow(ME)
        end
    end
end

end