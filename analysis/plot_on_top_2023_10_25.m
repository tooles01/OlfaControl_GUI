% plot on top of another fig

a = p.Color; clearvars -except a

% load file
load 2023-10-18_datafile02_2.mat


yyaxis left; p4 = plot(d_olfa_flow_x,d_olfa_flow_y,'HandleVisibility','off'); p4.Color = a;
yyaxis right; p3 = plot(d_pid_x,d_pid_y,'HandleVisibility','off');
p3.Color = '#77AC30'; p3.LineWidth = 1.5; p3.LineStyle = '-';