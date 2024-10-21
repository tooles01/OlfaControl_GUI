%Plot average olfa flow vs. pid (for each trial, aka OV event)
%  
%Required Input:
%   a_thisfile_name - file name
%
%Plot Options:
%   olfa_flow       - flow values on left yaxis
%   olfa_ctrl       - ctrl values on right yaxis
%   pid             - pid data on right yaxis
%
%   flow_in_SCCM    - flow units in SCCM (default==yes) 
%   ctrl_in_V       - ctrl units in V (default=integers)
%   plot_in_minutes - timescale in minutes (default==seconds)
%
%   pid_lims
%   olfa_lims_sccm
%
%   show_error_bars
%   time_to_cut
%
%   plot_over_time
%   plot_all
%
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
        plot_opts.pid_lims          (1,:) double = [0 7]
        plot_opts.olfa_lims_sccm    (1,:) double = [0 105]
        
        % Other
        plot_opts.show_error_bars   (1,1) string = 'no'
        plot_opts.time_to_cut       (1,:) double = 0        % time to cut off beginning of each section
        
        % Additional Figures
        plot_opts.plot_over_time    (1,1) string = 'no'     % plot the entire trial over time
        plot_opts.plot_all          (1,1) string = 'no'     % plot each event individually
        
        % For individual event plots
        plot_opts.plot_x_lines      (1,1) string = 'no'     % Overlay x-lines of where the mean was calculated from
        plot_opts.show_pid_mean     (1,1) string = 'no'     % Overlay mean PID value on plot
        plot_opts.show_flow_mean    (1,1) string = 'no'     % Overlay mean flow value on plot
        
    end

%%
%close all
set(0,'DefaultTextInterpreter','none')

%% Display variables
f = struct();   % struct containing all figure variables
f.x_lim = [];
f.olfa_lims_int = [];
f.flow_width = 1;
f.pid_width = 1.5;
f.dot_size = 60;

% Vial colors
f.colors{1} = '#0072BD';
f.colors{2} = '#A2142F';
f.colors{3} = '#D95319';
f.colors{4} = '#7E2F8E';

%f.position = [140 230 1355 686];   % wide - for over time
%f.position = [166 230 650 600];    % for PowerPoint (1/2 size)
%f.position = [960 230 780 686];    % not that small
f.position = [175 230 812 709];
f.f2_position = [1050 230 812 709];


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


%% Load *.mat file

% Full directory for .mat file
dir_this_mat_file = strcat(a_dir_OlfaControlGUI,'\analysis\data (.mat files)\',a_thisfile_name,'.mat');

try
    load(dir_this_mat_file);
    %{
    %% get mean flow/pid for each event section - if they were to be cut shorter    % TODO make this a plot option?
    % for each vial
    for i=1:length(d_olfa_flow)
        this_vial_int_means = [];
        this_vial_sccm_means = [];
    
        if ~isempty(d_olfa_flow(i).events.OV)       % in case this vial was recorded, but has no OV events
            
            % for each event
            for e=1:length(d_olfa_flow(i).events.OV)
                
                % cut section shorter
                how_much_to_cut = 12;

                e_t_start = d_olfa_flow(i).events.OV(e).t_event + how_much_to_cut;
                e_duration = d_olfa_flow(i).events.OV(e).t_duration;
                e_t_end = d_olfa_flow(i).events.OV(e).t_end;

                e_olfa_flow_int = d_olfa_flow(i).flow.flow_int;
                e_olfa_flow_sccm = d_olfa_flow(i).flow.flow_sccm;
                e_pid_data = data_pid;

                e_this_section_olfa_flow_int = get_section_data(e_olfa_flow_int,e_t_start,e_t_end);
                e_this_section_olfa_flow_sccm = get_section_data(e_olfa_flow_sccm,e_t_start,e_t_end);
                e_this_section_pid_data = get_section_data(e_pid_data,e_t_start,e_t_end);

                e_int_mean = mean(e_this_section_olfa_flow_int(:,2));
                e_sccm_mean = mean(e_this_section_olfa_flow_sccm(:,2));
                e_pid_mean = mean(e_this_section_pid_data(:,2));
                
                %{                
                % calculate means
                int_mean = mean(d_olfa_flow(i).events.OV(e).flow_int(:,2));
                sccm_mean = mean(d_olfa_flow(i).events.OV(e).flow_sccm(:,2));
                pid_mean = mean(d_olfa_flow(i).events.OV(e).pid(:,2));
                
                d_olfa_flow(i).events.OV(e).int_mean = int_mean;
                d_olfa_flow(i).events.OV(e).sccm_mean = sccm_mean;
                d_olfa_flow(i).events.OV(e).pid_mean = pid_mean;

                % matrix of (int_mean, pid_mean) for all events
                int_pair = [int_mean pid_mean];
                this_vial_int_means = [this_vial_int_means;int_pair];
                sccm_pair = [sccm_mean pid_mean];
                this_vial_sccm_means = [this_vial_sccm_means;sccm_pair];
                %}
                
                d_olfa_flow(i).events.OV(e).int_mean = e_int_mean;
                d_olfa_flow(i).events.OV(e).sccm_mean = e_sccm_mean;
                d_olfa_flow(i).events.OV(e).pid_mean = e_pid_mean;
                
                % matrix of (int_mean, pid_mean) for all events
                int_pair = [e_int_mean e_pid_mean];
                this_vial_int_means = [this_vial_int_means;int_pair];
                sccm_pair = [e_sccm_mean e_pid_mean];
                this_vial_sccm_means = [this_vial_sccm_means;sccm_pair];
            end

        end

        d_olfa_flow(i).int_means = this_vial_int_means;
        d_olfa_flow(i).sccm_means = this_vial_sccm_means;
    
    end
    clearvars *_mean
    %}

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
        figTitle_main = a_thisfile_name;
        if ~strcmp(a_this_note, ''); figTitle_main = append(figTitle_main, ': ',  a_this_note); end
        
        f1 = figure; f1.NumberTitle = 'off'; f1.Position = f.position; hold on;
        f1.Name = a_thisfile_name; title(figTitle_main)
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
        
        %% Plot: Olfa flow
        % For each vial
        for i=1:length(d_olfa_flow)
            % Plot as SCCM or integer values
            if strcmp(plot_opts.flow_in_SCCM,'yes')
                % if this vial has a calibration table
                if ~isempty(d_olfa_flow(i).cal_table_name)
                    % Plot as SCCM
                    if ~isempty(d_olfa_flow(i).flow.flow_sccm)
                        ylabel('Olfa flow (sccm)')
                        p = plot(d_olfa_flow(i).flow.flow_sccm(:,1),d_olfa_flow(i).flow.flow_sccm(:,2));
                        if ~isempty(plot_opts.olfa_lims_sccm); ylim(plot_opts.olfa_lims_sccm)
                        else; ylim([-5 150]); end
                    end
                else
                    % Plot as integer
                    if ~isempty(d_olfa_flow(i).flow.flow_int)
                        ylabel('Olfa flow (integer values)')
                        p = plot(d_olfa_flow(i).flow.flow_int(:,1),d_olfa_flow(i).flow.flow_int(:,2));
                        if ~isempty(f.olfa_lims_int); ylim(f.olfa_lims_int)
                        else; ylim([0 1024]); end
                    end
                end
                p.LineWidth = f.flow_width;
                p.DisplayName = [d_olfa_flow(i).vial_num ' flow'];
                
            else
                % Plot as integer
                if ~isempty(d_olfa_flow(i).flow.flow_int)
                    ylabel('Olfa flow (integer values)')
                    p = plot(d_olfa_flow(i).flow.flow_int(:,1),d_olfa_flow(i).flow.flow_int(:,2));
                    p.LineWidth = f.flow_width;
                    p.DisplayName = [d_olfa_flow(i).vial_num ' flow'];
                    if ~isempty(f.olfa_lims_int); ylim(f.olfa_lims_int)
                    else; ylim([0 1024]); end
                end
            end
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
    
    
    %% If selected: Plot each section individually
    if strcmp(plot_opts.plot_all,'yes')
        time_around_event = 3;
        % for each vial
        for i=1:length(d_olfa_flow)
            this_vial = d_olfa_flow(i).vial_num;
        
            % since i don't have setpoint data let's do it by OV events
            % for each OV event
            for e=1:length(d_olfa_flow(i).events.OV_keep)
                t_beg_event = d_olfa_flow(i).events.OV_keep(e).t_event;  % actual time of OV
                t_end_event = d_olfa_flow(i).events.OV_keep(e).t_end;
                t_beg_plot = t_beg_event - time_around_event;
                t_end_plot = t_end_event + time_around_event;
        
                f1 = figure; f1.NumberTitle = 'off'; f1.Position = f.position; hold on;
                f1.Name = a_thisfile_name;
                legend('Location','northeast');
                f1_ax = gca;
                xlabel('Time (s)');
                %figTitle = ['calculated mean from ' num2str(how_much_to_cut) 's into event'];
                %title(figTitle);
                
                % Plot: Olfa flow
                if strcmp(plot_opts.flow_in_SCCM,'yes')
                    if ~isempty(d_olfa_flow(i).cal_table_name)
                        % Plot as SCCM
                        if ~isempty(d_olfa_flow(i).flow.flow_sccm)
                            ylabel('Olfa flow (sccm)')
    
                            % get data for this section
                            this_flow_data_shifted = [];
                            this_flow_data = d_olfa_flow(i).flow.flow_sccm;
                            this_flow_data = get_section_data(this_flow_data,t_beg_plot,t_end_plot);
                            
                            % shift x-axis so OV happens at t=0
                            this_flow_data_shifted(:,1) = this_flow_data(:,1) - t_beg_event;
                            this_flow_data_shifted(:,2) = this_flow_data(:,2);
                            
                            % plot it
                            p = plot(this_flow_data_shifted(:,1),this_flow_data_shifted(:,2));
                            p.DisplayName = [d_olfa_flow(i).vial_num ' flow'];
                            p.Color = f.colors{i};
                            ylim([plot_opts.olfa_lims_sccm]);
                            
                            this_flow_val_sccm = d_olfa_flow(i).sccm_means(e,1);
                            if strcmp(plot_opts.show_flow_mean,'yes')
                                % plot line at the mean
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
        
                % Plot: PID
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
                    % plot line at the mean
                    if strcmp(plot_opts.show_pid_mean,'yes')
                        p_pid_mean = plot(this_x_coord,[this_pid_val;this_pid_val],'LineWidth',4);% TODO error if show_flow_mean is not selected
                        p_pid_mean.LineStyle = '-';
                        p_pid_mean.DisplayName = ['PID mean: ' num2str(round(this_pid_val,2)) ' V'];
                        p_pid_mean.Color = f1_ax.YColor;
                    end
                end
                
                % set x lims
                xlim([-time_around_event this_flow_data_shifted(end,1)])
    
                % mark where we calculated the mean from
                if strcmp(plot_opts.plot_x_lines,'yes')
                    p_start_time = plot_opts.time_to_cut;
                    p_end_time = d_olfa_flow(i).events.OV_keep(e).t_duration;
                    p_t_start = xline(p_start_time,'HandleVisibility','off');
                    p_t_end = xline(p_end_time,'HandleVisibility','off');
                end
                
                figTitle = [num2str(round(this_flow_val_sccm,1)) ' sccm (calculated mean from ' num2str(plot_opts.time_to_cut) 's into event)'];
                title(a_thisfile_name); subtitle(figTitle);
                %{
                a = [num2str(round(this_flow_val_sccm,1)) ' sccm ' a_thisfile_name '.png'];
                saveas(f1,a);
                %}
            end
        end
        
    end
    
    %% Plot Flow v. PID
    f2 = figure; f2.NumberTitle = 'off'; f2.Position = f.f2_position; hold on;
    f2.Name = ['FLOW v. PID: ',a_thisfile_name];
    title(['FLOW v. PID:     ', a_thisfile_name]);
    subtitle(a_this_note);
    legend('Location','northwest');
    f2_ax = gca;
    ylabel('PID (V)')
    if ~isempty(plot_opts.pid_lims); ylim(plot_opts.pid_lims); end
    
    % For each vial
    for i=1:length(d_olfa_flow)
        if ~isempty(d_olfa_flow(i).int_means)
            % Plot the values for this vial
            if strcmp(plot_opts.flow_in_SCCM,'no')
                p = scatter(d_olfa_flow(i).int_means(:,1),d_olfa_flow(i).int_means(:,2),f.dot_size,'filled');
                xlabel('Olfa flow (int)');
                if ~isempty(f.olfa_lims_int); f2_ax.XLim = f.olfa_lims_int; end
            end
            if strcmp(plot_opts.flow_in_SCCM,'yes')
                p = scatter(d_olfa_flow(i).sccm_means(:,1),d_olfa_flow(i).sccm_means(:,2),f.dot_size,'filled');
                xlabel('Olfa flow (sccm)');
                if ~isempty(plot_opts.olfa_lims_sccm); f2_ax.XLim = plot_opts.olfa_lims_sccm; end
            end
            p.DisplayName = d_olfa_flow(i).vial_num;
            p.MarkerFaceColor = f.colors{i};

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
    end

    %% plot the error bars
    %{
    for i=1:length(d_olfa_flow)
        if ~isempty(d_olfa_flow(i).int_means)
            x = d_olfa_flow(i).sccm_means(:,1);
            y = d_olfa_flow(i).sccm_means(:,2);

            if strcmp(plot_opts.show_error_bars,'yes')

                for e=1:length(d_olfa_flow(i).sccm_means)
                    flow_std = d_olfa_flow(i).events.OV_keep(e).flow_std_sccm;
                    pid_std = d_olfa_flow(i).events.OV_keep(e).pid_std;

                    xneg(e,1) = flow_std/2;
                    xpos(e,1) = flow_std/2;
                    yneg(e,1) = pid_std/2;
                    ypos(e,1) = pid_std/2;

                end

                e = errorbar(x,y,yneg,ypos,xneg,xpos,'o');
                e.HandleVisibility = 'off';
                e.Color = p.MarkerFaceColor;

            end
    %}
            %{
            % for each event
            for e=1:length(d_olfa_flow(i).events.OV_keep)

                % flow error bars
                if strcmp(plot_opts.show_error_bars,'yes')
                    if strcmp(plot_opts.flow_in_SCCM,'no')
                        flow_mean = d_olfa_flow(i).events.OV_keep(e).flow_mean_int;
                        flow_std_dev = d_olfa_flow(i).events.OV_keep(e).flow_std_int;
                        flow_sample_size = length(d_olfa_flow(i).events.OV_keep(e).data.flow_int);
                        flow_sem = flow_std_dev / sqrt(flow_sample_size);
                        pid_mean = d_olfa_flow(i).events.OV_keep(e).pid_mean;
                        e_flow = errorbar(flow_mean,pid_mean,flow_sem,'horizontal');
                    else
                        flow_mean = d_olfa_flow(i).events.OV_keep(e).flow_mean_sccm;
                        flow_std_dev = d_olfa_flow(i).events.OV_keep(e).flow_std_sccm;
                        flow_sample_size = length(d_olfa_flow(i).events.OV_keep(e).data.flow_sccm);
                        flow_sem = flow_std_dev / sqrt(flow_sample_size);
                        pid_mean = d_olfa_flow(i).events.OV_keep(e).pid_mean;
                        e_flow = errorbar(flow_mean,pid_mean,flow_sem,'horizontal','DisplayName','off');
                        %e_flow.DisplayName = '';
                    end
                    e_flow.Color = [0 .4471 .7412];
                end

                % pid error bars
                if strcmp(plot_opts.pid_error_bars,'yes')                        
                    % TODO fix the sample size here
                    % or change the calculated value to the median maybe
                    pid_std_dev = d_olfa_flow(i).events.OV_keep(e).pid_std;
                    pid_sample_size = length(d_olfa_flow(i).events.OV_keep(e).data.pid);
                    pid_sem = pid_std_dev / sqrt(pid_std_dev);
                    e_pid = errorbar(flow_mean,pid_mean,pid_sem,'vertical');%,'DisplayName','off');
                    e_pid.Color = [0 .4471 .7412];
                    %e_pid.DisplayName = '';
                end
            end
            %}
            
        %end
    %end

    clearvars x xneg xpos y yneg ypos


    %% save this shit i want 10/30/2023
    %{
    save_file_name = a_thisfile_name + "_" + d_olfa_flow.vial_num;
    if ~isfile(save_file_name)
        save(save_file_name,'d_olfa_flow','data_pid','d_olfa_data_combined');
        disp("saved " + save_file_name)
    else
        delete(save_file_name)
        save(save_file_name,'d_olfa_flow','data_pid','d_olfa_data_combined');
        disp("rewrote " + save_file_name)
    end
    %}
    
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