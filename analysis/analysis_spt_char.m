%% analysis_spt_char

% plot flow v. pid graph
%%
clearvars
%close all
%#ok<*SAGROW>
%#ok<*AGROW>
set(0,'DefaultTextInterpreter','none')

%% enter directory for this computer
%a_dir_OlfaEngDropbox = 'C:\Users\Admin\Dropbox (NYU Langone Health)\OlfactometerEngineeringGroup (2)';
a_dir_OlfaEngDropbox = 'C:\Users\SB13FLLT004\Dropbox (NYU Langone Health)\OlfactometerEngineeringGroup (2)';
a_dir_OlfaControlGUI = strcat(a_dir_OlfaEngDropbox,'\Control\a_software\OlfaControl_GUI');

%% select shit to plot
plot_opts = struct();
plot_opts.plot_flow_as_sccm = 'yes'; % plot olfa as sccm or int

plot_opts.all_points = 'yes';   % TODO this does nothing right now
plot_opts.plot_over_time = 'no';    % plot the entire trial over time
plot_opts.plot_all = 'yes'; % plot each individually
plot_opts.plot_x_lines = 'no';   % x lines of where the mean was calculated from
plot_opts.show_pid_mean = 'yes';
plot_opts.show_flow_mean = 'yes';
plot_opts.flow_error_bars = 'no';
plot_opts.pid_error_bars = 'no';

%% display variables
f.x_lim = [];
f.olfa_lims_int = [];
f.olfa_lims_sccm = [0 100];
f.pid_lims = [];
f.flow_width = 1;
f.pid_width = 1;
f.time_to_cut = 0;  % time to cut off beginning of each section
f.dot_size = 60;
f.colors{1} = '#0072BD';
f.colors{2} = '#A2142F';
f.colors{3} = '#D95319';
f.colors{4} = '#7E2F8E';


%% enter data file name

%a_thisfile_name = '2023-10-12_datafile_00'; f.pid_lims = [-.1 3];
%a_thisfile_name = '2023-10-12_datafile_01'; f.pid_lims = [-.1 3];
%a_thisfile_name = '2023-10-12_datafile_02'; f.pid_lims = [-.1 3];
%a_thisfile_name = '2023-10-12_datafile_03'; f.pid_lims = [-.1 3];
%a_thisfile_name = '2023-10-12_datafile_04'; f.pid_lims = [-.1 3];
%a_thisfile_name = '2023-10-12_datafile_05'; f.pid_lims = [-.1 3];
%a_thisfile_name = '2023-10-12_datafile_06'; f.pid_lims = [-.1 3];
%a_thisfile_name = '2023-10-12_datafile_07'; f.pid_lims = [-.1 3];
%f.pid_lims = [0 3];
%plot_opts.show_pid_mean = 'no';
%plot_opts.show_flow_mean = 'no';

%a_thisfile_name = '2023-10-17_datafile_00'; f.pid_lims = [0 .15];
%a_thisfile_name = '2023-10-18_datafile_00'; f.pid_lims = [0 .15];   % something weird happened with PID baseline here
%a_thisfile_name = '2023-10-18_datafile_01'; f.pid_lims = [0 .15];
%a_thisfile_name = '2023-10-18_datafile_02'; f.pid_lims = [0 .15];
%a_thisfile_name = '2023-10-19_datafile_00'; f.pid_lims = [0 3];
%a_thisfile_name = '2023-10-19_datafile_01'; f.pid_lims = [0 3];
%a_thisfile_name = '2023-10-19_datafile_02'; f.pid_lims = [0 3];
%a_thisfile_name = '2023-10-19_datafile_03'; f.pid_lims = [0 3];
%a_thisfile_name = '2023-10-19_datafile_04'; f.pid_lims = [0 3];
%a_thisfile_name = '2023-10-19_datafile_05'; f.pid_lims = [0 1.2];
%a_thisfile_name = '2023-10-20_datafile_00'; f.pid_lims = [0 1.2];
%a_thisfile_name = '2023-10-20_datafile_01'; f.pid_lims = [0 1.2];

%a_thisfile_name = '2023-10-27_datafile_01'; f.pid_lims = [0 6];
%a_thisfile_name = '2023-10-27_datafile_02'; f.pid_lims = [0 6];
%a_thisfile_name = '2023-10-27_datafile_03'; f.pid_lims = [0 6];
%a_thisfile_name = '2023-10-30_datafile_00'; f.pid_lims = [0 6];
%a_thisfile_name = '2023-10-30_datafile_01'; f.pid_lims = [0 5.5];
%a_thisfile_name = '2023-10-30_datafile_02'; f.pid_lims = [0 5.5];
%a_thisfile_name = '2023-10-30_datafile_03'; f.pid_lims = [0 5.5];
%a_thisfile_name = '2023-10-30_datafile_04'; f.pid_lims = [0 6];
%a_thisfile_name = '2023-10-30_datafile_05'; f.pid_lims = [0 6]; 
%a_thisfile_name = '2023-10-30_datafile_06';
%a_thisfile_name = '2023-10-30_datafile_08';
%a_thisfile_name = '2023-10-30_datafile_09';
%a_thisfile_name = '2023-10-30_datafile_10';
a_thisfile_name = '2023-10-31_datafile_00';
f.olfa_lims_sccm = [0 105];
f.pid_lims= [0 5.5];

plot_opts.plot_all = 'no';

f.time_to_cut = 2;
f.olfa_lims_int = [143 575];
%f.position = [140 200 1355 686];
%f.position = [960 210 780 686];  % not that small
f.position = [260 230 812 709];
%f.position = [166 210 650 600];    % for PowerPoint (1/2 size)

%% load .mat file
dir_this_mat_file = strcat(a_dir_OlfaControlGUI,'\analysis\data (.mat files)\',a_thisfile_name,'.mat');
%dir_this_mat_file = strcat(pwd,'\data (.mat files)\',a_thisfile_name,'.mat');

try
    load(dir_this_mat_file);
    %{
    %% get mean flow/pid for each event section - if they were to be cut shorter
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

    %% cut additional time off (& recalculate stats)
    % for each vial
    for i=1:length(d_olfa_flow)
        % for each OV event
        for e=1:length(d_olfa_flow(i).events.OV_keep)
            % cut down the sections
            this_flow_int_data = d_olfa_flow(i).events.OV_keep(e).data.flow_int;
            this_flow_sccm_data = d_olfa_flow(i).events.OV_keep(e).data.flow_sccm;
            this_pid_data = d_olfa_flow(i).events.OV_keep(e).data.pid;
            start_time = this_flow_int_data(1,1) + f.time_to_cut;
            end_time = this_flow_int_data(end,1);
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

    %% plot the whole thing over time
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
        
        % olfa flow
        for i=1:length(d_olfa_flow)
            % if "plot as sccm" is selected
            if strcmp(plot_opts.plot_flow_as_sccm,'yes')
                % if this vial has a calibration table
                if ~isempty(d_olfa_flow(i).cal_table_name)
                    % plot as sccm
                    if ~isempty(d_olfa_flow(i).flow.flow_sccm)
                        ylabel('Olfa flow (sccm)')
                        p = plot(d_olfa_flow(i).flow.flow_sccm(:,1),d_olfa_flow(i).flow.flow_sccm(:,2));
                        if ~isempty(f.olfa_lims_sccm); ylim(f.olfa_lims_sccm)
                        else; ylim([-5 150]); end
                    end
                else
                    % plot as integer
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
                % plot as integer
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
        
        % pid
        if ~isempty(data_pid)
            yyaxis right;
            colororder('#77AC30');  f1_ax.YColor = '#77AC30';
            if ~isempty(f.pid_lims)
                f1_ax.YLim = f.pid_lims;
            end
            ylabel('PID output (V)');
            p2 = plot(data_pid(:,1),data_pid(:,2),'DisplayName','PID');
            p2.LineWidth = f.pid_width;
        end
    end
    
    
    %% plot each section
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
                
                % plot olfa
                if strcmp(plot_opts.plot_flow_as_sccm,'yes')
                    if ~isempty(d_olfa_flow(i).cal_table_name)
                        % plot as sccm
                        if ~isempty(d_olfa_flow(i).flow.flow_sccm)
                            ylabel('Olfa flow (sccm)')
    
                            % get data for this section
                            this_flow_data_shifted = [];
                            this_flow_data = d_olfa_flow(i).flow.flow_sccm;
                            this_flow_data = get_section_data(this_flow_data,t_beg_plot,t_end_plot);
                            
                            % shift x-axis so OV happens at t=0
                            this_flow_data_shifted(:,1) = this_flow_data(:,1) - t_beg_event;
                            this_flow_data_shifted(:,2) = this_flow_data(:,2);
                            
                            p = plot(this_flow_data_shifted(:,1),this_flow_data_shifted(:,2));
                            p.DisplayName = [d_olfa_flow(i).vial_num ' flow'];
                            p.Color = f.colors{i};
                            ylim([f.olfa_lims_sccm]);
                            
                            this_flow_val_sccm = d_olfa_flow(i).sccm_means(e,1);
                            if strcmp(plot_opts.show_flow_mean,'yes')
                                % plot line at the mean
                                this_x_coord = [f.time_to_cut;d_olfa_flow(i).events.OV_keep(e).t_duration];
                                this_y_coord = [this_flow_val_sccm;this_flow_val_sccm];
                                p_flow_mean = plot(this_x_coord,this_y_coord,'LineWidth',4);
                                p_flow_mean.DisplayName = [d_olfa_flow.vial_num ' mean: ' num2str(round(this_flow_val_sccm,1)) ' sccm'];
                                p_flow_mean.Color = f.colors{i};
                            end
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
                if ~isempty(data_pid)
                    yyaxis right; colororder('#77AC30');  f1_ax.YColor = '#77AC30';
                    ylabel('PID output (V)');
                    if ~isempty(f.pid_lims);  ylim([f.pid_lims]); end
                    this_pid_data = get_section_data(data_pid,t_beg_plot,t_end_plot);
                    this_pid_data_shifted = [];
                    this_pid_data_shifted(:,1) = this_pid_data(:,1) - t_beg_event;
                    this_pid_data_shifted(:,2) = this_pid_data(:,2);
                    p2 = plot(this_pid_data_shifted(:,1),this_pid_data_shifted(:,2),'DisplayName','PID');
                    p2.LineWidth = f.pid_width;
                    
                    this_pid_val = d_olfa_flow(i).sccm_means(e,2);
                    % plot line at the mean
                    if strcmp(plot_opts.show_pid_mean,'yes')
                        p_pid_mean = plot(this_x_coord,[this_pid_val;this_pid_val],'LineWidth',4);
                        p_pid_mean.LineStyle = '-';
                        p_pid_mean.DisplayName = ['PID mean: ' num2str(round(this_pid_val,2)) ' V'];
                        p_pid_mean.Color = f1_ax.YColor;
                    end
                end
                
                % set x lims
                xlim([-time_around_event this_flow_data_shifted(end,1)])
    
                % mark where we calculated the mean from
                if strcmp(plot_opts.plot_x_lines,'yes')
                    p_start_time = f.time_to_cut;
                    p_end_time = d_olfa_flow(i).events.OV_keep(e).t_duration;
                    p_t_start = xline(p_start_time,'HandleVisibility','off');
                    p_t_end = xline(p_end_time,'HandleVisibility','off');
                end
                
                figTitle = [num2str(round(this_flow_val_sccm,1)) ' sccm (calculated mean from ' num2str(f.time_to_cut) 's into event)'];
                title(a_thisfile_name); subtitle(figTitle);
                
                %a = [num2str(round(this_flow_val_sccm,1)) ' sccm ' a_thisfile_name '.png'];
                %saveas(f1,a);
            end
        end
        
    end
    
    %% plot: flow v. pid
    f1 = figure; f1.NumberTitle = 'off'; f1.Position = f.position; hold on;
    f1.Name = ['FLOW v. PID: ',a_thisfile_name];
    title(['FLOW v. PID:     ', a_thisfile_name]);
    subtitle(a_this_note);
    legend('Location','northwest');
    f1_ax = gca;
    ylabel('PID (V)')
    if ~isempty(f.pid_lims); ylim(f.pid_lims); end
    
    for i=1:length(d_olfa_flow)
        if ~isempty(d_olfa_flow(i).int_means)
            % plot the values for this vial
            if strcmp(plot_opts.plot_flow_as_sccm,'no')
                p = scatter(d_olfa_flow(i).int_means(:,1),d_olfa_flow(i).int_means(:,2),f.dot_size,'filled');
                xlabel('Olfa flow (int)');
                if ~isempty(f.olfa_lims_int); f1_ax.XLim = f.olfa_lims_int; end
            end
            if strcmp(plot_opts.plot_flow_as_sccm,'yes')
                p = scatter(d_olfa_flow(i).sccm_means(:,1),d_olfa_flow(i).sccm_means(:,2),f.dot_size,'filled');
                xlabel('Olfa flow (sccm)');
                if ~isempty(f.olfa_lims_sccm); f1_ax.XLim = f.olfa_lims_sccm; end
            end
            p.DisplayName = d_olfa_flow(i).vial_num;
            p.MarkerFaceColor = f.colors{i};
        end
    end


%% error catch in case file has not been parsed yet
catch ME
    switch ME.identifier
        case 'MATLAB:load:couldNotReadFile'
            disp(['---> ' a_thisfile_name,' has not been parsed yet: run analysis_get_and_parse_files.m first'])
        otherwise
            rethrow(ME)
    end
end
