%% analysis_plot_olfa_and_pid
% plot olfa flow & pid values over time

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
f.PID_color = '#77AC30';
f.scale_time = 'no';

a_this_note = '';

%% Select shit to plot
plot_opts = struct();

% olfa options:

% plot olfa as sccm or int
plot_opts.plot_flow_as_sccm = 'yes';
% **if datafile does not have calibration tables listed in header, plot will be in ints regardless

% pick one of these
plot_opts.olfa = 'yes';
plot_opts.pid = 'no';
plot_opts.output_flow = 'no';
plot_opts.ctrl = 'yes';
plot_opts.ctrl_as_voltage = 'no';
plot_opts.plot_in_minutes = 'no';

%% Enter directory for this computer
%a_dir_OlfaEngDropbox = 'C:\Users\Admin\Dropbox (NYU Langone Health)\OlfactometerEngineeringGroup (2)';
%a_dir_OlfaEngDropbox = 'C:\Users\SB13FLLT004\Dropbox (NYU Langone Health)\OlfactometerEngineeringGroup (2)';
a_dir_OlfaEngDropbox = 'C:\Users\shann\Dropbox (NYU Langone Health)\OlfactometerEngineeringGroup (2)';

a_dir_OlfaControlGUI = strcat(a_dir_OlfaEngDropbox,'\Control\a_software\OlfaControl_GUI');

% make sure OlfaControlGUI is on matlab path
addpath(genpath(a_dir_OlfaControlGUI));

%% Enter data file name
a_thisfile_name = '2024-08-27_datafile_00';

%f.position = [549 166 1353 684];
%f.position = [166 600 775 275];     % for OneNote
f.position = [166 210 1300 600];    % for PowerPoint
%f.position = [166 210 650 600];    % for PowerPoint (1/2 size)
f.pid_width = 1.5;

%% Load .mat file

% full directory for .mat file
dir_this_mat_file = strcat(a_dir_OlfaControlGUI,'\analysis\data (.mat files)\',a_thisfile_name,'.mat');
%dir_this_mat_file = strcat(pwd,'\data (.mat files)\',a_thisfile_name,'.mat');

try
    load(dir_this_mat_file);
    clearvars mat_* dir_*
    %{
    %% plot: in sections (9/21/2022)
    % this is for spt characterization plots
    time_around_event = 3;
    for i=1:length(d_olfa_flow)
        this_vial = d_olfa_flow(i).vial_num;
    
        % since i don't have setpoint data let's do it by OV events
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
    
            % plot olfa
            if strcmp(plot_opts.plot_flow_as_sccm,'yes')
                if ~isempty(d_olfa_flow(i).cal_table_name)
                    % plot as sccm
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
                    % plot as integer
                    if ~isempty(d_olfa_flow(i).flow.flow_int)
                        ylabel('Olfa flow (integer values)')
                        p = plot(d_olfa_flow(i).flow.flow_int(:,1),d_olfa_flow(i).flow.flow_int(:,2));
                    end
                end
            else
                % plot as integer
                if ~isempty(d_olfa_flow(i).flow.flow_int)
                    ylabel('Olfa flow (integer values)')
                    p = plot(d_olfa_flow(i).flow.flow_int(:,1),d_olfa_flow(i).flow.flow_int(:,2));
                end
            end
            p.LineWidth = f.flow_width;
            p.DisplayName = [d_olfa_flow(i).vial_num ' flow'];
    
            % plot pid
            if strcmp(plot_opts.pid,'yes')
                if ~isempty(data_pid)
                    yyaxis right; colororder('#77AC30');  f1_ax.YColor = '#77AC30';
                    ylabel('PID output (V)');
                    this_pid_data = get_section_data(data_pid,t_beg_plot,t_end_plot);
                    this_pid_data_shifted = [];
                    this_pid_data_shifted(:,1) = this_pid_data(:,1) - t_beg_event;
                    this_pid_data_shifted(:,2) = this_pid_data(:,2);
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
    %% Make figure
    figTitle = a_thisfile_name;
    if ~strcmp(a_this_note, ''); figTitle = append(figTitle, ': ',  a_this_note); end
    
    f1 = figure; f1.NumberTitle = 'off'; f1.Position = f.position; hold on;
    f1.Name = a_thisfile_name;
    title(a_thisfile_name)
    subtitle(a_this_note)
    legend('Location','northwest');
    f1_ax = gca;
    
    % x limits
    if strcmp(plot_opts.plot_in_minutes,'no')
        xlabel('Time (s)');
    else
        xlabel('Time (min)')
    end
    if ~isempty(f.x_lim)
        xlim(f.x_lim);
    else
        t_end = data_time_raw(end,1);
        if strcmp(plot_opts.plot_in_minutes,'no')
            xlim([0 t_end]);
        else
            xlim([0 t_end/60])
        end
    end
    
    %% Plot: olfa flow
    if strcmp(plot_opts.olfa,'yes')
        % for each vial
        for i=1:length(d_olfa_flow)
            if strcmp(plot_opts.plot_flow_as_sccm,'yes')
                if ~isempty(d_olfa_flow(i).cal_table_name)
                    % plot as sccm
                    if ~isempty(d_olfa_flow(i).flow.flow_sccm)
                        d_olfa_flow_x = d_olfa_flow(i).flow.flow_sccm(:,1);
                        d_olfa_flow_y = d_olfa_flow(i).flow.flow_sccm(:,2);
                        ylabel('Olfa flow (sccm)')
                        if ~isempty(f.flow_ylims); ylim(f.flow_ylims)
                        else; ylim([-5 150]); end
                    end
                else
                    % plot as integer
                    if ~isempty(d_olfa_flow(i).flow.flow_int)
                        d_olfa_flow_x = d_olfa_flow(i).flow.flow_int(:,1);
                        d_olfa_flow_y = d_olfa_flow(i).flow.flow_int(:,2);
                        ylabel('Olfa flow (integer values)')
                        if ~isempty(f.flow_ylims); ylim(f.flow_ylims)
                        else; ylim([0 1024]); end
                    end
                end
            else
                % plot as integer
                if ~isempty(d_olfa_flow(i).flow.flow_int)
                    d_olfa_flow_x = d_olfa_flow(i).flow.flow_int(:,1);
                    d_olfa_flow_y = d_olfa_flow(i).flow.flow_int(:,2);
                    ylabel('Olfa flow (integer values)')
                    if ~isempty(f.flow_ylims); ylim(f.flow_ylims)
                    else; ylim([0 1024]); end
                end
            end
            
            if strcmp(f.scale_time,'yes')
                if ~isempty(f.x_lim)
                    % scale time to zero
                    d_olfa_flow_x = d_olfa_flow_x - f.x_lim(1);
                    % readjust x limits
                    xlim([-.5 16]);                
                end
            end
            if strcmp(plot_opts.plot_in_minutes,'yes')
                d_olfa_flow_x = d_olfa_flow_x/60;
            end
            p = plot(d_olfa_flow_x,d_olfa_flow_y);
            p.LineWidth = f.flow_width;
            p.DisplayName = [d_olfa_flow(i).vial_num ' flow'];
            %pa = scatter(d_olfa_flow_x,d_olfa_flow_y,'filled','HandleVisibility','off');
        end
    end
    
    %% Plot: olfa ctrl
    if strcmp(plot_opts.ctrl,'yes')
        % for each vial
        for i=1:length(d_olfa_flow)
            if strcmp(plot_opts.ctrl_as_voltage,'yes')
                % plot as voltage
                if ~isempty(d_olfa_flow(i).ctrl.ctrl_volt)
                    d_ctrl_x = d_olfa_flow(i).ctrl.ctrl_volt(:,1);
                    d_ctrl_y = d_olfa_flow(i).ctrl.ctrl_volt(:,2);
                    if strcmp(plot_opts.olfa,'no')
                        yyaxis left;
                    else
                        yyaxis right;
                    end
                    ylabel('Prop valve value (V)');
                    ylim([-0.1 5.1])
                end
            else
                % plot as integer
                if ~isempty(d_olfa_flow(i).ctrl.ctrl_int)
                    d_ctrl_x = d_olfa_flow(i).ctrl.ctrl_int(:,1);
                    d_ctrl_y = d_olfa_flow(i).ctrl.ctrl_int(:,2);
                    if strcmp(plot_opts.olfa,'no')
                        yyaxis left;
                    else
                        yyaxis right;
                    end
                    ylabel('Prop valve value (int)')
                    if ~isempty(f.ctrl_ylims); ylim(f.ctrl_ylims)
                    else; ylim([-5 260]); end
                    %ylim([0 260])
                end
            end
            if strcmp(f.scale_time,'yes')
                % scale time to zero
                d_ctrl_x = d_ctrl_x - f.x_lim(1);
                % readjust x limits
                xlim([-.5 16]);
            end
            if strcmp(plot_opts.plot_in_minutes,'yes')
                d_ctrl_x = d_ctrl_x/60;
            end
            p2 = plot(d_ctrl_x,d_ctrl_y);
            p2.DisplayName = [d_olfa_flow(i).vial_num ' ctrl'];
            %p2.HandleVisibility = 'off';
            p2.LineStyle = '-';
            %p2a = scatter(d_ctrl_x,d_ctrl_y,'filled','HandleVisibility','off');
        end
    end
    
    %% Plot: PID
    if strcmp(plot_opts.pid,'yes')
        if ~isempty(data_pid)
            d_pid_x = data_pid(:,1);
            d_pid_y = data_pid(:,2);
            yyaxis right;
            f1_ax.YColor = f.PID_color;
            ylabel('PID output (V)');
            if ~isempty(f.pid_ylims); f1_ax.YLim = f.pid_ylims; end
            
            if strcmp(f.scale_time,'yes')
                if ~isempty(f.x_lim)
                    d_pid_x = data_pid(:,1) - f.x_lim(1);
                end
            end
            
            if strcmp(plot_opts.plot_in_minutes,'yes')
                d_pid_x = d_pid_x/60;
            end
            p2 = plot(d_pid_x,d_pid_y,'DisplayName','PID');
            p2.LineWidth = f.pid_width;
            p2.Color = f.PID_color;
        end
    end
    
    %% Plot: output flow sensor
    if strcmp(plot_opts.output_flow,'yes')
        if ~isempty(data_fsens_raw)
            yyaxis right;
            ylabel('Output flow sensor (integer values)')
            p2 = plot(data_fsens_raw(:,1),data_fsens_raw(:,2));
            p2.DisplayName = 'Flow sensor';
        end
    end 
    
    %% Plot: calibration value
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