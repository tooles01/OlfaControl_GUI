%% plot eachsccm value , overlay all vials


%% before you do this, run analysis_spt_char on each file you want to load here
% then save like:
% save('2023-10-30_datafile06_E1.mat','d_olfa_flow','data_pid');

clear variables
%% datafile names
E1_all = load('2023-10-30_datafile_06_E1.mat');
E2_all = load('2023-10-30_datafile_08_E2.mat');
E3_all = load('2023-10-30_datafile_09_E3.mat');
E4_all = load('2023-10-30_datafile_10_E4.mat');

%{
E1_all = load('2023-10-30_datafile04_E1.mat');
E2_all = load('2023-10-30_datafile03_E2.mat');
E3_all = load('2023-10-30_datafile02_E3.mat');
E4_all = load('2023-10-30_datafile05_E4.mat');
%}

%% load data
E1_flow = E1_all.d_olfa_flow;
E2_flow = E2_all.d_olfa_flow;
E3_flow = E3_all.d_olfa_flow;
E4_flow = E4_all.d_olfa_flow;

E1_pid = E1_all.data_pid;
E2_pid = E2_all.data_pid;
E3_pid = E3_all.data_pid;
E4_pid = E4_all.data_pid;

E1_flow_data = E1_flow.flow.flow_sccm;
E2_flow_data = E2_flow.flow.flow_sccm;
E3_flow_data = E3_flow.flow.flow_sccm;
E4_flow_data = E4_flow.flow.flow_sccm;

c = struct();
c.E1_color = '#A2142F';
c.E2_color = '#77AC30';
c.E3_color = '#EDB120';
c.E4_color = 'm';
c.flow_color = [0 .447 .741];
c.flow_width = 0.1;
c.pid_width = 2;
%% plot each flow value
for i=1:2:length(E1_flow.events.OV_keep)
%for i=1:2:length(E1_all.d_olfa_data_combined)
%for i=1:length(E1_flow.events.OV_keep)
%for i=1:5
    this_flow_value = round(E1_flow.events.OV_keep(i).flow_mean_sccm);
    f = figure; hold on;
    f.Position = [166 210 1300 600];    % for PowerPoint
    legend;
    xlabel('Time (s)')
    title(this_flow_value)

    t_start = E1_flow.events.OV_keep(i).t_event;
    t_end = E1_flow.events.OV_keep(i).t_end;
    
    %% plot flow
    yyaxis left; ylabel('Flow (SCCM)')
    ylim([0 100]);
    % first trial: shift flow data to zero
    E1_flow_shifted1(:,1) = E1_flow_data(:,1) - E1_flow.events.OV_keep(i).t_event;
    E1_flow_shifted1(:,2) = E1_flow_data(:,2);
    E2_flow_shifted1(:,1) = E2_flow_data(:,1) - E2_flow.events.OV_keep(i).t_event;
    E2_flow_shifted1(:,2) = E2_flow_data(:,2);
    E3_flow_shifted1(:,1) = E3_flow_data(:,1) - E3_flow.events.OV_keep(i).t_event;
    E3_flow_shifted1(:,2) = E3_flow_data(:,2);
    E4_flow_shifted1(:,1) = E4_flow_data(:,1) - E4_flow.events.OV_keep(i).t_event;
    E4_flow_shifted1(:,2) = E4_flow_data(:,2);
    pf1 = plot(E1_flow_shifted1(:,1),E1_flow_shifted1(:,2),'DisplayName','E1 flow');
    pf2 = plot(E2_flow_shifted1(:,1),E2_flow_shifted1(:,2),'DisplayName','E2 flow');
    pf3 = plot(E3_flow_shifted1(:,1),E3_flow_shifted1(:,2),'DisplayName','E3 flow');
    pf4 = plot(E4_flow_shifted1(:,1),E4_flow_shifted1(:,2),'DisplayName','E4 flow');
    %pf4 = plot(E4_flow_data(:,1),E4_flow_data(:,2),'DisplayName','E4 flow');
    xlim([0 20]);

    % assuming the trials were run in sequential order
    % second trial: shift flow data so that OV happens at 0
    E1_flow_shifted2(:,1) = E1_flow_data(:,1) - E1_flow.events.OV_keep(i+1).t_event;
    E1_flow_shifted2(:,2) = E1_flow_data(:,2);
    E2_flow_shifted2(:,1) = E2_flow_data(:,1) - E2_flow.events.OV_keep(i+1).t_event;
    E2_flow_shifted2(:,2) = E2_flow_data(:,2);
    E3_flow_shifted2(:,1) = E3_flow_data(:,1) - E3_flow.events.OV_keep(i+1).t_event;
    E3_flow_shifted2(:,2) = E3_flow_data(:,2);
    E4_flow_shifted2(:,1) = E4_flow_data(:,1) - E4_flow.events.OV_keep(i+1).t_event;
    E4_flow_shifted2(:,2) = E4_flow_data(:,2);
    % plot it
    %pf1_2 = plot(E1_flow_shifted2(:,1),E1_flow_shifted2(:,2));
    %pf2_2 = plot(E2_flow_shifted2(:,1),E2_flow_shifted2(:,2));
    %pf3_2 = plot(E3_flow_shifted2(:,1),E3_flow_shifted2(:,2));
    %pf4_2 = plot(E4_flow_shifted2(:,1),E4_flow_shifted2(:,2));

    %% plot stuff
    pf1.HandleVisibility = 'off';
    pf2.HandleVisibility = 'off';
    pf3.HandleVisibility = 'off';
    pf4.HandleVisibility = 'off';
    pf1.LineStyle = '-';
    pf2.LineStyle = '-';
    pf3.LineStyle = '-';
    pf4.LineStyle = '-';
    pf1.Color = c.flow_color;
    pf2.Color = c.flow_color;
    pf3.Color = c.flow_color;
    pf4.Color = c.flow_color;
    pf1_2.HandleVisibility = 'off';
    pf2_2.HandleVisibility = 'off';
    pf3_2.HandleVisibility = 'off';
    pf4_2.HandleVisibility = 'off';
    pf1_2.LineStyle = '-';
    pf2_2.LineStyle = '-';
    pf3_2.LineStyle = '-';
    pf4_2.LineStyle = '-';
    pf1_2.Color = c.flow_color;
    pf2_2.Color = c.flow_color;
    pf3_2.Color = c.flow_color;
    pf4_2.Color = c.flow_color;
    pf1_2.Marker = 'none';
    pf2_2.Marker = 'none';
    pf3_2.Marker = 'none';
    pf4_2.Marker = 'none';
    pf1.LineWidth = c.flow_width;
    pf2.LineWidth = c.flow_width;
    pf3.LineWidth = c.flow_width;
    pf4.LineWidth = c.flow_width;
    pf1_2.LineWidth = c.flow_width;
    pf2_2.LineWidth = c.flow_width;
    pf3_2.LineWidth = c.flow_width;
    pf4_2.LineWidth = c.flow_width;

    %% plot pid
    yyaxis right; ylabel('PID (V)')
    ylim([-.1 5.5]);
    % first trial: shift pid data to zero
    E1_pid_shifted1(:,1) = E1_pid(:,1) - E1_flow.events.OV_keep(i).t_event;
    E1_pid_shifted1(:,2) = E1_pid(:,2);
    E2_pid_shifted1(:,1) = E2_pid(:,1) - E2_flow.events.OV_keep(i).t_event;
    E2_pid_shifted1(:,2) = E2_pid(:,2);
    E3_pid_shifted1(:,1) = E3_pid(:,1) - E3_flow.events.OV_keep(i).t_event;
    E3_pid_shifted1(:,2) = E3_pid(:,2);
    E4_pid_shifted1(:,1) = E4_pid(:,1) - E4_flow.events.OV_keep(i).t_event;
    E4_pid_shifted1(:,2) = E4_pid(:,2);
    pp1 = plot(E1_pid_shifted1(:,1),E1_pid_shifted1(:,2),'DisplayName','E1 PID');
    pp2 = plot(E2_pid_shifted1(:,1),E2_pid_shifted1(:,2),'DisplayName','E2 PID');
    pp3 = plot(E3_pid_shifted1(:,1),E3_pid_shifted1(:,2),'DisplayName','E3 PID');
    pp4 = plot(E4_pid_shifted1(:,1),E4_pid_shifted1(:,2),'DisplayName','E4 PID');

    % second trial: shift pid data to 0
    E1_pid_shifted2(:,1) = E1_pid(:,1) - E1_flow.events.OV_keep(i+1).t_event;
    E1_pid_shifted2(:,2) = E1_pid(:,2);
    E2_pid_shifted2(:,1) = E2_pid(:,1) - E2_flow.events.OV_keep(i+1).t_event;
    E2_pid_shifted2(:,2) = E2_pid(:,2);
    E3_pid_shifted2(:,1) = E3_pid(:,1) - E3_flow.events.OV_keep(i+1).t_event;
    E3_pid_shifted2(:,2) = E3_pid(:,2);
    E4_pid_shifted2(:,1) = E4_pid(:,1) - E4_flow.events.OV_keep(i+1).t_event;
    E4_pid_shifted2(:,2) = E4_pid(:,2);
    pp1_2 = plot(E1_pid_shifted2(:,1),E1_pid_shifted2(:,2));
    pp2_2 = plot(E2_pid_shifted2(:,1),E2_pid_shifted2(:,2));
    pp3_2 = plot(E3_pid_shifted2(:,1),E3_pid_shifted2(:,2));
    pp4_2 = plot(E4_pid_shifted2(:,1),E4_pid_shifted2(:,2));

    %{
    pp1 = plot(E1_pid(:,1),E1_pid(:,2),'DisplayName','E1 PID');
    pp2 = plot(E2_pid(:,1),E2_pid(:,2),'DisplayName','E2 PID');
    pp3 = plot(E3_pid(:,1),E3_pid(:,2),'DisplayName','E3 PID');
    pp4 = plot(E4_pid(:,1),E4_pid(:,2),'DisplayName','E4 PID');
    %}

    t_start = t_start - 2;
    t_end = t_end + 5;
    xlim([t_start t_end]);
    xlim([0 20]);
    %% plot things
    
    
    pp1.Color = c.E1_color;
    pp2.Color = c.E2_color;
    pp3.Color = c.E3_color;
    pp4.Color = c.E4_color;
    pp1_2.Color = c.E1_color;
    pp2_2.Color = c.E2_color;
    pp3_2.Color = c.E3_color;
    pp4_2.Color = c.E4_color;
    pp1.LineStyle = '-';
    pp2.LineStyle = '-';
    pp3.LineStyle = '-';
    pp4.LineStyle = '-';
    pp1_2.LineStyle = '-';
    pp2_2.LineStyle = '-';
    pp3_2.LineStyle = '-';
    pp4_2.LineStyle = '-';
    pp1.LineWidth = c.pid_width;
    pp2.LineWidth = c.pid_width;
    pp3.LineWidth = c.pid_width;
    pp4.LineWidth = c.pid_width;
    pp1_2.Marker = 'none';
    pp2_2.Marker = 'none';
    pp3_2.Marker = 'none';
    pp4_2.Marker = 'none';
    pp1_2.HandleVisibility = 'off';
    pp2_2.HandleVisibility = 'off';
    pp3_2.HandleVisibility = 'off';
    pp4_2.HandleVisibility = 'off';
    pp1_2.LineWidth = c.pid_width;
    pp2_2.LineWidth = c.pid_width;
    pp3_2.LineWidth = c.pid_width;
    pp4_2.LineWidth = c.pid_width;

end



