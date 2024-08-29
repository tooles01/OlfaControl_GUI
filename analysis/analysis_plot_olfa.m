%% analysis_plot_olfa
% plot olfa over time
%%
clearvars
set(0,'DefaultTextInterpreter','none')
%close all
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

% blue for E1
E1_flow = [0 0.4470 0.7410];
% orange for E1 ctrl
E1_ctrl = [0.8500 0.3250 0.0980];

this_color = [];

%% Select shit to plot
plot_opts = struct();

% plot olfa as sccm or int
plot_opts.plot_flow_as_sccm = 'yes';    % **if datafile does not have calibration tables listed in header, plot will be in ints regardless

% ctrl options:
plot_opts.ctrl = 'yes';
plot_opts.ctrl_as_voltage = 'no';

%% Enter directory for this computer
%a_dir_OlfaEngDropbox = 'C:\Users\Admin\Dropbox (NYU Langone Health)\OlfactometerEngineeringGroup (2)';
%a_dir_OlfaEngDropbox = 'C:\Users\SB13FLLT004\Dropbox (NYU Langone Health)\OlfactometerEngineeringGroup (2)';
a_dir_OlfaEngDropbox = 'C:\Users\shann\Dropbox (NYU Langone Health)\OlfactometerEngineeringGroup (2)';

a_dir_OlfaControlGUI = strcat(a_dir_OlfaEngDropbox,'\Control\a_software\OlfaControl_GUI');

addpath(genpath(a_dir_OlfaControlGUI));     % make sure OlfaControlGUI is on matlab path

%% Enter data file name
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
%a_thisfile_name = '2022-09-09_datafile_13'; a_this_note = 'A2 setpoint char'; f.pid_ylims = [-.01 .6]; f.flow_ylims = [-1 110];
% view delayed PID response
% 40cc
%f.x_lim = [197.758 247.4]; f.pid_ylims = [-.01 .35]; f.flow_ylims = [-1 50]; a_this_note = 'A2 at 40 sccm';
% 50cc
%f.x_lim = [250 320];
%a_thisfile_name = '2022-09-09_datafile_14'; a_this_note = 'A6 setpoint char'; f.pid_ylims = [-.1 7];
%a_thisfile_name = '2022-09-09_datafile_15'; a_this_note = 'A6 setpoint char'; %f.pid_ylims = [-.1 7]; plot_opts.plot_flow_as_sccm = 'yes';
% flow calibration
%{
%a_thisfile_name = '2022-09-12_datafile_00'; a_this_note = 'A2 flow calibration (automated)'; %plot_opts.plot_flow_as_sccm = 'no';
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

%a_thisfile_name = '2023-09-15_datafile_00';
%a_thisfile_name = '2023-09-15_datafile_01';
%a_thisfile_name = '2023-09-15_datafile_02';
%a_thisfile_name = '2023-09-15_datafile_03'; f.flow_ylims = [-5 100];
%a_thisfile_name = '2023-09-15_datafile_04';% f.flow_ylims = [-5 100];
%a_thisfile_name = '2023-09-15_datafile_05';
%a_thisfile_name = '2023-09-15_datafile_06';
%a_thisfile_name = '2023-09-15_datafile_07';
%a_thisfile_name = '2023-09-15_datafile_08';
%a_thisfile_name = '2023-09-15_datafile_09';
%a_thisfile_name = '2023-09-15_datafile_10';
%a_thisfile_name = '2023-09-15_datafile_11';
%a_thisfile_name = '2023-09-15_datafile_12';
%a_thisfile_name = '2023-09-15_datafile_13';
%a_thisfile_name = '2023-09-15_datafile_14';
%a_thisfile_name = '2023-09-15_datafile_15';
%a_thisfile_name = '2023-09-15_datafile_16';

%a_thisfile_name = '2023-09-18_datafile_07';
%a_thisfile_name = '2023-09-18_datafile_08';
%a_thisfile_name = '2023-09-19_datafile_07';
%a_thisfile_name = '2023-09-19_datafile_08'; %plot_opts.plot_flow_as_sccm = 'no'; f.x_lim = [3 35];

%a_thisfile_name = '2023-09-21_datafile_02';
%a_thisfile_name = '2023-09-21_datafile_03'; plot_opts.ctrl = 'no';
%a_thisfile_name = '2023-09-21_datafile_04'; plot_opts.ctrl = 'no';
%a_thisfile_name = '2023-09-21_datafile_05'; plot_opts.ctrl = 'no';
%a_thisfile_name = '2023-09-21_datafile_07';
%a_thisfile_name = '2023-09-21_datafile_08';
%a_thisfile_name = '2023-09-21_datafile_09';
%a_thisfile_name = '2023-09-21_datafile_10';
%a_thisfile_name = '2023-09-21_datafile_11';
%a_thisfile_name = '2023-09-21_datafile_01';% f.x_lim = [0 32];
%a_thisfile_name = '2023-09-26_datafile_00'; plot_opts.plot_flow_as_sccm = 'no'; f.flow_ylims = [190 218]; f.ctrl_ylims = [119 141];
%a_thisfile_name = '2023-09-26_datafile_01'; plot_opts.plot_flow_as_sccm = 'no'; f.flow_ylims = [190 218]; f.ctrl_ylims = [100 130];
%a_thisfile_name = '2023-09-26_datafile_02'; plot_opts.plot_flow_as_sccm = 'no'; f.flow_ylims = [190 218]; f.ctrl_ylims = [119 141];
%a_thisfile_name = '2023-09-26_datafile_03'; plot_opts.plot_flow_as_sccm = 'no'; f.flow_ylims = [190 218]; f.ctrl_ylims = [119 141];
%a_thisfile_name = '2023-09-26_datafile_04'; plot_opts.plot_flow_as_sccm = 'no'; f.ctrl_ylims = [139 181];

%a_thisfile_name = '2023-09-26_datafile_05'; plot_opts.plot_flow_as_sccm = 'no'; f.x_lim = [3 40];
%a_thisfile_name = '2023-09-19_datafile_08'; plot_opts.plot_flow_as_sccm = 'no'; f.x_lim = [3 35];

%a_thisfile_name = '2023-10-02_datafile_00'; plot_opts.ctrl = 'no';
%a_thisfile_name = '2023-10-03_datafile_00'; plot_opts.ctrl = 'yes'; plot_opts.plot_flow_as_sccm = 'no'; f.flow_ylims = [856 879];
%a_thisfile_name = '2023-10-11_datafile_06'; plot_opts.ctrl = 'yes'; 
%a_thisfile_name = '2023-10-11_datafile_07'; plot_opts.ctrl = 'yes';
%a_thisfile_name = '2023-10-11_datafile_08'; plot_opts.ctrl = 'yes';
%a_thisfile_name = '2023-10-11_datafile_09'; plot_opts.ctrl = 'yes';
%a_thisfile_name = '2023-10-11_datafile_10'; plot_opts.ctrl = 'yes';
%a_thisfile_name = '2023-10-11_datafile_11'; plot_opts.ctrl = 'yes';
%a_thisfile_name = '2023-10-11_datafile_12'; plot_opts.ctrl = 'yes';
%a_thisfile_name = '2023-10-11_datafile_13'; plot_opts.ctrl = 'yes';
%a_thisfile_name = '2023-10-11_datafile_14'; plot_opts.ctrl = 'yes';
%a_thisfile_name = '2023-10-11_datafile_15'; plot_opts.ctrl = 'yes';
%a_thisfile_name = '2023-10-11_datafile_16'; plot_opts.ctrl = 'yes';
%a_thisfile_name = '2023-10-11_datafile_17'; plot_opts.ctrl = 'yes';
%f.ctrl_ylims = [140 200]; f.flow_ylims = [30 190];
%a_thisfile_name = '2023-10-11_datafile_18'; plot_opts.ctrl = 'yes';
a_thisfile_name = '2024-01-19_datafile_00';
a_thisfile_name = '2024-08-27_datafile_00';

%f.flow_ylims = [-5 150];
%f.pid_ylims = [-.1 7];
%f.position = [166 600 775 275];     % for OneNote
f.position = [166 210 1300 600];    % for PowerPoint
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
    
    % x limits
    xlabel('Time (s)');
    if ~isempty(f.x_lim)
        xlim(f.x_lim);
    else
        t_end = data_time_raw(end,1);
        xlim([0 t_end]);
    end
    
    %% Plot: olfa flow
    % for each vial
    for i=1:length(d_olfa_flow)
        if contains(d_olfa_flow(i).vial_num,'E1')
            this_color = E1_flow;
        else
            this_color = f.colors{i};
        end
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

        p = plot(d_olfa_flow_x,d_olfa_flow_y);
        %p = scatter(d_olfa_flow_x,d_olfa_flow_y,'filled');
        p.LineWidth = f.flow_width;
        p.DisplayName = [d_olfa_flow(i).vial_num ' flow'];
        if ~isempty(this_color); p.Color = this_color; end
        %p.Color = f.colors{i};
    end
    
    %% Plot: olfa ctrl
    if strcmp(plot_opts.ctrl,'yes')
        % for each vial
        for i=1:length(d_olfa_flow)
            this_color = E1_ctrl;
            %if contains(d_olfa_flow(i).vial_num,'E1'); this_color = E1_ctrl;
            %else; this_color = f.colors{i}; end
            if strcmp(plot_opts.ctrl_as_voltage,'yes')        
                % plot as voltage
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
                % plot as integer
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