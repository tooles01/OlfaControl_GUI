%% analysis_plot_olfa_and_pid
% plot olfa over time
%%
clearvars
set(0,'DefaultTextInterpreter','none')
%close all
%#ok<*SAGROW>
%#ok<*AGROW> 
%{
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

%}
%% display variables
f = struct();   % struct containing all figure variables
f.position = [30 200 1700 700];
f.pid_ylims = [];
f.flow_ylims = [];
f.flow_width = 1;
f.pid_width = 1;
f.x_lim = [];
f.calibration_value = [];

%% enter directory for this computer
a_dir_OlfaEngDropbox = 'C:\Users\Admin\Dropbox (NYU Langone Health)\OlfactometerEngineeringGroup (2)';
%a_dir_OlfaEngDropbox = 'C:\Users\SB13FLLT004\Dropbox (NYU Langone Health)\OlfactometerEngineeringGroup (2)';

a_dir_OlfaControlGUI = strcat(a_dir_OlfaEngDropbox,'\Control\a_software\OlfaControl_GUI');

% make sure OlfaControlGUI is on matlab path
addpath(genpath(a_dir_OlfaControlGUI));
%% select shit to plot
plot_opts = struct();

% plot olfa as sccm or int
plot_opts.plot_sccm = 'no';
% **if datafile does not have calibration tables listed in header, plot will be in ints regardless

% ctrl options:
plot_opts.ctrl = 'no';
plot_opts.ctrl_as_voltage = 'no';

%% enter data file name
%{
%a_thisfile_name = '2020-12-15_exp01_21';
%a_thisfile_name = '2020-12-16_exp01_22';
%a_thisfile_name = '2022-09-08_datafile_00';
%a_thisfile_name = '2022-09-07_datafile_01'; a_this_note = 'sensor calibration';
%a_thisfile_name = '2022-09-07_datafile_02'; a_this_note = 'sensor calibration';
%a_thisfile_name = '2022-09-07_datafile_03'; a_this_note = 'setpoint char 0-100 sccm';  f.pid_ylims=([-.1 1.2]);
%a_thisfile_name = '2022-09-07_datafile_04'; a_this_note = 'setpoint char 80, 90, 100 sccm';
%a_thisfile_name = '2022-09-07_datafile_05';
%}
%a_thisfile_name = '2022-09-06_datafile_11'; plot_opts.ctrl = 'yes';   f.position = [549 166 1353 684];

%a_thisfile_name = '2022-09-09_datafile_00'; a_this_note = 'A2 at 100sccm'; f.pid_ylims = [-.1 2.5];
%a_thisfile_name = '2022-09-09_datafile_01'; a_this_note = 'A6 at 100sccm'; f.pid_ylims = [-.5 10];
%_thisfile_name = '2022-09-09_datafile_02'; a_this_note = 'A6- Kp at .05, .04, .03, .01, .00, .08';
%a_thisfile_name = '2022-09-09_datafile_03'; a_this_note = 'A6- Kp at .010, .005, .010, .010,';
%a_thisfile_name = '2022-09-09_datafile_04'; a_this_note = 'A6- with A2 vial, Kp back at .05';
%a_thisfile_name = '2022-09-09_datafile_05'; a_this_note = 'A6- with A2 vial, Kp back at .05, with correct cal table';
%a_thisfile_name = '2022-09-09_datafile_06'; a_this_note = 'A6- with A2 vial, Kp at .10, .15, .05';
%a_thisfile_name = '2022-09-09_datafile_07'; a_this_note = 'A6- with A2 vial, Kp at .05, .04, .03, .02, .01';
%a_thisfile_name = '2022-09-09_datafile_08'; a_this_note = 'A6- Kp at .05, Ki at .0001, .0005, .0010';

% additive/spt char
%a_thisfile_name = '2022-09-09_datafile_09'; a_this_note = 'A2 90cc, A6 10cc';
%a_thisfile_name = '2022-09-09_datafile_10'; a_this_note = 'A2 50cc, A6 50cc';
%a_thisfile_name = '2022-09-09_datafile_11'; a_this_note = 'A2 50cc, A6 50cc';%   f.pid_ylims = [-.1 6];
%a_thisfile_name = '2022-09-09_datafile_12'; a_this_note = 'A2 & A6 additive'; f.pid_ylims = [-.1 7];
%a_thisfile_name = '2022-09-09_datafile_13'; a_this_note = 'A2 setpoint char'; f.pid_ylims = [-.1 7];
a_thisfile_name = '2022-09-09_datafile_13'; a_this_note = 'A2 setpoint char'; f.pid_ylims = [-.01 .6]; f.flow_ylims = [-1 110];
% view delayed PID response
% 40cc
%f.x_lim = [197.758 247.4]; f.pid_ylims = [-.01 .35]; f.flow_ylims = [-1 50]; a_this_note = 'A2 at 40 sccm';
% 50cc
%f.x_lim = [250 320];

%a_thisfile_name = '2022-09-09_datafile_14'; a_this_note = 'A6 setpoint char'; f.pid_ylims = [-.1 7];
%a_thisfile_name = '2022-09-09_datafile_15'; a_this_note = 'A6 setpoint char'; %f.pid_ylims = [-.1 7]; plot_opts.plot_sccm = 'yes';
% flow calibration
%{
%a_thisfile_name = '2022-09-12_datafile_00'; a_this_note = 'A2 flow calibration (automated)'; %plot_opts.plot_sccm = 'no';
%a_thisfile_name = '2022-09-13_datafile_00';
%a_this_note = '110 sccm auto calibration'; f.position = [1206 166 696 326]; f.flow_ylims = [560 575]; f.x_lim = [80 149];
%a_this_note = '100 sccm auto calibration'; f.position = [1206 166 696 326]; f.flow_ylims = [537 550]; f.x_lim = [180 262];    % def still decreasing
%a_this_note = '90 sccm auto calibration'; f.position = [1206 166 696 326]; f.flow_ylims = [505 520]; f.x_lim = [300 384];     % a little bit decreasing
%a_this_note = '80 sccm auto calibration'; f.position = [1206 166 696 326]; f.flow_ylims = [475 495]; f.x_lim = [420 495]; % still decreasing but so close
%a_thisfile_name = '2022-09-13_datafile_02 - Copy';
%a_this_note = '100 sccm'; f.flow_ylims = [530 542]; f.x_lim = ([90 240]); f.calibration_value = 535.04;
%a_this_note = '90 sccm'; f.flow_ylims = [502 513]; f.x_lim = ([280 815]); f.calibration_value = 507.83;
f.position = [549 166 1353 684];
%}

plot_opts.plot_sccm = 'yes';
%f.flow_ylims = [-5 150];
%f.pid_ylims = [-.1 7];
%f.position = [549 166 1353 684];
%f.position = [166 600 775 275];     % for OneNote
f.position = [166 210 1300 600];    % for PowerPoint
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
            if strcmp(plot_opts.plot_sccm,'yes')
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
    
            % set x lims
            xlim([-time_around_event this_data_shifted(end,1)])
            %xlim([t_beg_plot t_end_plot]);
            %pause
        end
    
    end
    %}
    %% make figure
    figTitle = a_thisfile_name;
    if ~strcmp(a_this_note, '')
        figTitle = append(figTitle, ': ',  a_this_note);
    end
    
    f1 = figure; f1.NumberTitle = 'off'; f1.Position = f.position; hold on;
    f1.Name = a_thisfile_name; title(figTitle)
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
    % for each vial
    for i=1:length(d_olfa_flow)
        if strcmp(plot_opts.plot_sccm,'yes')
            if ~isempty(d_olfa_flow(i).cal_table_name)
                % plot as sccm
                if ~isempty(d_olfa_flow(i).flow.flow_sccm)
                    ylabel('Olfa flow (sccm)')
                    p = plot(d_olfa_flow(i).flow.flow_sccm(:,1),d_olfa_flow(i).flow.flow_sccm(:,2));
                    p.LineWidth = f.flow_width;
                    p.DisplayName = [d_olfa_flow(i).vial_num ' flow'];
                    if ~isempty(f.flow_ylims)
                        ylim(f.flow_ylims)
                    else
                        ylim([-5 150])
                    end
                end
            else
                % plot as integer
                if ~isempty(d_olfa_flow(i).flow.flow_int)
                    ylabel('Olfa flow (integer values)')
                    p = plot(d_olfa_flow(i).flow.flow_int(:,1),d_olfa_flow(i).flow.flow_int(:,2));
                    p.LineWidth = f.flow_width;
                    p.DisplayName = [d_olfa_flow(i).vial_num ' flow'];
                    if ~isempty(f.flow_ylims)
                        ylim(f.flow_ylims)
                    else
                        ylim([0 1024])
                    end
                end
            end
        else
            % plot as integer
            if ~isempty(d_olfa_flow(i).flow.flow_int)
                ylabel('Olfa flow (integer values)')
                p = plot(d_olfa_flow(i).flow.flow_int(:,1),d_olfa_flow(i).flow.flow_int(:,2));
                p.LineWidth = f.flow_width;
                p.DisplayName = [d_olfa_flow(i).vial_num ' flow'];
                if ~isempty(f.flow_ylims)
                    ylim(f.flow_ylims)
                else
                    ylim([0 1024])
                end
            end
        end
    end
    
    %% plot: olfa ctrl
    if strcmp(plot_opts.ctrl,'yes')
        % for each vial
        for i=1:length(d_olfa_flow)
            if strcmp(plot_opts.ctrl_as_voltage,'yes')        
                % plot as voltage
                if ~isempty(d_olfa_flow(i).ctrl.ctrl_volt)
                    yyaxis right;
                    ylabel('Prop valve value (V)');
                    p2 = plot(d_olfa_flow.ctrl.ctrl_volt(:,1),d_olfa_flow.ctrl.ctrl_volt(:,2));
                    p2.DisplayName = [d_olfa_flow(i).vial_num ' ctrl'];
                    ylim([-0.1 5.1])
                end
            else
                % plot as integer
                if ~isempty(d_olfa_flow(i).ctrl.ctrl_int)
                    yyaxis right;
                    ylabel('Prop valve value (int)')
                    p2 = plot(d_olfa_flow.ctrl.ctrl_int(:,1),d_olfa_flow.ctrl.ctrl_int(:,2));
                    p2.DisplayName = [d_olfa_flow(i).vial_num ' ctrl'];
                    ylim([-5 260])
                end
            end
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