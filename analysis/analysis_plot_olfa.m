%% analysis_plot_olfa
% Plot olfa over time

%%
clearvars
%close all
set(0,'DefaultTextInterpreter','none')
%#ok<*SAGROW>
%#ok<*AGROW> 

%% Display variables
f = struct();   % struct containing all figure variables
f.position = [30 200 1700 700];
f.pid_ylims = [];
f.flow_ylims = [];
f.ctrl_ylims = [];
f.flow_width = 1;
f.pid_width = 1;
f.x_lim = [];
f.calibration_value = [];

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

E1_flow = [0 0.4470 0.7410];        % blue for E1
E1_ctrl = [0.8500 0.3250 0.0980];   % orange for E1 ctrl

%% Select shit to plot
plot_opts = struct();

% Plot olfa as sccm or int
plot_opts.plot_flow_as_sccm = 'yes';    % **if datafile does not have calibration tables listed in header, plot will be in ints regardless

% Ctrl options:
plot_opts.ctrl = 'yes';
plot_opts.ctrl_as_voltage = 'no';

%% Find OlfaControl_GUI directory (& add to path)

% Check if current directory contains 'OlfaControl_GUI'
c_current_dir = pwd;
c_str_to_find = 'OlfaControl_GUI';
c_idx_of_str = strfind(c_current_dir,c_str_to_find);

% If not, whole thing will fail (i don't feel like writing another try except statement rn)
if isempty(c_idx_of_str); disp(['Could not find ''' c_str_to_find,''' directory.']); end

% Get OlfaControl_GUI path
c_len_of_strToFind = length(c_str_to_find);
a_dir_OlfaControlGUI = c_current_dir(1:c_idx_of_str+c_len_of_strToFind-1);

% Make sure datafiles are on matlab path
dir_data_files = [a_dir_OlfaControlGUI '\result_files\48-line olfa\'];
addpath(genpath(dir_data_files));

clearvars c_*

%% Enter data file name (& additional plot options)
% ****Do not include '.csv' at end of file name****

%a_thisfile_name = '2023-10-11_datafile_18';
%a_thisfile_name = '2024-01-19_datafile_00';
a_thisfile_name = '2024-08-27_datafile_00'; plot_opts.ctrl = 'yes';
%a_thisfile_name = '2024-08-28_2024-01-16_datafile_14'; plot_opts.ctrl = 'no';

%f.position = [166 600 775 275];     % for OneNote
f.position = [166 210 1300 600];    % for PowerPoint
f.pid_width = 1.5;

%% Load *.mat file

% Full directory for .mat file
dir_this_mat_file = strcat(a_dir_OlfaControlGUI,'\analysis\data (.mat files)\',a_thisfile_name,'.mat');

try
    load(dir_this_mat_file);
    clearvars mat_* dir_*
    %{
    %% Plot: in sections (9/21/2022)
    % this is for spt characterization plots
    time_around_event = 3;
    for i=1:length(d_olfa_flow)
        this_vial = d_olfa_flow(i).vial_num;
    
        % Since i don't have setpoint data let's do it by OV events
        for e=1:length(d_olfa_flow(i).events.OV)
            t_beg_event = d_olfa_flow(i).events.OV(e).time;
            t_end_event = d_olfa_flow(i).events.OV(e).time + d_olfa_flow(i).events.OV(e).value;
            t_beg_plot = t_beg_event - time_around_event;
            t_end_plot = t_end_event + time_around_event;
    
            f1 = figure; f1.NumberTitle = 'off'; hold on; legend('Location','northwest');
            f1.Position = f.position;
            f1.WindowState = 'maximized';
            f1.Name = a_thisfile_name;
            f1_ax = gca;
            xlabel('Time (s)');
    
            % Plot olfa
            if strcmp(plot_opts.plot_flow_as_sccm,'yes')
                if ~isempty(d_olfa_flow(i).cal_table_name)
                    % Plot as sccm
                    if ~isempty(d_olfa_flow(i).flow.flow_sccm)
                        ylabel('Olfa flow (sccm)')
                        this_data_shifted = [];
                        this_data = d_olfa_flow(i).flow.flow_sccm;
                        this_data = get_section_data(this_data,t_beg_plot,t_end_plot);
                        this_data_shifted(:,1) = this_data(:,1) - t_beg_event;
                        this_data_shifted(:,2) = this_data(:,2);
                        p = plot(this_data_shifted(:,1),this_data_shifted(:,2));
                        %p = plot(d_olfa_flow(i).flow.flow_sccm(:,1),d_olfa_flow(i).flow.flow_sccm(:,2));
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
    
    f1 = figure; f1.NumberTitle = 'off'; f1.Position = f.position; hold on;
    f1.Name = a_thisfile_name;
    title(a_thisfile_name)
    subtitle(a_this_note)

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
    
    legend('Location','northwest');
    f1_ax = gca;
    
    % Set X limits
    xlabel('Time (s)');
    if ~isempty(f.x_lim)
        xlim(f.x_lim);
    else
        t_end = data_time_raw(end,1);
        xlim([0 t_end]);
    end
    
    %% Plot: Olfa flow
    % For each vial
    for i=1:length(d_olfa_flow)
        this_color = f.colors{i};   % Color to plot this vial as
        %{
        if contains(d_olfa_flow(i).vial_num,'E1')
            this_color = E1_flow;
        else
            this_color = f.colors{i};
        end
        %}
        % Plot as SCCM or integer values
        if strcmp(plot_opts.plot_flow_as_sccm,'yes')
            if ~isempty(d_olfa_flow(i).cal_table_name)
                % Plot as sccm
                if ~isempty(d_olfa_flow(i).flow.flow_sccm)
                    d_olfa_flow_x = d_olfa_flow(i).flow.flow_sccm(:,1);
                    d_olfa_flow_y = d_olfa_flow(i).flow.flow_sccm(:,2);
                    ylabel('Olfa flow (sccm)')
                    if ~isempty(f.flow_ylims); ylim(f.flow_ylims)
                    else; ylim([-5 150]); end
                end
            else
                % Plot as integer
                if ~isempty(d_olfa_flow(i).flow.flow_int)
                    d_olfa_flow_x = d_olfa_flow(i).flow.flow_int(:,1);
                    d_olfa_flow_y = d_olfa_flow(i).flow.flow_int(:,2);
                    ylabel('Olfa flow (integer values)')
                    if ~isempty(f.flow_ylims); ylim(f.flow_ylims)
                    else; ylim([0 1024]); end
                end
            end
        else
            % Plot as integer
            if ~isempty(d_olfa_flow(i).flow.flow_int)
                d_olfa_flow_x = d_olfa_flow(i).flow.flow_int(:,1);
                d_olfa_flow_y = d_olfa_flow(i).flow.flow_int(:,2);
                ylabel('Olfa flow (integer values)')
                if ~isempty(f.flow_ylims); ylim(f.flow_ylims)
                else; ylim([0 1024]); end
            end
        end

        p = plot(d_olfa_flow_x,d_olfa_flow_y);
        %p = scatter(d_olfa_flow_x,d_olfa_flow_y,'filled');
        p.LineWidth = f.flow_width;
        p.DisplayName = [d_olfa_flow(i).vial_num ' flow'];
        if ~isempty(this_color); p.Color = this_color; end
        %p.Color = f.colors{i};
    end
    
    %% Plot: Olfa ctrl
    if strcmp(plot_opts.ctrl,'yes')
        % For each vial
        for i=1:length(d_olfa_flow)
            this_color = E1_ctrl;
            %{
            if contains(d_olfa_flow(i).vial_num,'E1'); this_color = E1_ctrl;
            else; this_color = f.colors{i}; end
            %}
            if strcmp(plot_opts.ctrl_as_voltage,'yes')        
                % Plot as voltage
                if ~isempty(d_olfa_flow(i).ctrl.ctrl_volt)
                    d_ctrl_x = d_olfa_flow.ctrl.ctrl_volt(:,1);
                    d_ctrl_y = d_olfa_flow.ctrl.ctrl_volt(:,2);
                    yyaxis right;
                    ylabel('Prop valve value (V)');
                    ax = gca; ax.YColor = E1_ctrl;
                    if ~isempty(this_color); p2.Color = this_color; end
                    %if ~isempty(f.ctrl_ylims); ylim(f.ctrl_ylims)
                    %else; ylim([-0.1 5.1]); end
                    ylim([-0.1 5.1]);
                end
            else
                % Plot as integer
                if ~isempty(d_olfa_flow(i).ctrl.ctrl_int)
                    d_ctrl_x = d_olfa_flow(i).ctrl.ctrl_int(:,1);
                    d_ctrl_y = d_olfa_flow(i).ctrl.ctrl_int(:,2);
                    yyaxis right;
                    ylabel('Prop valve value (int)')
                    ax = gca; ax.YColor = E1_ctrl;
                    if ~isempty(this_color); p2.Color = this_color; end
                    if ~isempty(f.ctrl_ylims); ylim(f.ctrl_ylims)
                    else; ylim([-5 260]); end
                end
            end
            p2 = plot(d_ctrl_x,d_ctrl_y);
            p2.DisplayName = [d_olfa_flow(i).vial_num ' ctrl'];
        end
    end
    
    %% Plot: Calibration value
    if ~isempty(f.calibration_value)
        yyaxis left;
        yline(f.calibration_value,'r','LineWidth',2);
    end

catch ME
    switch ME.identifier
        case 'MATLAB:load:couldNotReadFile'
            disp(['---> ' a_thisfile_name,' has not been parsed yet: run analysis_get_and_parse_files.m first'])
        otherwise
            rethrow(ME)
    end
end