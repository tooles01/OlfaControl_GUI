%Plot average olfa flow vs. pid (for each trial, aka OV event)
%  
%Required Input:
%   a_thisfile_name - file name
%
%Data to plot:
%   olfa_flow       - flow values on left yaxis
%   olfa_ctrl       - ctrl values on right yaxis
%   pid             - pid data on right yaxis
%
%Units:
%   flow_in_SCCM    - flow units in SCCM (default==yes) 
%   ctrl_in_V       - ctrl units in V (default=integers)
%   plot_in_minutes - timescale in minutes (default==seconds)
%
%Axis Limits:
%   pid_lims        - Axis limits for PID
%   flow_lims       - Axis limits for Olfa flow (SCCM)
%   flow_lims_int   - Axis limits for Olfa flow (integer)
%
%Data Manipulation:
%   time_to_cut
%
%Additional Figures:
%   plot_over_time
%   plot_all
%
%Plot Options:
%   fig_position
%   legend_on
%   show_error_bars
%
%For individual event plots:
%   x_lim
%   plot_x_lines
%   show_pid_mean
%   show_flow_mean


%%

function a_plot_spt_char(a_thisfile_name,plot_opts)
    
arguments
        a_thisfile_name             (1,1) string = '-'
        
        % Data to plot
        plot_opts.olfa_flow         (1,1) string = 'yes'
        plot_opts.olfa_ctrl         (1,1) string = 'no'
        plot_opts.pid               (1,1) string = 'yes'
        
        % Units
        plot_opts.flow_in_SCCM      (1,1) string = 'yes'    % plot olfa as sccm or int
        plot_opts.ctrl_in_V         (1,1) string = 'no'     % plot ctrl as int or voltage
        plot_opts.plot_in_minutes   (1,1) string = 'no'

        % Axis Limits
        plot_opts.pid_lims          (1,:) double = [0 3]
        plot_opts.flow_lims         (1,:) double = [0 105]
        plot_opts.flow_lims_int     (1,:) double = [0 1024]
        
        % Data Manipulation
        plot_opts.time_to_cut       (1,:) double = 0        % time to cut off beginning of each section
        
        % Additional Figures
        plot_opts.plot_over_time    (1,1) string = 'no'     % plot the entire trial over time
        plot_opts.plot_all          (1,1) string = 'no'     % plot each event individually
        
        % Plot options:
        plot_opts.fig_position      (1,:) double = [1050 230 812 709]   % flow v. PID plot
        plot_opts.legend_on         (1,:) string = 'yes'
        plot_opts.show_error_bars   (1,1) string = 'yes'
        
        % For individual event plots
        plot_opts.x_lim             (1,:) double = []
        plot_opts.show_pid_mean     (1,1) string = 'no'     % Overlay mean PID value on plot
        plot_opts.show_flow_mean    (1,1) string = 'no'     % Overlay mean flow value on plot
        plot_opts.show_x_lines      (1,1) string = 'no'     % Overlay x-lines of where the mean was calculated from
    end

%%
set(0,'DefaultTextInterpreter','none')

%% Display Variables
f = struct();   % struct containing all figure variables
f.flow_width = 1;
f.pid_width = 1.5;
f.dot_size = 60;
f.PID_color = '#77AC30';

% Vial colors
f.colors{1} = '#0072BD';
f.colors{2} = '#A2142F';
f.colors{3} = '#D95319';
f.colors{4} = '#7E2F8E';

% For plot over time
f0.position = [166 210 1300 600];   % wide - for over time
f.position = [175 230 412 350];     % small - for individual event plots
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

%% Load *.mat file

% Full directory for .mat file
dir_this_mat_file = strcat(a_dir_OlfaControlGUI,'\analysis\data (.mat files)\',a_thisfile_name,'.mat');

try
    load(dir_this_mat_file,'d_olfa_flow','a_this_note','data_time_raw','data_pid');

    %% Cut additional time off (& recalculate stats)
    % For each vial
    for i=1:length(d_olfa_flow)
        % for each OV event
        for e=1:length(d_olfa_flow(i).events.OV_keep)
            % cut down the sections
            this_flow_int_data = d_olfa_flow(i).events.OV_keep(e).data.flow_int;
            this_flow_sccm_data = d_olfa_flow(i).events.OV_keep(e).data.flow_sccm;
            this_pid_data = d_olfa_flow(i).events.OV_keep(e).data.pid;
            start_time = d_olfa_flow(i).events.OV_keep(e).t_event + plot_opts.time_to_cut;
            end_time = this_pid_data(end,1);
            this_flow_int_data = get_section_data(this_flow_int_data,start_time,end_time);
            this_flow_sccm_data = get_section_data(this_flow_sccm_data,start_time,end_time);
            this_pid_data = get_section_data(this_pid_data,start_time,end_time);

            % recalculate the mean
            this_flow_int_mean = mean(this_flow_int_data(:,2));
            this_flow_sccm_mean = mean(this_flow_sccm_data(:,2));
            this_pid_mean = mean(this_pid_data(:,2));
            this_flow_int_std = std(this_flow_int_data(:,2));
            this_flow_sccm_std = std(this_flow_sccm_data(:,2));
            this_pid_std = std(this_pid_data(:,2));

            % add these means back into the structure
            d_olfa_flow(i).events.OV_keep(e).flow_mean_int = this_flow_int_mean;
            d_olfa_flow(i).events.OV_keep(e).flow_mean_sccm = this_flow_sccm_mean;
            d_olfa_flow(i).events.OV_keep(e).pid_mean = this_pid_mean;
            d_olfa_flow(i).events.OV_keep(e).flow_std_int = this_flow_int_std;
            d_olfa_flow(i).events.OV_keep(e).flow_std_sccm = this_flow_sccm_std;
            d_olfa_flow(i).events.OV_keep(e).pid_std = this_pid_std;

            % add them to the int/sccm structs
            d_olfa_flow(i).int_means(e,1) = this_flow_int_mean;
            d_olfa_flow(i).int_means(e,2) = this_pid_mean;
            d_olfa_flow(i).sccm_means(e,1) = this_flow_sccm_mean;
            d_olfa_flow(i).sccm_means(e,2) = this_pid_mean;
        end
    end
    clearvars this_*

    %% If selected: Plot the whole thing over time
    if strcmp(plot_opts.plot_over_time,'yes')
        
        %% Create figure
        figTitle = a_thisfile_name;
        f1 = figure; f1.NumberTitle = 'off'; f1.Position = f0.position; hold on;
        f1.Name = a_thisfile_name;
        title(figTitle)
        subtitle(a_this_note)
        if strcmp(plot_opts.legend_on,'yes'); legend('Location','northwest'); end
        f1_ax = gca;
        
        % Set X-limits
        xlabel('Time (sec)');
        if ~isempty(plot_opts.x_lim)
            xlim(plot_opts.x_lim);
        else
            t_end = data_time_raw(end,1);
            xlim([0 t_end]);
        end
        
        %% Plot: Olfa flow
        % For each vial
        for i=1:length(d_olfa_flow)
            d_olfa_flow_x = [];
            d_olfa_flow_y = [];
            
            %% Get olfa flow data
            if strcmp(plot_opts.flow_in_SCCM,'yes')
                % Plot as SCCM
                if ~isempty(d_olfa_flow(i).flow.flow_sccm)
                    d_olfa_flow_x = d_olfa_flow(i).flow.flow_sccm(:,1);
                    d_olfa_flow_y = d_olfa_flow(i).flow.flow_sccm(:,2);
                    ylabel('Odor flow rate (SCCM)')
                    ylim(plot_opts.flow_lims);
                end
            else
                % Plot as integer
                if ~isempty(d_olfa_flow(i).flow.flow_int)
                    d_olfa_flow_x = d_olfa_flow(i).flow.flow_int(:,1);
                    d_olfa_flow_y = d_olfa_flow(i).flow.flow_int(:,2);
                    ylabel('Odor flow rate (integer values)')
                    ylim(plot_opts.flow_lims_int);
                end
            end
        end
        
        %% Plot olfa flow data
        try
            p = plot(d_olfa_flow_x,d_olfa_flow_y);
            p.LineWidth = f.flow_width;
            p.DisplayName = [d_olfa_flow(i).vial_num ' Flow'];
        % Error message in case no flow values available
        catch ME
            switch ME.identifier
                case 'MATLAB:emptyObjectDotAssignment'
                    disp(['---> No flow values available to plot for ' d_olfa_flow(i).vial_num])
                otherwise
                    rethrow(ME)
            end
        end
        %% Set axis color : unclear if this does anything (8/7/2025)
        try
            yyaxis left
            f1_ax.YColor = ax_color;
        catch ME    % in case olfa flow was not plotted
            disp(ME.identifier);
        end

        %% Plot: PID
        if ~isempty(data_pid)
            yyaxis right;
            colororder('#77AC30');  f1_ax.YColor = '#77AC30';
            if ~isempty(plot_opts.pid_lims)
                f1_ax.YLim = plot_opts.pid_lims;
            end
            ylabel('PID output (V)');
            p2 = plot(data_pid(:,1),data_pid(:,2),'DisplayName','PID');
            p2.LineWidth = f.pid_width;
        end
    end
    
    %% Plot: each section individually
    if strcmp(plot_opts.plot_all,'yes')
        time_around_event = 3;
        % For each vial
        for i=1:length(d_olfa_flow)        
            % since i don't have setpoint data let's do it by OV events
            % For each OV event
            for e=1:length(d_olfa_flow(i).events.OV_keep)
                t_beg_event = d_olfa_flow(i).events.OV_keep(e).t_event;  % actual time of OV
                t_end_event = d_olfa_flow(i).events.OV_keep(e).t_end;
                t_beg_plot = t_beg_event - time_around_event;
                t_end_plot = t_end_event + time_around_event;
        
                f1 = figure; f1.NumberTitle = 'off'; f1.Position = f.position; hold on;
                f1.Name = a_thisfile_name;
                if strcmp(plot_opts.legend_on,'yes'); legend('Location','northeast'); end
                f1_ax = gca;
                xlabel('Time (sec)');
                %figTitle = ['calculated mean from ' num2str(how_much_to_cut) 's into event'];
                %title(figTitle);
                
                %% Plot: Olfa flow
                if strcmp(plot_opts.flow_in_SCCM,'yes')
                    if ~isempty(d_olfa_flow(i).cal_table_name)
                        % Plot as SCCM
                        if ~isempty(d_olfa_flow(i).flow.flow_sccm)
                            ylabel('Odor flow rate (SCCM)')
    
                            % Get data for this section
                            this_flow_data_shifted = [];
                            this_flow_data = d_olfa_flow(i).flow.flow_sccm;
                            this_flow_data = get_section_data(this_flow_data,t_beg_plot,t_end_plot);
                            
                            % Shift x-axis so OV happens at t=0
                            this_flow_data_shifted(:,1) = this_flow_data(:,1) - t_beg_event;
                            this_flow_data_shifted(:,2) = this_flow_data(:,2);
                            
                            % Plot flow data
                            p = plot(this_flow_data_shifted(:,1),this_flow_data_shifted(:,2));
                            p.DisplayName = [d_olfa_flow(i).vial_num ' Flow'];
                            p.Color = f.colors{i};
                            ylim([plot_opts.flow_lims]);
                            
                            this_flow_val_sccm = d_olfa_flow(i).sccm_means(e,1);
                            if strcmp(plot_opts.show_flow_mean,'yes')
                                % Plot line at the mean
                                this_x_coord = [plot_opts.time_to_cut;d_olfa_flow(i).events.OV_keep(e).t_duration];
                                this_y_coord = [this_flow_val_sccm;this_flow_val_sccm];
                                p_flow_mean = plot(this_x_coord,this_y_coord,'LineWidth',4);
                                p_flow_mean.DisplayName = [d_olfa_flow.vial_num ' mean: ' num2str(round(this_flow_val_sccm,1)) ' sccm'];
                                p_flow_mean.Color = f.colors{i};
                            end
                        end
                    else
                        % Plot as integer - pls don't do this I didn't finish the script
                        if ~isempty(d_olfa_flow(i).flow.flow_int)
                            ylabel('Odor flow rate (integer values)')
                            p = plot(d_olfa_flow(i).flow.flow_int(:,1),d_olfa_flow(i).flow.flow_int(:,2));
                        end
                    end
                else
                    % Plot as integer
                    if ~isempty(d_olfa_flow(i).flow.flow_int)
                        ylabel('Odor flow rate (integer values)')
                        p = plot(d_olfa_flow(i).flow.flow_int(:,1),d_olfa_flow(i).flow.flow_int(:,2));
                    end
                end
                p.LineWidth = f.flow_width;
                p.DisplayName = [d_olfa_flow(i).vial_num ' Flow'];
        
                %% Plot: PID
                if ~isempty(data_pid)
                    yyaxis right; colororder('#77AC30');  f1_ax.YColor = '#77AC30';
                    ylabel('PID output (V)');
                    if ~isempty(plot_opts.pid_lims);  ylim([plot_opts.pid_lims]); end
                    this_pid_data = get_section_data(data_pid,t_beg_plot,t_end_plot);
                    this_pid_data_shifted = [];
                    this_pid_data_shifted(:,1) = this_pid_data(:,1) - t_beg_event;
                    this_pid_data_shifted(:,2) = this_pid_data(:,2);
                    p2 = plot(this_pid_data_shifted(:,1),this_pid_data_shifted(:,2),'DisplayName','PID');
                    p2.LineWidth = f.pid_width;
                    
                    this_pid_val = d_olfa_flow(i).sccm_means(e,2);
                    % Plot line at the mean
                    if strcmp(plot_opts.show_pid_mean,'yes')
                        this_x_coord = [plot_opts.time_to_cut;d_olfa_flow(i).events.OV_keep(e).t_duration];
                        p_pid_mean = plot(this_x_coord,[this_pid_val;this_pid_val],'LineWidth',4);% TODO error if show_flow_mean is not selected
                        p_pid_mean.LineStyle = '-';
                        p_pid_mean.DisplayName = ['PID mean: ' num2str(round(this_pid_val,2)) ' V'];
                        p_pid_mean.Color = f1_ax.YColor;
                    end
                end
                
                % Set x lims
                xlim([-time_around_event this_flow_data_shifted(end,1)])
                
                % Mark where we calculated the mean from
                if strcmp(plot_opts.show_x_lines,'yes')
                    p_start_time = plot_opts.time_to_cut;
                    p_end_time = d_olfa_flow(i).events.OV_keep(e).t_duration;
                    p_t_start = xline(p_start_time,'HandleVisibility','off');
                    p_t_end = xline(p_end_time,'HandleVisibility','off');
                end
                
                figTitle = [num2str(round(this_flow_val_sccm,1)) ' sccm (calculated mean from ' num2str(plot_opts.time_to_cut) 's into event)'];
                title(a_thisfile_name); subtitle(figTitle);
            end
        end
        
    end
    
    %% Plot: Flow v. PID
    
    % Create figure
    f2 = figure; f2.NumberTitle = 'off'; f2.Position = plot_opts.fig_position; hold on;
    f2.Name = 'FLOW v. PID: '+ a_thisfile_name;
    title(a_thisfile_name);
    subtitle(a_this_note);
    if strcmp(plot_opts.legend_on,'yes'); legend('Location','northwest'); end
    f2_ax = gca;
    ylabel('PID reading (V)')
    if ~isempty(plot_opts.pid_lims); ylim(plot_opts.pid_lims); end
    
    % Plot the mean values for this vial
    % For each vial
    for i=1:length(d_olfa_flow)
        if strcmp(plot_opts.flow_in_SCCM,'yes')
            % Plot as SCCM
            if ~isempty(d_olfa_flow(i).sccm_means)
                p = scatter(d_olfa_flow(i).sccm_means(:,1),d_olfa_flow(i).sccm_means(:,2),f.dot_size,'filled');
                xlabel('Odor flow rate (SCCM)');
                f2_ax.XLim = plot_opts.flow_lims;
            end
        else
            % Plot as integer
            if ~isempty(d_olfa_flow(i).int_means)
                p = scatter(d_olfa_flow(i).int_means(:,1),d_olfa_flow(i).int_means(:,2),f.dot_size,'filled');
                xlabel('Odor flow rate (int)');
                f2_ax.XLim = plot_opts.flow_lims_int;
            end
        end
        p.DisplayName = d_olfa_flow(i).vial_num;
        %p.MarkerFaceColor = f.colors{i};
        p.MarkerFaceColor = f.PID_color;

        %% Plot: Error bars
        if strcmp(plot_opts.show_error_bars,'yes')

            % Mean values
            if strcmp(plot_opts.flow_in_SCCM,'no')
                x = d_olfa_flow(i).int_means(:,1);
                y = d_olfa_flow(i).int_means(:,2);
            else
                x = d_olfa_flow(i).sccm_means(:,1);
                y = d_olfa_flow(i).sccm_means(:,2);
            end

            % Standard deviations
            for e=1:length(d_olfa_flow(i).sccm_means)
                % Flow
                if strcmp(plot_opts.flow_in_SCCM,'no'); flow_std = d_olfa_flow(i).events.OV_keep(e).flow_std_int;
                else;                                   flow_std = d_olfa_flow(i).events.OV_keep(e).flow_std_sccm; end
                % PID
                pid_std = d_olfa_flow(i).events.OV_keep(e).pid_std;
                
                xneg(e,1) = flow_std/2;
                xpos(e,1) = flow_std/2;
                yneg(e,1) = pid_std/2;
                ypos(e,1) = pid_std/2;

            end

            % Plot error bars
            e = errorbar(x,y,yneg,ypos,xneg,xpos,'o');
            e.HandleVisibility = 'off';
            e.Color = p.MarkerFaceColor;
        end

    end
    clearvars x xneg xpos y yneg ypos    

%% error catch in case file has not been parsed yet
catch ME
    switch ME.identifier
        case 'MATLAB:load:couldNotReadFile'
            disp(['---> ' a_thisfile_name,' has not been parsed yet: run analysis_get_and_parse_files.m first'])
        otherwise
            rethrow(ME)
    end
end

end