%% plot standard and 8-line on top of each other

clear variables



%% display variables
f = struct();
f.pid_ylims = [0 3];
f.x_lims = [];
f.plot_all = 'yes';

f.position = [260 230 812 709];
f2_position = [987 230 812 709];


%% enter data file names

%a_8line_file_name = '2023-10-20_datafile_00';
%a_standard_file_name = '2023-10-20_datafile00_acetophenone';

%a_8line_file_name = '2023-10-20_datafile_01';
%a_standard_file_name = '2023-10-20_datafile01_acetophenone';

%f.pid_ylims = [0 1.2];

%a_8line_file_name = '2023-11-06_datafile_03';   % E1
%a_8line_file_name = '2023-11-06_datafile_04';   % E3
%a_8line_file_name = '2023-11-06_datafile_05';   % E4
%a_standard_file_name = '2023-11-06_datafile_00_ethyltiglate';
%a_standard_file_name = '2023-11-06_datafile_02_ethyltiglate';

a_8line_file_name = '2023-11-07_datafile_05';   % E2
a_standard_file_name = '2023-11-07_datafile_00_ethyltiglate_B';

f.pid_ylims = [0 3.5];
f.x_lims = [-.5 15];

%% enter directory for this computer
%a_dir_OlfaEngDropbox = 'C:\Users\Admin\Dropbox (NYU Langone Health)\OlfactometerEngineeringGroup (2)';
a_dir_OlfaEngDropbox = 'C:\Users\SB13FLLT004\Dropbox (NYU Langone Health)\OlfactometerEngineeringGroup (2)';
a_dir_OlfaControlGUI = strcat(a_dir_OlfaEngDropbox,'\Control\a_software\OlfaControl_GUI');

addpath(genpath(a_dir_OlfaControlGUI)); % make sure datafiles are on matlab path


%% load .mat files
dir_8line_mat_file = strcat(a_dir_OlfaControlGUI,'\analysis\data (.mat files)\',a_8line_file_name,'.mat');
dir_standard_mat_file = strcat(a_dir_OlfaControlGUI,'\analysis\data (.mat files)\',a_standard_file_name,'.mat');
d_8line_all = load(dir_8line_mat_file,'d_olfa_flow','data_pid');
d_standard_all = load(dir_standard_mat_file,'d_olfa_data_combined','d_olfa_data_sorted');

clearvars dir*

d_standard = d_standard_all.d_olfa_data_combined;


%% plot PID at each flow value separately
if strcmp(f.plot_all,'yes')
    % for each flow value
    for i=1:length(d_8line_all.d_olfa_flow.d_olfa_data_combined)
        % make a plot
        f1 = figure; hold on; f1.Position = f.position;
        legend;
        xlabel('Time (s)')
        ylabel('PID (V)')
        if ~isempty(f.pid_ylims); ylim(f.pid_ylims); end
        if ~isempty(f.x_lims); xlim(f.x_lims);end
        this_flow_value = d_standard(i).flow_value;
        title([num2str(this_flow_value) ' sccm']);
    
        % 8-line:
        %% if there was a trial at this flow value
        this_file_flow_values = [d_8line_all.d_olfa_flow.d_olfa_data_combined.flow_value];
        [lia, locb] = ismember(this_flow_value,this_file_flow_values);  % get index of where ismember
        if lia == 1
            % and shit didn't hit the fan
            if ~isempty(d_8line_all.d_olfa_flow.d_olfa_data_combined(locb).pid_mean1)
                %% plot the first trial
                % find the t_event that's closest to the first flow time
                t_event_values = [d_8line_all.d_olfa_flow.events.OV_keep.t_event];
                t_flow_start= d_8line_all.d_olfa_flow.d_olfa_data_combined(locb).data1.flow_sccm(1,1);
                [val,idx] = min(abs(t_event_values-t_flow_start));
                this_t_event = d_8line_all.d_olfa_flow.events.OV_keep(idx).t_event;
                this_pid_data = d_8line_all.data_pid;
    
                %% shift all of this data to zero
                this_pid_data(:,1) = this_pid_data(:,1) - this_t_event;
    
                %% plot PID
                p_pid = plot(this_pid_data(:,1),this_pid_data(:,2));
                p_pid.DisplayName = '8-line olfa';
                p_pid.Color = 'red';
    
                %% if there was a second trial at this flow value
                if ~isempty(d_8line_all.d_olfa_flow.d_olfa_data_combined(locb).data2)    
                    
                    % find the t_event that's closest to the first flow time
                    %t_flow_start2 = d_8line_all.d_olfa_data_combined(locb).data2.flow_sccm(1,1);
                    t_flow_start2 = d_8line_all.d_olfa_flow.d_olfa_data_combined(locb).data2.flow_sccm(1,1);
                    [val2,idx2] = min(abs(t_event_values-t_flow_start2));
                    this_t_event2 = d_8line_all.d_olfa_flow.events.OV_keep(idx2).t_event;
                    
                    this_pid_data2 = d_8line_all.data_pid;
                    % shift all of this data to zero
                    this_pid_data2(:,1) = this_pid_data2(:,1) - this_t_event2;
                    
                    %% plot PID
                    p_pid2 = plot(this_pid_data2(:,1),this_pid_data2(:,2));
                    p_pid2.HandleVisibility = 'off';
                    p_pid2.Color = 'red';
                end
            end
        end
        
        % Standard olfa
        this_standard_data1 = d_standard(i).data1;    
        
        p1b = plot(this_standard_data1(:,1),this_standard_data1(:,2),'DisplayName','standard olfa');
        p1b.Color = 'blue';
        
        % if there was a second run
        if ~isempty(d_standard(i).data2)
            this_standard_data2 = d_standard(i).data2;
            p2b = plot(this_standard_data2(:,1),this_standard_data2(:,2),'HandleVisibility','off');
            p2b.Color = 'blue';
        end

    end
end

%% plot spt char
f2 = figure; hold on;

f2.Position = f2_position;
legend;
xlabel('Flow (sccm)')
ylabel('PID (V)')
if ~isempty(f.pid_ylims)
    ylim(f.pid_ylims);
end

xlim([0 100])

d_8line_sccm_means = d_8line_all.d_olfa_flow.sccm_means;
p1a_s = scatter(d_8line_sccm_means(:,1),d_8line_sccm_means(:,2),'filled','DisplayName','8-line olfa');
p1a_s.MarkerFaceColor = 'red';

d_standard_sccm_means = [];
d_standard_sccm_means(:,1) = [d_standard_all.d_olfa_data_sorted.flow_value];
d_standard_sccm_means(:,2) = [d_standard_all.d_olfa_data_sorted.pid_mean];
p2a_s = scatter(d_standard_sccm_means(:,1),d_standard_sccm_means(:,2),'filled','DisplayName','standard olfa');
p2a_s.MarkerFaceColor = 'blue';

