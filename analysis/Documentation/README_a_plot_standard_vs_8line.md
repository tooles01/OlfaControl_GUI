# a_plot_standard_vs_8line



Enter data file names
    1 8line olf file
    1 standard olf file
    

Load mat files
    Data loaded in:
        8line olfa: 'd_olfa_flow', 'data_pid'
        standard olfa: 'd_olfa_data_combined','d_olfa_data_sorted'

Plot each flow value separately
    1. Find when the trial started
        d_olfa_data_combined: Find the first time where we have flow data
        d_olfa_flow.events: Find the closest OV_keep.t_event time (real time of event start, aka when the 'OV' command was sent)
    2. Use this "real event start time" and shift the PID data so t=0 is when the event starts
    3. Plot the PID data
    4. If there is a second trial here:
        d_olfa_data_combined: Find the first time where we have flow data
        d_olfa_flow.events: Find the closest OV_keep.t_event time (real time of event start)




