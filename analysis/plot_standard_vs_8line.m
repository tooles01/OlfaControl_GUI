%% plot standard and 8-line on top of each other

clear variables



%% display variables
f = struct();
f.pid_ylims = [0 3];
f.x_lims = [];
f.position = [260 230 812 709];


%% enter data file names

%a_8line_file_name = '2023-10-20_datafile_00';
%a_standard_file_name = '2023-10-20_datafile00_acetophenone';

%a_8line_file_name = '2023-10-20_datafile_01';
%a_standard_file_name = '2023-10-20_datafile01_acetophenone';

f.pid_ylims = [0 1.2];
f.x_lims = [-.5 15];

a_8line_file_name = '2023-11-06_datafile_03';
%a_8line_file_name = '2023-11-06_datafile_04';
%a_8line_file_name = '2023-11-06_datafile_05';
%a_standard_file_name = '2023-11-06_datafile_00_ethyltiglate';
a_standard_file_name = '2023-11-06_datafile_02_ethyltiglate';

f.pid_ylims = [0 3.5];

%% enter directory for this computer
%a_dir_OlfaEngDropbox = 'C:\Users\Admin\Dropbox (NYU Langone Health)\OlfactometerEngineeringGroup (2)';
a_dir_OlfaEngDropbox = 'C:\Users\SB13FLLT004\Dropbox (NYU Langone Health)\OlfactometerEngineeringGroup (2)';
a_dir_OlfaControlGUI = strcat(a_dir_OlfaEngDropbox,'\Control\a_software\OlfaControl_GUI');

addpath(genpath(a_dir_OlfaControlGUI)); % make sure datafiles are on matlab path


%% load .mat files
dir_8line_mat_file = strcat(a_dir_OlfaControlGUI,'\analysis\data (.mat files)\',a_8line_file_name,'.mat');
dir_standard_mat_file = strcat(a_dir_OlfaControlGUI,'\analysis\data (.mat files)\',a_standard_file_name,'.mat');
%d_olfa21_v10_all = load(dir_this_mat_file);
d_8line_all = load(dir_8line_mat_file);
d_standard_all = load(dir_standard_mat_file);

clearvars dir*

d_8line = d_8line_all.d_olfa_data_combined;
d_standard = d_standard_all.d_olfa_data_combined;


%% plot PID at each flow value separately
for i=1:length(d_8line)
    % make a plot
    f1 = figure; hold on; f1.Position = f.position;
    legend;
    xlabel('Time (s)')
    ylabel('PID (V)')
    if ~isempty(f.pid_ylims); ylim(f.pid_ylims); end
    if ~isempty(f.x_lims); xlim(f.x_lims);end
    this_flow_value = d_standard(i).flow_value;
    title([num2str(this_flow_value) ' sccm']);
    
    % get 8line data
    this_8line_data1 = d_8line(i).data1.pid;
    
    % adjust time to zero
    this_8line_data1(:,1) = this_8line_data1(:,1) - this_8line_data1(1,1);
    
    
    % get standard olfa data
    this_standard_data1 = d_standard(i).data1;
    
    % plot them?
    p1a = plot(this_8line_data1(:,1),this_8line_data1(:,2),'DisplayName','8-line olfa');
    p1a.Color = 'red';

    % if there was a second run
    if ~isempty(d_8line(i).data2)
        this_8line_data2 = d_8line(i).data2.pid;
        this_8line_data2(:,1) = this_8line_data2(:,1) - this_8line_data2(1,1);
        p2a = plot(this_8line_data2(:,1),this_8line_data2(:,2),'HandleVisibility','off');
        p2a.Color = 'red';
    end
    
    p1b = plot(this_standard_data1(:,1),this_standard_data1(:,2),'DisplayName','standard olfa');
    p1b.Color = 'blue';
    
    % if there was a second run
    if ~isempty(d_standard(i).data2)
        this_standard_data2 = d_standard(i).data2;
        p2b = plot(this_standard_data2(:,1),this_standard_data2(:,2),'HandleVisibility','off');
        p2b.Color = 'blue';
    end

end

%% plot spt char
figure; hold on;

f1.Position = f.position;
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
%p1a = scatter(d_8line)

