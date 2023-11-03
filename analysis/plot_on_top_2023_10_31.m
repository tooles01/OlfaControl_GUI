%% plot each sccm value , overlay all vials


clear variables
set(0,'DefaultTextInterpreter','none')
%% config variables
a_title = '';
a_subtitle = '';

f_position = [166 210 1300 600];    % for PowerPoint
f2_position = [260 230 812 709];
f3_position = [774 224 812 709];

c = struct();
%{
%c.colors{1} = '#A2142F';
%c.colors{2} = '#77AC30';
%c.colors{3} = '#EDB120';
%c.colors{4} = 'm';
%c.colors{1} = [162 20 47];
%c.colors{2} = [119 172 48];
%c.colors{3} = [237 177 32];
%}
c.colors{1} = [.6353 .0784 .1843];
c.colors{4} = [0.4667    0.6745    0.1882];
c.colors{3} = [0.9294    0.6941    0.1255];
c.colors{2} = 'm';
c.flow_color = [0 .447 .741];
c.flow_width = 0.1;
c.pid_width = 2;
c.blue = [0 .447 .741];
c.yellow = [.929 .694 .125];

%% plot options
c.pid_lims = [0 5];

c.flow_lims = [0 105];
c.time_to_cut = 6;
c.plot_by_flow = 'yes';     % plot each flow rate individually
c.plot_error_bars = 'yes';
c.plot_by_vial = 'yes';      % colors based on vial #
c.plot_ctrl = 'no';

%% datafile names
%% 10-30-2023 2-Heptanone
% did not pressurize anything
%c.pid_lims = [0 6];
%{
c.time_to_cut = 9;
file_names = {'2023-10-30_datafile_01.mat'
    '2023-10-30_datafile_02.mat'
    '2023-10-30_datafile_03.mat'
    '2023-10-30_datafile_04.mat'
    '2023-10-30_datafile_05.mat'};
file_names = {'2023-10-30_datafile_02.mat'
    '2023-10-30_datafile_03.mat'
    '2023-10-30_datafile_04.mat'
    '2023-10-30_datafile_05.mat'};
% pressurized each time
file_names = {'2023-10-30_datafile_06.mat'
    '2023-10-30_datafile_08.mat'
    '2023-10-30_datafile_09.mat'
    '2023-10-30_datafile_10.mat'};
% all files
file_names = {'2023-10-30_datafile_01.mat'
    '2023-10-30_datafile_02.mat'
    '2023-10-30_datafile_03.mat'
    '2023-10-30_datafile_04.mat'
    '2023-10-30_datafile_05.mat'
    '2023-10-30_datafile_06.mat'
    '2023-10-30_datafile_08.mat'
    '2023-10-30_datafile_09.mat'
    '2023-10-30_datafile_10.mat'};

%}

%% 10-31-2023 2-Heptanone
%c.time_to_cut = 9;
%{
% before I added odor to the vial
file_names = {'2023-10-31_datafile_00.mat'
    '2023-10-31_datafile_01.mat'
    '2023-10-31_datafile_02.mat'};
% after I added odor to the vial
file_names = {'2023-10-31_datafile_03.mat'
    '2023-10-31_datafile_04.mat'
    '2023-10-31_datafile_05.mat'
    '2023-10-31_datafile_06.mat'};
% all trials
file_names = {'2023-10-31_datafile_00.mat'
    '2023-10-31_datafile_01.mat'
    '2023-10-31_datafile_02.mat'
    '2023-10-31_datafile_03.mat'
    '2023-10-31_datafile_04.mat'
    '2023-10-31_datafile_05.mat'
    '2023-10-31_datafile_06.mat'};
%}

%% 10-31-2023 Acetophenone
%{
% E1->E4
file_names = {'2023-10-31_datafile_07.mat'
    '2023-10-31_datafile_08.mat'
    '2023-10-31_datafile_09.mat'
    '2023-10-31_datafile_10.mat'};
c.pid_lims = [0 1];
% now in backwards order
file_names = {'2023-10-31_datafile_11.mat'
    '2023-10-31_datafile_12.mat'
    '2023-10-31_datafile_13.mat'
    '2023-10-31_datafile_14.mat'};
% all together
file_names = {'2023-10-31_datafile_07.mat'
    '2023-10-31_datafile_08.mat'
    '2023-10-31_datafile_09.mat'
    '2023-10-31_datafile_10.mat'
    '2023-10-31_datafile_11.mat'
    '2023-10-31_datafile_12.mat'
    '2023-10-31_datafile_13.mat'
    '2023-10-31_datafile_14.mat'};
%}
%% 11-01-2023 Ethyl Tiglate

%{
a_subtitle = 'by mixing chamber position';
c.time_to_cut = 6;
c.pid_lims = [0 3.5];
a_title = 'Ethyl Tiglate';
file_names = {'2023-11-01_datafile_01.mat'
    '2023-11-01_datafile_02.mat'
    '2023-11-01_datafile_03.mat'
    '2023-11-01_datafile_04.mat'};

% all
% E1 MC
file_names = {'2023-11-01_datafile_01.mat'
    '2023-11-01_datafile_02.mat'};
% E2 MC
file_names = {'2023-11-01_datafile_03.mat'
    '2023-11-01_datafile_04.mat'};
% E1 olfa manifold
file_names = {'2023-11-01_datafile_01.mat'
    '2023-11-01_datafile_04.mat'};
% E2 olfa manifold
file_names = {'2023-11-01_datafile_02.mat'
    '2023-11-01_datafile_03.mat'};
%}

%% 11-02-2023 Ethyl Tiglate

%{
a_title = 'Ethyl Tiglate';
a_subtitle = '11-02-2023';
c.time_to_cut = 5;
c.pid_lims = [0 3.5];
file_names = {'2023-11-02_datafile_03.mat'
    '2023-11-02_datafile_04.mat'
    '2023-11-02_datafile_05.mat'
    '2023-11-02_datafile_06.mat'
    '2023-11-02_datafile_07.mat'
    '2023-11-02_datafile_08.mat'
    '2023-11-02_datafile_09.mat'};
%}

%% 11-03-2023 Ethyl Tiglate
a_title = 'Ethyl Tiglate';
a_subtitle = '11-02-2023';
c.time_to_cut = 6;
c.pid_lims = [0 3.5];


% after adding odor
file_names = {'2023-11-03_datafile_06.mat'
    '2023-11-03_datafile_07.mat'};
%{
% before adding odor
file_names = {'2023-11-03_datafile_00.mat'
    '2023-11-03_datafile_01.mat'
    '2023-11-03_datafile_02.mat'
    '2023-11-03_datafile_03.mat'
    '2023-11-03_datafile_04.mat'
    '2023-11-03_datafile_05.mat'
    '2023-11-03_datafile_06.mat'};

% all
file_names = {'2023-11-03_datafile_00.mat'
    '2023-11-03_datafile_01.mat'
    '2023-11-03_datafile_02.mat'
    '2023-11-03_datafile_03.mat'
    '2023-11-03_datafile_04.mat'
    '2023-11-03_datafile_05.mat'
    '2023-11-03_datafile_06.mat'
    '2023-11-03_datafile_07.mat'};
%}

%% preallocate array
d = struct('file_name','', ...
    'd_olfa_data_combined','', ...
    'd_olfa_flow','', ...
    'data_pid','');
data(length(file_names)) = d;

%% load these files into the array
for i=1:length(file_names)
    this_file_name = file_names{i};
    data(i).file_name = this_file_name;
    a = load(this_file_name,'d_olfa_data_combined','d_olfa_flow','data_pid');
    data(i).d_olfa_data_combined = a.d_olfa_data_combined;
    data(i).d_olfa_flow = a.d_olfa_flow;
    data(i).data_pid = a.data_pid;
end

clearvars a d
flow_values = [data(i).d_olfa_data_combined.flow_value];

%% plot each flow value separately
if strcmp(c.plot_by_flow,'yes')
    for i=1:length(flow_values)
        f = figure; hold on; f.Position = f_position; legend('Interpreter','none');
        xlabel('Time (s)');
        yyaxis left; ylabel('Flow (SCCM)')
        ylim([c.flow_lims])
        yyaxis right; ylabel('PID (V)')
        ylim([c.pid_lims]);
        this_flow_value = flow_values(i);
        title([num2str(this_flow_value) ' SCCM'])
        
        %% for each file
        for r=1:length(data)
            this_file_name = data(r).file_name;
            shortened_file_name = extractAfter(this_file_name,11);
            shortened_file_name = erase(shortened_file_name,'.mat');

            % for each vial
            for j=1:length(data(r).d_olfa_flow)

                % check if there was a trial at this flow value
                this_file_combined_data = data(r).d_olfa_flow(j).d_olfa_data_combined;
                this_file_flow_values = [data(r).d_olfa_flow(j).d_olfa_data_combined.flow_value];
                %this_file_combined_data = data(r).d_olfa_data_combined;
                %this_file_flow_values = [data(r).d_olfa_data_combined.flow_value];
                [lia, locb] = ismember(this_flow_value,this_file_flow_values);  % get index of where ismember
                
                %% if there was a trial at this flow value
                if lia == 1
                    % and shit didn't hit the fan
                    if ~isempty(data(r).d_olfa_flow(j).d_olfa_data_combined(locb).pid_mean1)
                    %if ~isempty(data(r).d_olfa_data_combined(locb).pid_mean1)
                        %% plot the first trial
                        % find the t_event that's closest to the first flow time
                        t_event_values = [data(r).d_olfa_flow(j).events.OV_keep.t_event];
                        %t_flow_start = data(r).d_olfa_data_combined(locb).data1.flow_sccm(1,1);
                        t_flow_start = data(r).d_olfa_flow(j).d_olfa_data_combined(locb).data1.flow_sccm(1,1);
                        [val,idx]=min(abs(t_event_values-t_flow_start));
                        this_t_event = data(r).d_olfa_flow(j).events.OV_keep(idx).t_event;
            
                        this_vial_num = data(r).d_olfa_flow(j).vial_num;
                        this_flow_data = data(r).d_olfa_flow(j).flow.flow_sccm;
                        this_pid_data = data(r).data_pid;
                        
                        %% shift all of this data to zero
                        this_flow_data(:,1) = this_flow_data(:,1) - this_t_event;
                        this_pid_data(:,1) = this_pid_data(:,1) - this_t_event;
            
                        %% plot flow
                        yyaxis left;
                        p_flow = plot(this_flow_data(:,1),this_flow_data(:,2));
                        p_flow.HandleVisibility = 'off';
                        p_flow.Color = c.flow_color;
                        p_flow.LineWidth = c.flow_width;
                        p_flow.LineStyle = '-';
                        p_flow.Marker = 'none';
            
                        %% plot PID
                        yyaxis right;
                        r_ax = gca; r_ax.YColor = 'k';
                        p_pid = plot(this_pid_data(:,1),this_pid_data(:,2));
                        p_pid.DisplayName = this_vial_num + " " + shortened_file_name;
                        if strcmp(c.plot_by_vial,'yes')
                            vial_num = str2double(this_vial_num(2));    % figure out which color
                            p_pid.Color = c.colors{vial_num};
                        else
                            p_pid.Color = c.colors{r};
                        end
                        p_pid.LineWidth = c.pid_width;
                        p_pid.LineStyle = '-';
                        p_pid.Marker = 'none';
                        
                        xlim([-2 30]);
            
                        %% if there was a second trial at this flow value
                        if ~isempty(data(r).d_olfa_data_combined(locb).data2)        
                            
                            % find the t_event that's closest to the first flow time
                            t_flow_start2 = data(r).d_olfa_data_combined(locb).data2.flow_sccm(1,1);
                            [val2,idx2]=min(abs(t_event_values-t_flow_start2));
                            this_t_event2 = data(r).d_olfa_flow.events.OV_keep(idx2).t_event;
            
                            this_flow_data2 = data(r).d_olfa_flow.flow.flow_sccm;
                            this_pid_data2 = data(r).data_pid;
            
                            % shift all of this data to zero
                            this_flow_data2(:,1) = this_flow_data2(:,1) - this_t_event2;
                            this_pid_data2(:,1) = this_pid_data2(:,1) - this_t_event2;
            
                            % plot flow
                            yyaxis left;
                            p_flow2 = plot(this_flow_data2(:,1),this_flow_data2(:,2));
                            p_flow2.HandleVisibility = 'off';
                            p_flow2.Color = c.flow_color;
                            p_flow2.LineWidth = c.flow_width;
                            p_flow2.LineStyle = '-';
                            p_flow2.Marker = 'none';
                            
                            % plot PID
                            yyaxis right;
                            p_pid2 = plot(this_pid_data2(:,1),this_pid_data2(:,2));
                            p_pid2.HandleVisibility = 'off';
                            if strcmp(c.plot_by_vial,'yes');  p_pid2.Color = c.colors{vial_num}; end
                            p_pid2.LineWidth = c.pid_width;
                            p_pid2.LineStyle = '-';
                            p_pid2.Marker = 'none';
                        end
    
                    end
                end
            end
        
        end
    end
end

%% set up spt char plot
f2 = figure; hold on;
f2.Name = ['FLOW v. PID: ', a_title];
f2.Position = f2_position;
ax2 = gca;
legend('Location','northwest','Interpreter','none');
xlabel('Flow (SCCM)')
xlim(c.flow_lims)
ylabel('PID (V)')
ylim(c.pid_lims)
title(a_title);
if ~isempty(a_subtitle); subtitle(a_subtitle); end
%xlim([37 83]); ylim([1 3]);

%% set up ctrl plot
if strcmp(c.plot_ctrl,'yes')
    f3 = figure; hold on;
    f3.Position = f3_position;
    f3.Name = ['FLOW v. CTRL: ', a_title];
    ax3 = gca;
    legend('Location','northwest','Interpreter','none');
    xlabel('Flow (SCCM)')
    xlim(c.flow_lims)
    ylabel('Ctrl (int)')
    %ylim(c.pid_lims)
    title(a_title);
    if ~isempty(a_subtitle); subtitle(a_subtitle); end
end

%% plot flow v. PID for each file
for r=1:length(data)
    this_file_name = data(r).file_name;
    shortened_file_name = extractAfter(this_file_name,11);
    shortened_file_name = erase(shortened_file_name,'.mat');

    % for each vial
    for i=1:length(data(r).d_olfa_flow)

        this_vial_num = data(r).d_olfa_flow(i).vial_num;
    
        % get the mean flow & PID, after cutting c.time_to_cut
        this_file_events = data(r).d_olfa_flow(i).events.OV_keep;
        this_file_new_means = [];
        this_file_new_stds = [];
        this_file_ctrl_means = [];
        this_file_ctrl_stds = [];
        %% for each trial
        for e=1:length(this_file_events)
            this_event_start_time = this_file_events(e).t_event;
            this_event_end_time = this_file_events(e).t_end;
            this_event_cut_t_start = this_event_start_time + c.time_to_cut;
            this_event_cut_t_end = this_event_end_time;
            
            %% cut data
            this_event_flow_data = this_file_events(e).data.flow_sccm;
            this_event_cut_flow_data = get_section_data(this_event_flow_data,this_event_cut_t_start,this_event_cut_t_end);
            this_event_pid_data = this_file_events(e).data.pid;
            this_event_cut_pid_data = get_section_data(this_event_pid_data,this_event_cut_t_start,this_event_cut_t_end);
            this_event_ctrl_data = data(r).d_olfa_flow(i).ctrl.ctrl_int;
            this_event_cut_ctrl_data = get_section_data(this_event_ctrl_data,this_event_cut_t_start,this_event_cut_t_end);
    
            %% calculate means
            this_event_flow_mean = mean(this_event_cut_flow_data(:,2));
            this_event_pid_mean = mean(this_event_cut_pid_data(:,2));
            this_event_ctrl_mean = mean(this_event_cut_ctrl_data(:,2));
    
            %% calculate standard deviations
            this_event_flow_std = std(this_event_cut_flow_data(:,2));
            this_event_pid_std = std(this_event_cut_pid_data(:,2));
            this_event_ctrl_std = std(this_event_cut_ctrl_data(:,2));
    
            %% add to new structure
            if this_event_flow_mean ~= 0    % JUST FOR THIS ONE TIME 11/1/2023 SINCE GUI BEING DUMB % IF YOU'RE DOING ZERO FLOW TRIALS THEN GET RID OF THIS
                this_event_mean_pair = [this_event_flow_mean this_event_pid_mean];
                this_event_std_pair = [this_event_flow_std this_event_pid_std];
                this_file_new_means = [this_file_new_means;this_event_mean_pair];
                this_file_new_stds = [this_file_new_stds;this_event_std_pair];
                this_file_ctrl_means = [this_file_ctrl_means;this_event_ctrl_mean];
                this_file_ctrl_stds = [this_file_ctrl_stds;this_event_ctrl_std];
            end
        end
        clearvars this_event*
        %% add means to the big data struct
        data(r).new_means = this_file_new_means;
    
        %% add this to the plot
        x_flow = [];
        if ~isempty(this_file_new_means)
            x_flow = this_file_new_means(:,1);
            y_pid = this_file_new_means(:,2);
            %s = scatter(x_flow,y_pid,'filled');
            s = scatter(ax2,x_flow,y_pid,'filled');
            s.DisplayName = this_vial_num + " " + shortened_file_name;
            if strcmp(c.plot_by_vial,'yes')
                vial_num = str2double(this_vial_num(2));    % figure out which color
                s.MarkerFaceColor = c.colors{vial_num};
            end
        end
    
        %% add ctrl to the ctrl plot
        if ~isempty(this_file_ctrl_means)
            if strcmp(c.plot_ctrl,'yes')
                y_ctrl = this_file_ctrl_means;
                s2 = scatter(ax3,x_flow,y_ctrl,'filled');
                s2.DisplayName = this_vial_num + " " + shortened_file_name;
                if strcmp(c.plot_by_vial,'yes')
                    vial_num = str2double(this_vial_num(2));    % figure out which color
                    s2.MarkerFaceColor = c.colors{vial_num};
                end
            end
        end
        
        %% plot error bars
        if ~isempty(x_flow)
            if strcmp(c.plot_error_bars,'yes')
                xneg = [];
                xpos = [];
                yneg = [];
                ypos = [];
                yneg_ctrl = [];
                ypos_ctrl = [];
                % for each event
                for e=1:length(this_file_new_stds)
                    % xneg and xpos will be 1/2 the std dev at each point
                    flow_std = this_file_new_stds(e,1);
                    pid_std = this_file_new_stds(e,2);
                    ctrl_std = this_file_ctrl_stds(e);
                    xneg(e,1) = flow_std/2;
                    xpos(e,1) = flow_std/2;
                    yneg(e,1) = pid_std/2;
                    ypos(e,1) = pid_std/2;
                    yneg_ctrl(e,1) = ctrl_std/2;
                    ypos_ctrl(e,1) = ctrl_std/2;
                end
                e = errorbar(ax2,x_flow,y_pid,yneg,ypos,xneg,xpos,'o');
                e.HandleVisibility = 'off';
                try e.Color = s.MarkerFaceColor;
                catch ME; e.Color = s.CData; end
                
                if strcmp(c.plot_ctrl,'yes')
                    e_ctrl = errorbar(ax3,x_flow,y_ctrl,yneg_ctrl,ypos_ctrl,xneg,xpos,'o');
                    e_ctrl.HandleVisibility = 'off';
                    try e_ctrl.Color = s2.MarkerFaceColor;
                    catch ME; e_ctrl.Color = s2.CData; end
                end
            end
        end    
    end
end

%% plot flow v. ctrl for each file
%for r=1:length(data)


