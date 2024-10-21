%% analysis_plot_olfa_and_pid
% plot olfa flow & pid values over time
%% THIS IS PROBABLY USELESS NOW since I updated analysis_plot_olfa_and_pid - ST 09/19/2024
% you could still copy the concept tho onto the updated file but this file itself is no good


%%
clearvars
set(0,'DefaultTextInterpreter','none')
close all
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
plot_opts.plot_flow_as_sccm = 'no';
% **if datafile does not have calibration tables listed in header, plot will be in ints regardless

% pick one of these
plot_opts.pid = 'yes';
plot_opts.output_flow = 'no';
plot_opts.ctrl = 'no';
plot_opts.ctrl_as_voltage = 'no';


plot_opts.plot_flow_as_sccm = 'yes';
%f.flow_ylims = [-5 150];
%f.pid_ylims = [-.1 7];
%f.position = [549 166 1353 684];
%f.position = [166 600 775 275];     % for OneNote
f.position = [166 450 1560 424];     % for OneNote
%f.position = [166 210 1300 600];    % for PowerPoint
f.pid_width = 1.5;

%% enter date
%a_thisfile_date = '2022-08-29';
a_thisfile_date = '2022-09-07';
a_thisfile_date = '2022-09-09';


% for each file with this date hmmmmmmm
matlab_files_dir = strcat(pwd,'\','data (.mat files)');
files_this_date = dir(fullfile(matlab_files_dir,strcat(a_thisfile_date,'*')));

for p=1:length(files_this_date)
    
    %% load .mat file
    a_thisfile_name = files_this_date(p).name;
    
    % full directory for .mat file
    dir_this_mat_file = strcat(files_this_date(p).folder,'\',a_thisfile_name);

    %% plot
    try
        load(dir_this_mat_file);
        clearvars mat_* dir_*
        
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
            if strcmp(plot_opts.plot_flow_as_sccm,'yes')
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
        
        %% plot: pid
        if strcmp(plot_opts.pid,'yes')
            if ~isempty(data_pid)
                yyaxis right;
                colororder('#77AC30');  f1_ax.YColor = '#77AC30';
                if ~isempty(f.pid_ylims)
                    f1_ax.YLim = f.pid_ylims;
                end
                ylabel('PID output (V)');
                p2 = plot(data_pid(:,1),data_pid(:,2),'DisplayName','PID');
                p2.LineWidth = f.pid_width;
                if ~isempty(f.pid_ylims)
                    ylim(f.pid_ylims);
                end
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
end