%% analysis_plot_olfa_and_pid
% plot olfa flow & pid values over time
%%
clearvars
set(0,'DefaultTextInterpreter','none')
%close all
%#ok<*SAGROW>
%#ok<*AGROW> 

%% display variables
f = struct();   % struct containing all figure variables
f.position = [30 200 1700 700];
f.pid_ylims = [];
f.flow_ylims = [];
f.flow_width = 1;
f.pid_width = 1;
f.x_lim = [];
f.calibration_value = [];
f.PID_color = '#77AC30';
f.scale_time = 'no';

a_this_note = '';

%% enter directory for this computer
%a_dir_OlfaEngDropbox = 'C:\Users\Admin\Dropbox (NYU Langone Health)\OlfactometerEngineeringGroup (2)';
a_dir_OlfaEngDropbox = 'C:\Users\SB13FLLT004\Dropbox (NYU Langone Health)\OlfactometerEngineeringGroup (2)';

a_dir_OlfaControlGUI = strcat(a_dir_OlfaEngDropbox,'\Control\a_software\OlfaControl_GUI');

% make sure OlfaControlGUI is on matlab path
addpath(genpath(a_dir_OlfaControlGUI));
%% select shit to plot
plot_opts = struct();

% olfa options:

% plot olfa as sccm or int
plot_opts.plot_flow_as_sccm = 'yes';
% **if datafile does not have calibration tables listed in header, plot will be in ints regardless

% pick one of these
plot_opts.olfa = 'yes';
plot_opts.pid = 'yes';
plot_opts.output_flow = 'no';
plot_opts.ctrl = 'no';
plot_opts.ctrl_as_voltage = 'no';

%% enter data file name
%{
% 10 SCCM
%a_thisfile_name = '2023-10-11_datafile_19';
%a_thisfile_name = '2023-10-11_datafile_20'; f.x_lim = [15.028 92.17];
% 0.5 sec before fake open, 1 sec after end of real open
%a_thisfile_name = '2023-10-11_datafile_19'; f.x_lim = [6.044 26.475];
%a_thisfile_name = '2023-10-11_datafile_19'; f.x_lim = [26.6 47.03];
%a_thisfile_name = '2023-10-11_datafile_20'; f.x_lim = [21.177 41.126];  % fake open didn't work for some reason
%a_thisfile_name = '2023-10-11_datafile_20'; f.x_lim = [56.626 77.052];
%f.pid_ylims = [-0.01 .25];
%f.scale_time = 'yes';

% 20 SCCM
%a_thisfile_name = '2023-10-11_datafile_21';
% 1 sec before fake open, 2 sec after real open ends
%a_thisfile_name = '2023-10-11_datafile_21'; f.x_lim = [20.549 41.2710];
%a_thisfile_name = '2023-10-11_datafile_21'; f.x_lim = [56.133 76.813];
%f.pid_ylims = [-0.01 .5];
%f.scale_time = 'yes';

%a_thisfile_name = '2023-10-11_datafile_22';
%a_thisfile_name = '2023-10-11_datafile_23';
%a_thisfile_name = '2023-10-11_datafile_24';
%a_thisfile_name = '2023-10-11_datafile_25';
%f.pid_ylims = [0 3];
%}

%a_thisfile_name = '2023-10-12_datafile_00'; f.pid_ylims = [-.1 3];
%a_thisfile_name = '2023-10-12_datafile_01'; f.pid_ylims = [-.1 3];
%a_thisfile_name = '2023-10-17_datafile_00';
%{
%a_thisfile_name = '2023-10-18_datafile_00';

%a_thisfile_name = '2023-10-18_datafile_02';
% 10 SCCM
%f.x_lim = [536.472 1000];
%f.x_lim = [809.812 1000];
% 100 SCCM
%f.x_lim = [260.979 1000];
%f.x_lim = [306.567 1000];
%f.pid_ylims = [0 .15];
%f.pid_ylims = [0 .5];
%f.flow_ylims = [0 100];
%f.scale_time = 'yes';

%a_thisfile_name = '2023-10-19_datafile_03';
% 10 SCCM
%{
%f.x_lim = [348.782 368.394];
%f.x_lim = [833.06 852.741];
%}
%f.x_lim = [352.394 368.394];
%f.x_lim = [836.741 900];
%f.pid_ylims = [0 .5];
%plot_opts.ctrl = 'yes';
%f.flow_ylims = [0 100];

%a_thisfile_name = '2023-10-19_datafile_04';
% 10 SCCM
%{
%f.x_lim = [651.172 670.78]; f.pid_ylims = [0 .5];
%f.x_lim = [1558.8 1578.4]; f.pid_ylims = [0 .5];
%}
%f.x_lim = [654.78 670.78]; f.pid_ylims = [0 .5];
%f.x_lim = [1562.401 1578.4]; f.pid_ylims = [0 .5];
%f.scale_time = 'yes';

%a_thisfile_name = '2023-10-19_datafile_05';
% 10 SCCM
%{
%f.x_lim = [283.863 303.471];
%f.x_lim = [830.152 849.76];
%}
%f.x_lim = [287.471 303.471];
%f.x_lim = [833.76 849.76];
%f.flow_ylims = [0 100];
%f.pid_ylims = [0 .5];
%f.scale_time = 'yes';

%}
%a_thisfile_name = '2023-10-20_datafile_00';

%a_thisfile_name = '2023-10-27_datafile_01'; f.pid_ylims = [0 6];
% 10 SCCM
%f.x_lim = [31.541 900];
%f.x_lim = [72.064 900];
% 100 SCCM
%f.x_lim = [760.671 900];
%f.x_lim = [801.182 900];

%a_thisfile_name = '2023-10-27_datafile_02'; f.pid_ylims = [0 6];
% 10 SCCM
%f.x_lim = [72.023 900];
%f.x_lim = [153.08 900];
% 100 SCCM
%f.x_lim = [436.755 900];
%f.x_lim = [720.489 900];
%f.scale_time = 'yes';

%a_thisfile_name = '2023-10-27_datafile_03'; f.pid_ylims = [0 6];
%a_thisfile_name = '2023-10-27_datafile_04'; f.pid_ylims = [0 6]; f.flow_ylims = [0 100];
%a_thisfile_name = '2023-10-27_datafile_05'; f.pid_ylims = [0 6]; f.flow_ylims = [0 100];
%a_thisfile_name = '2023-10-27_datafile_06'; f.pid_ylims = [0 6]; f.flow_ylims = [0 100];
%a_thisfile_name = '2023-10-27_datafile_08'; f.pid_ylims = [0 6]; f.flow_ylims = [0 100]; f.x_lim = [21.508 91.508];
%a_thisfile_name = '2023-10-27_datafile_11'; f.pid_ylims = [0 6]; f.flow_ylims = [0 100]; f.x_lim = [21.508 91.508];    % make sure you change it to i=2:length
%a_thisfile_name = '2023-10-27_datafile_14'; f.pid_ylims = [0 6]; f.flow_ylims = [0 100]; f.x_lim = [21.509 91.509];
%a_thisfile_name = '2023-10-27_datafile_15'; f.pid_ylims = [0 6]; f.flow_ylims = [0 100]; f.x_lim = [21.518 91.518];
%f.pid_ylims = [0 8];
%a_thisfile_name = '2023-10-30_datafile_05'; f.pid_ylims = [0 6]; f.flow_ylims = [0 100];
%a_thisfile_name = '2023-10-31_datafile_00';
%a_thisfile_name = '2023-10-31_datafile_08';
%a_thisfile_name = '2023-10-31_datafile_11';

a_thisfile_name = '2023-11-02_datafile_00';
%a_thisfile_name = '2023-11-02_datafile_01';
%a_thisfile_name = '2023-11-02_datafile_02';
%a_thisfile_name = '2023-11-02_datafile_04';
f.flow_ylims = [0 120];
f.pid_ylims = [0 3.5];

%f.position = [549 166 1353 684];
%f.position = [166 600 775 275];     % for OneNote
f.position = [166 210 1300 600];    % for PowerPoint
%f.position = [166 210 650 600];    % for PowerPoint (1/2 size)
f.pid_width = 1.5;

%% load .mat file

% full directory for .mat file
dir_this_mat_file = strcat(a_dir_OlfaControlGUI,'\analysis\data (.mat files)\',a_thisfile_name,'.mat');
%dir_this_mat_file = strcat(pwd,'\data (.mat files)\',a_thisfile_name,'.mat');

%% plot
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
    %% make figure
    figTitle = a_thisfile_name;
    if ~strcmp(a_this_note, ''); figTitle = append(figTitle, ': ',  a_this_note); end
    
    f1 = figure; f1.NumberTitle = 'off'; f1.Position = f.position; hold on;
    f1.Name = a_thisfile_name;
    title(a_thisfile_name)
    subtitle(a_this_note)
    legend('Location','northwest');
    f1_ax = gca;
    
    % x limits
    xlabel('Time (s)');
    if ~isempty(f.x_lim)
        xlim(f.x_lim);
    else
        t_end = data_time_raw(end,1);
        xlim([0 t_end]);
    end
    
    %% plot: olfa flow
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
            p = plot(d_olfa_flow_x,d_olfa_flow_y);
            p.LineWidth = f.flow_width;
            p.DisplayName = [d_olfa_flow(i).vial_num ' flow'];
            %pa = scatter(d_olfa_flow_x,d_olfa_flow_y,'filled','HandleVisibility','off');
        end
    end
    
    %% plot: olfa ctrl
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
                    ylim([-5 260])
                end
            end
            if strcmp(f.scale_time,'yes')
                d_ctrl_x = d_ctrl_x - f.x_lim(1);
            end
            p2 = plot(d_ctrl_x,d_ctrl_y);
            p2.DisplayName = [d_olfa_flow(i).vial_num ' ctrl'];
            p2.LineStyle = '-';
            %p2a = scatter(d_ctrl_x,d_ctrl_y,'filled','HandleVisibility','off');
        end
    end
    
    %% plot: pid
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
            
            p2 = plot(d_pid_x,d_pid_y,'DisplayName','PID');
            p2.LineWidth = f.pid_width;
            p2.Color = f.PID_color;
        end
    end
    
    %% plot: output flow sensor
    if strcmp(plot_opts.output_flow,'yes')
        if ~isempty(data_fsens_raw)
            yyaxis right;
            ylabel('Output flow sensor (integer values)')
            p2 = plot(data_fsens_raw(:,1),data_fsens_raw(:,2));
            p2.DisplayName = 'Flow sensor';
        end
    end 
    
    %% plot calibration value
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