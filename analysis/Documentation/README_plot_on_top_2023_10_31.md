## plot_on_top_2023_10_31



- Set all of the plot options
- Get datafile names
    - (n x 1) cell of file names
- Preallocate struct array called "data"
- Load the list of files into the array
    d_olfa_data_combined
    d_olfa_flow
    data_pid
    d_olfa_data_sorted

- Get the list of flow values recorded in these files
    For each file:
        For each vial: (shouldn't there only be one?)
            Get all of the mean flow values (from d_olfa_data_sorted)... and round them to the nearest 5???
        For standard olf, same shit except variable name for "flow value" is different
    Sort the list and remove duplicates, now you have every value in these files

- Plot each flow value separately
    For each flow value:
        Create figure
        Shorten file name (for legend)
        For each file:
            8line olfa:
                Get the rows of the trials at this flow value
                For each row (trial):
                    Get the data (flow, ctrl, pid)
                    Shift it all to t=0
                    Plot ctrl/flow on left yaxis
                    Plot PID on right yaxis
            Standard olfa:
                Get the rows of the trials at this flow value
                For each row (trial):
                    Get the pid data & plot it on right yaxis



#

### Plot Options:

#### Axis Limits
**pid_lims - Y-Limits for PID data**  
**flow_lims - Y-Limits for Olfa flow data**  
**ctrl_lims - Y-Limits for Olfa ctrl data**  

<br>

#### Data Manipulation
**round_to - When getting flow means from file, round them to the nearest x**  
&nbsp;&nbsp;5 (default) | positive integer value  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;When plotting each flow rate, this is used to determine the flow values that will be plotted. (If round_to = 5, the flow values plotted will be 5,10,15,....100. If round_to = 10, the flow values plotted will be 10,20,30,...100.) (Just don't fuck with this for now, leave it at 5.)  



time_to_cut - Duration (s) to cut from beginning of event when 

<br>

#### Plot Options
**plot_by_flow - Plot each flow value individually**  
&nbsp;&nbsp;"yes" (default) | "no"  

**plot_flow - Show flow data on individual flow rate plots**  
&nbsp;&nbsp;"yes" (default) | "no"  

**plot_ctrl - Show ctrl data on individual flow rate plots & Show Flow v. Ctrl plot**  
&nbsp;&nbsp;"no" (default) | "yes"  

<p align="center">1. no ctrl (default) 2. ctrl, no flow 3. no flow, no ctrl</p>
<p align="center">
  <img src="images/plot_by_flow_flow_noctrl.jpg" width="30%">
  <img src="images/plot_by_flow_noflow_ctrl.jpg" width="30%">
  <img src="images/plot_by_flow_noflow_noctrl.jpg" width="30%">
</p>

<br>


plot_error_bars - Show error bars on Flow v. PID

**plot_by_vial - Plot color determined by vial #**  
&nbsp;&nbsp;"yes" (default) | "no"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Generally, setting this to "no" will only be used when comparing multiple trials of the same vial. Otherwise, you'll want all trials from the same vial to be the same color.

<p align="center">1. no ctrl (default) 2. ctrl, no flow 3. no flow, no ctrl</p>
<p align="center">
  <img src="images/plot_by_flow_flow_noctrl.jpg" width="30%">
  <img src="images/plot_by_flow_noflow_ctrl.jpg" width="30%">
  <img src="images/plot_by_flow_noflow_noctrl.jpg" width="30%">
</p>


shorten_file_name


















