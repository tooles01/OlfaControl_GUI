%% analysis_plot_additive

% plot additive


%%

function analysis_plot_additive(file_names,a_subtitle,plot_opts)

arguments
    file_names  (:,1) cell  % 3 files: 1st and 2nd spt char, additive file
    % TODO: change this to : spt char files [cell], additive file [single file]
    a_subtitle  (1,1) string = ''

    % Axis Limits
    plot_opts.pid_lims          (1,:) double = [0 3]
    plot_opts.flow_lims         (1,:) double = [0 105]
    
    % Data Manipulation
    plot_opts.time_to_cut       (1,:) double = 0

    % Other
    plot_opts.fig_position      (1,:) double = [175 230 812 709]
    plot_opts.show_error_bars   (1,1) string = 'yes'

end

%%
set(0,'DefaultTextInterpreter','none')

%% Display Variables
f.dot_size = 60;
f.PID_color = '#77AC30';

% Vial colors
f.colors{1} = '#0072BD';
f.colors{2} = '#A2142F';
f.colors{3} = '#D95319';
f.colors{4} = '#7E2F8E';

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

%% Load *.mat files

% Get file names
a_thisfile_spt1 = file_names{1};
a_thisfile_spt2 = file_names{2};
a_thisfile_add = file_names{3};

% Full directory for .mat file
dir_mat_file_spt1 = strcat(dir_data_files,a_thisfile_spt1,'.mat');
dir_mat_file_spt2 = strcat(dir_data_files,a_thisfile_spt2,'.mat');
dir_mat_file_add = strcat(dir_data_files,a_thisfile_add,'.mat');

try
    d_spt1 = load(dir_mat_file_spt1);
    d_spt2 = load(dir_mat_file_spt2);
    d_add = load(dir_mat_file_add);

    %% Cut additional time off (& recalculate stats)

    % Setpoint Char #1
    d_olfa_flow_spt1 = d_spt1.d_olfa_flow;

    % For each vial
    for i=1:length(d_olfa_flow_spt1)
        % for each OV event
        for e=1:length(d_olfa_flow_spt1(i).events.OV_keep)
            % cut down the sections
            this_flow_sccm_data = d_olfa_flow_spt1(i).events.OV_keep(e).data.flow_sccm;
            this_pid_data = d_olfa_flow_spt1(i).events.OV_keep(e).data.pid;
            start_time = d_olfa_flow_spt1.events.OV_keep(e).t_event + plot_opts.time_to_cut;
            end_time = this_pid_data(end,1);
            this_flow_sccm_data = get_section_data(this_flow_sccm_data,start_time,end_time);
            this_pid_data = get_section_data(this_pid_data,start_time,end_time);

            % recalculate the mean
            this_flow_sccm_mean = mean(this_flow_sccm_data(:,2));
            this_pid_mean = mean(this_pid_data(:,2));
            this_flow_std = std(this_flow_sccm_data(:,2));
            this_pid_std = std(this_pid_data(:,2));

            % add these means back into the structure
            d_olfa_flow_spt1(i).events.OV_keep(e).flow_mean_sccm = this_flow_sccm_mean;
            d_olfa_flow_spt1(i).events.OV_keep(e).pid_mean = this_pid_mean;
            d_olfa_flow_spt1(i).events.OV_keep(e).flow_std_sccm = this_flow_std;
            d_olfa_flow_spt1(i).events.OV_keep(e).pid_std = this_pid_std;

            % add them to the int/sccm structs
            d_olfa_flow_spt1(i).sccm_means(e,1) = this_flow_sccm_mean;
            d_olfa_flow_spt1(i).sccm_means(e,2) = this_pid_mean;
        end
    end
    clearvars this_*

    % Setpoint Char #2
    d_olfa_flow_spt2 = d_spt2.d_olfa_flow;
    % For each vial
    for i=1:length(d_olfa_flow_spt2)
        % for each OV event
        for e=1:length(d_olfa_flow_spt2(i).events.OV_keep)
            % cut down the sections
            this_flow_sccm_data = d_olfa_flow_spt2(i).events.OV_keep(e).data.flow_sccm;
            this_pid_data = d_olfa_flow_spt2(i).events.OV_keep(e).data.pid;
            start_time = d_olfa_flow_spt2.events.OV_keep(e).t_event + plot_opts.time_to_cut;
            end_time = this_pid_data(end,1);
            this_flow_sccm_data = get_section_data(this_flow_sccm_data,start_time,end_time);
            this_pid_data = get_section_data(this_pid_data,start_time,end_time);

            % recalculate the mean
            this_flow_sccm_mean = mean(this_flow_sccm_data(:,2));
            this_pid_mean = mean(this_pid_data(:,2));
            this_flow_std = std(this_flow_sccm_data(:,2));
            this_pid_std = std(this_pid_data(:,2));

            % add these means back into the structure
            d_olfa_flow_spt2(i).events.OV_keep(e).flow_mean_sccm = this_flow_sccm_mean;
            d_olfa_flow_spt2(i).events.OV_keep(e).pid_mean = this_pid_mean;
            d_olfa_flow_spt2(i).events.OV_keep(e).flow_std_sccm = this_flow_std;
            d_olfa_flow_spt2(i).events.OV_keep(e).pid_std = this_pid_std;

            % add them to the int/sccm structs
            d_olfa_flow_spt2(i).sccm_means(e,1) = this_flow_sccm_mean;
            d_olfa_flow_spt2(i).sccm_means(e,2) = this_pid_mean;
        end
    end
    clearvars this_*

    % Additive
    d_olfa_flow_add = d_add.d_olfa_flow;
    %{
    % for each vial
    for i=1:length(d_olfa_flow_add)
        % for each OV event
        for e=1:length(d_olfa_flow_add(i).events.OV_keep)
            % cut down the sections
            this_flow_sccm_data = d_olfa_flow_add(i).events.OV_keep(e).data.flow_sccm;
            this_pid_data = d_olfa_flow_add(i).events.OV_keep(e).data.pid;
            start_time = d_olfa_flow_add(i).events.OV_keep(e).t_event + plot_opts.time_to_cut;
            end_time = this_pid_data(end,1);
            this_flow_sccm_data = get_section_data(this_flow_sccm_data,start_time,end_time);
            this_pid_data = get_section_data(this_pid_data,start_time,end_time);

            % recalculate the mean
            this_flow_sccm_mean = mean(this_flow_sccm_data(:,2));
            this_pid_mean = mean(this_pid_data(:,2));
            this_flow_std = std(this_flow_sccm_data(:,2));
            this_pid_std = std(this_pid_data(:,2));

            % add these means back into the structure
            d_olfa_flow_add(i).events.OV_keep(e).flow_mean_sccm = this_flow_sccm_mean;
            d_olfa_flow_add(i).events.OV_keep(e).pid_mean = this_pid_mean;
            d_olfa_flow_add(i).events.OV_keep(e).flow_std_sccm = this_flow_std;
            d_olfa_flow_add(i).events.OV_keep(e).pid_std = this_pid_std;

            % add them to the int/sccm structs
            d_olfa_flow_add(i).sccm_means(e,1) = this_flow_sccm_mean;
            d_olfa_flow_add(i).sccm_means(e,2) = this_pid_mean;
        end
    end
    clearvars this_*
    %}


    d_olfa_flow_add(3).vial_num = 'additive';
    d_olfa_flow_add(3).events = [];
    d_olfa_flow_add_spt1_events = d_olfa_flow_add(1).events.OV_keep;
    d_olfa_flow_add_spt2_events = d_olfa_flow_add(2).events.OV_keep;

    % for each event
    for e=1:length(d_olfa_flow_add_spt1_events)
        % get data for each vial
        this_event_total_flow_data = [];
        vial1_data = d_olfa_flow_add_spt1_events(e).data.flow_sccm;
        vial2_data = d_olfa_flow_add_spt2_events(e).data.flow_sccm;
        
        % calculate new start time & cut data
        t_start = d_olfa_flow_add(1).events.OV_keep(e).t_event;
        t_start = t_start + plot_opts.time_to_cut;
        vial1_data_cut = get_section_data(vial1_data,t_start,max(vial1_data(:,1)));
        vial2_data_cut = get_section_data(vial2_data,t_start,max(vial2_data(:,1)));
        
        % if not the same length, cut the last value off of the longer one
        if length(vial1_data_cut) > length(vial2_data_cut)
            new_length = length(vial2_data_cut);
            vial1_data_cut = vial1_data_cut(1:new_length,:);
        end
        if length(vial2_data_cut) > length(vial1_data_cut)
            new_length = length(vial1_data_cut);
            vial2_data_cut = vial2_data_cut(1:new_length,:);
        end
        %num_points = length(vial1_data);
        %{
        if (length(vial2_data) < length(vial1_data))
            vial2_data(length(vial1_data),1) = vial1_data(length(vial1_data),1);
            %vial2_data(length(vial1_data),2) = [];
            vial2_data(length(vial1_data),2) = vial1_data((length(vial2_data)-1),2);
            %num_points = length(vial2_data);
        end
        if (length(vial1_data) < length(vial2_data))
            vial1_data(length(vial2_data),1) = vial2_data(length(vial2_data),1);
            vial1_data(length(vial2_data),2) = vial1_data((length(vial1_data)-1),2);
        end
        %}
        % which vial has the first timestamp
        if vial1_data_cut(1,1) < vial2_data_cut(1,1)
            time_values = vial1_data_cut(:,1);
        else
            time_values = vial2_data_cut(:,1);
        end

        % create matrix with total flow values
        this_event_total_flow_data(:,1) = time_values;
        this_event_total_flow_data(:,2) = vial1_data_cut(:,2) + vial2_data_cut(:,2);

        %{
        this_event_matrix = [];
        for n=1:num_points
            % add the time, vial1 flow, vial2 flow, total flow
            this_event_matrix(n,1) = vial1_data(n,1);
            this_event_matrix(n,2) = vial1_data(n,2);
            this_event_matrix(n,3) = vial2_data(n,2);
            this_event_matrix(n,4) = vial1_data(n,2) + vial2_data(n,2); %#ok<*SAGROW>
        end
        d_olfa_flow_add(3).events.OV_keep(e).this_event_flow_data = this_event_matrix;
        % cut off x seconds from this flow data
        new_start_time = this_event_matrix(1,1) + plot_opts.time_to_cut;
        % find this start time in column 1 of the data
        col1 = this_event_matrix(:,1);
        idx = find(col1 >= new_start_time,1,'first');
        % start the data at this point
        this_event_matrix_cut = this_event_matrix(idx:end,:);
        % calculate the mean total flow and std
        total_flow_values = this_event_matrix_cut(:,4);
        total_flow_mean = mean(total_flow_values);
        total_flow_std = std(total_flow_values);
        %}
        
        % calculate mean and std of total flow value
        total_flow_mean = mean(this_event_total_flow_data(:,2));
        total_flow_std = std(this_event_total_flow_data(:,2));

        % add back into the big structure
        d_olfa_flow_add(3).events.OV_keep(e).vial1_mean = mean(vial1_data_cut(:,2));
        d_olfa_flow_add(3).events.OV_keep(e).vial2_mean = mean(vial2_data_cut(:,2));
        d_olfa_flow_add(3).events.OV_keep(e).vial1_std = std(vial1_data_cut(:,2));
        d_olfa_flow_add(3).events.OV_keep(e).vial2_std = std(vial2_data_cut(:,2));
        d_olfa_flow_add(3).events.OV_keep(e).total_flow_mean = total_flow_mean;
        d_olfa_flow_add(3).events.OV_keep(e).total_flow_std = total_flow_std;

    end


    %% Plot it

    % Create figure
    f1 = figure; f1.NumberTitle = 'off'; f1.Position = plot_opts.fig_position; hold on;
    f1.Name = a_thisfile_add + " - " + a_subtitle;
    %title(['ADDITIVE: ',a_thisfile_add]);  % this blocks the top y-axis
    legend('Location','northwest','Interpreter','none');
    f1_ax1 = gca;
    xlabel('Vial 1 flow (sccm)');
    ylabel('PID (V)')
    ylim(plot_opts.pid_lims);
    xlim(plot_opts.flow_lims);

    %% Plot: spt1
    for i=1:length(d_olfa_flow_spt1)
        if ~isempty(d_olfa_flow_spt1(i).sccm_means)
            %% plot the values for this vial
            spt1_x = d_olfa_flow_spt1(i).sccm_means(:,1);
            spt1_y = d_olfa_flow_spt1(i).sccm_means(:,2);
            p_spt1 = scatter(spt1_x,spt1_y,'filled');
            p_spt1.SizeData = f.dot_size;
            p_spt1.DisplayName = d_olfa_flow_spt1(i).vial_num + ": " + a_thisfile_spt1;
            p_spt1.MarkerFaceColor = f.colors{i};
        
            %% plot the error bars
            if strcmp(plot_opts.show_error_bars,'yes')
                x = d_olfa_flow_spt1(i).sccm_means(:,1);
                y = d_olfa_flow_spt1(i).sccm_means(:,2);
                for e=1:length(d_olfa_flow_spt1(i).sccm_means)
                    flow_std = d_olfa_flow_spt1(i).events.OV_keep(e).flow_std_sccm;
                    pid_std = d_olfa_flow_spt1(i).events.OV_keep(e).pid_std;
                    xneg(e,1) = flow_std/2;
                    xpos(e,1) = flow_std/2;
                    yneg(e,1) = pid_std/2;
                    ypos(e,1) = pid_std/2;
                end
                e_spt1 = errorbar(x,y,yneg,ypos,xneg,xpos,'o');
                e_spt1.HandleVisibility = 'off';
                e_spt1.Color = p_spt1.MarkerFaceColor;
            end
        end
    end

    %% Plot: spt2
    for i=1:length(d_olfa_flow_spt2)
        if ~isempty(d_olfa_flow_spt2(i).sccm_means)
            %% plot the values for this vial
            spt2_x = d_olfa_flow_spt2(i).sccm_means(:,1);
            spt2_y = d_olfa_flow_spt2(i).sccm_means(:,2);
            spt2_x_reversed = 100-spt2_x;
            p_spt2 = scatter(spt2_x_reversed,spt2_y,'filled');
            p_spt2.SizeData = f.dot_size;
            p_spt2.DisplayName = d_olfa_flow_spt2(i).vial_num + ": " + a_thisfile_spt2;
            p_spt2.MarkerFaceColor = f.colors{i+1};
        
            %% plot the error bars
            if strcmp(plot_opts.show_error_bars,'yes')
                x = d_olfa_flow_spt2(i).sccm_means(:,1);
                x_reversed = 100-x;
                y = d_olfa_flow_spt2(i).sccm_means(:,2);
                for e=1:length(d_olfa_flow_spt2(i).sccm_means)
                    flow_std = d_olfa_flow_spt2(i).events.OV_keep(e).flow_std_sccm;
                    pid_std = d_olfa_flow_spt2(i).events.OV_keep(e).pid_std;
                    xneg(e,1) = flow_std/2;
                    xpos(e,1) = flow_std/2;
                    yneg(e,1) = pid_std/2;
                    ypos(e,1) = pid_std/2;
                end
                e_spt2 = errorbar(x_reversed,y,yneg,ypos,xneg,xpos,'o');
                e_spt2.HandleVisibility = 'off';
                e_spt2.Color = p_spt2.MarkerFaceColor;
            end
        end
    end

    %% Plot: additive
    d_additive_flow_means = [];

    % for each vial in the additive trial, add mean flow to d_additive_flow_means
    for i=1:length(d_olfa_flow_add)
        % as long as something didn't go disastrously wrong
        if ~isempty(d_olfa_flow_add(i).sccm_means)
            d_additive_flow_means = [d_additive_flow_means d_olfa_flow_add(i).sccm_means(:,1)]; %#ok<*AGROW>
        end
    end
    % then get the PID (it'll be identical for each vial, so you can just grab the first one)
    d_additive_pid = d_olfa_flow_add(1).sccm_means(:,2);

    % plot flow v. PID (using vial1 flow values)
    p_add_x = d_additive_flow_means(:,1);
    p_add_y = d_additive_pid;

    p_add = scatter(p_add_x,p_add_y,'filled');  % vial 1 flow, PID
    p_add.SizeData = f.dot_size;
    p_add.DisplayName = 'Additive: ' + " " + a_thisfile_add;
    p_add.MarkerFaceColor = f.PID_color;

    %% plot the additive error bars TODO
    if strcmp(plot_opts.show_error_bars,'yes')
        x = p_add_x;
        y = p_add_y;
        %vial_1_events = d_olfa_flow_add(1).
        %for e=1:length()
    end

    %% Create fake second x axis for top
    f1_ax2 = axes(f1);
    f1_ax2.Color = 'none';
    f1_ax2.XAxisLocation = 'top';
    ylim([f1_ax1.YLim])     % match y limits
    xlim([f1_ax1.XLim])     % match x limits
    set(f1_ax2, 'XDir', 'reverse');
    xlabel('Vial 2 flow (sccm)')

    %title(['ADDITIVE: ',a_thisfile_add]);

    % focus on first axis (so you can click stuff)
    %axes(f1_ax1);

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
