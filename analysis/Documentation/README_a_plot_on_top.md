# a_plot_on_top
**Plot data from multiple files on top of each other**

Plot a bunch of files on top of each other. can plot by flow value, can do flow v. PID spt char, flow v. ctrl spt char, can handle standard olfa files.  

## Syntax:
`a_plot_on_top(file_names,a_title,a_subtitle)` plots the files in the array `file_names`  
<br>

<!--## Examples-->

## Function Details

1. **Adds necessary folders to MATLAB path** (datafiles & functions)  

2. **Loads files in**  
    <details>

    - Preallocate struct array `data`
    - Load the list of files into the array
        - Variables loaded: `d_olfa_data_combined`, `d_olfa_flow`,`data_pid`,`d_olfa_data_sorted`
    - Get list of flow values recorded in these files
        - For each file:
            - For each vial: (shouldn't there only be one?)
                - Get all of the mean flow values (from d_olfa_data_sorted)... and round them to the nearest 5???
            - For standard olf, same shit except variable name for "flow value" is different
        - Sort the list and remove duplicates, now you have every value in these files
    </details>

3. If selected: **Plots each flow value separately**  
    `c.plot_by_flow`
    <p align="center">
        <img src="images/examples/plot_on_top_plot_all_01.jpg" width="30%">
        <img src="images/examples/plot_on_top_plot_all_02.jpg" width="30%">
    </p>
    
    <details>
    
    - For each flow value:
        - Create figure
        - For each file:
            - If **8line olfa**:
                - Get the rows of the trials at this flow value
                - For each row (trial/event):
                    - Get the data (flow, ctrl, pid)
                    - Shift it all to t=0
                    - Plots data
                        - If selected: **Plots ctrl values** on left yaxis (`c.plot_ctrl`)
                        - If selected: **Plots flow values** on left yaxis (`c.plot_flow`)
                        - **Plots PID** on right yaxis
                            - If neither flow nor ctrl are selected to be plotted, put PID on left yaxis
            - If **Standard olfa**:
                - Get the rows of the trials at this flow value
                - For each row (trial):
                    - Get the PID data & plot it on right yaxis
    </details>

4. **Flow v. PID plot**  
    and if selected, **Flow v. Ctrl plot** (`c.plot_ctrl`)  
    <p align="center">
        <img src="images/examples/plot_on_top_flowVpid.jpg" width="30%">
        <img src="images/examples/plot_on_top_flowVctrl.jpg" width="30%">
    </p>
    
    <details>

        - Create/set up both plots (title, legend, labels, etc)
        - For each file:
            - If **8-line olfa**:
                - For each vial:
                    - Initialize empty structures & get data from *d_olfa_flow.events.OV_keep*
                    - For each event: **Cut data & calculate mean/std**
                        - Get data from this event (flow, ctrl, pid)
                        - Cut off the first *c.time_to_cut* seconds
                        - Calculate mean & standard deviation (from cut data) & add to new data structures
                    - Put the stats into data(r).new_means
                        - (-->It doesn't seem data(r).new means is ever used, we only use this_file_new_means within this loop, can maybe remove this)
                    - **Plot Flow v. PID means** (figure 2)
                        - Add this file's data to the plot
                        - If selected:
                            - Shorten file name (`c.shorten_file_name`)
                            - Plot by vial number (`c.plot_by_vial`)
                    - If selected: **Plot Flow v. Ctrl means** (figure 3)
                        - Add this file's data to the plot
                        - If selected:
                            - Shorten file name (`c.shorten_file_name`)
                            - Plot by vial number (`c.plot_by_vial`)
                    - If selected: **Plot error bars** (`c.plot_error_bars`)
                        - Initialize empty structures (for creating error bars)
                        - For each event:
                            - Get flow, PID, ctrl standard deviations from the structures you just made before (this_file_new_stds, this_file_ctrl_stds)
                            - Divide by two and add to (xneg, xpos, etc) (divide by 2 so that entire length of the error bar = 1 standard deviation)
                        - Plot Flow & PID error bars on ax2
                        - If selected: Plot ctrl error bars on ax3 (`c.plot_ctrl`)
            - If **Standard olfa**:
                - not today
    </details>

## Input Arguments

### Required:
**file_names - Names of files to be plotted**  
&nbsp;&nbsp;(nx1) cell array of file names  
&nbsp;&nbsp;&nbsp;&nbsp;*Note:* Files must have already been parsed using [analysis_get_and_parse_files](analysis_get_and_parse_files.md)  
**a_title - Figure title** (usually the date)  
**a_subtitle - Figure subtitle**  
<br>

### Plot Options
**plot_by_flow - Plot each flow value individually**  
**plot_flow - Plot flow values on left yaxis** (8-line olfa)  
**plot_ctrl - Plot ctrl values on left yaxis** (8-line olfa)  
<br>

### Axis Limits  
Note: highly recommend entering PID lims  
**pid_lims - Y-Limits for PID data**  
&nbsp;&nbsp;[0 5] (default) | two-element vector  
**flow_lims - Y-Limits for Olfa flow data**  
&nbsp;&nbsp;[0 105] (default) | two-element vector  
**ctrl_lims - Y-Limits for Olfa ctrl data**  
&nbsp;&nbsp;[0 260] (default) | two-element vector  
<br>

### Data Manipulation
**round_to - When getting flow means from file, round them to the nearest 'x'**  
&nbsp;&nbsp;5 (default) | positive integer value  
&nbsp;&nbsp;&nbsp;&nbsp;->When plotting each flow rate, this is used to determine the flow values that will be plotted. (If round_to = 5, the flow values plotted will be 5,10,15,....100. If round_to = 10, the flow values plotted will be 10,20,30,...100.) (Just don't fuck with this for now, leave it at 5.)  

**time_to_cut - Duration (seconds) to cut from beginning of each section**  
&nbsp;&nbsp;6 (default) | positive value  
&nbsp;&nbsp;&nbsp;&nbsp;->Duration (seconds) to cut from the beginning of each section before recalculating stats (mean, standard deviation). This is used to remove the first few seconds from the trial (the period when PID has not yet reached its peak/plateau value)  
<br>

### Other
**plot_error_bars -**  
&nbsp;&nbsp;'yes' (default) | 'no'  
**plot_by_vial - Colors based on vial number**  
&nbsp;&nbsp;'yes' (default) | 'no'  
<br>

### Data to show on plot
**shorten_file_name - shorten file name in legend**  
&nbsp;&nbsp;'no' (default) | 'yes'  


## Plot Options:
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
  <img src="images/examples/plot_by_flow_flow_noctrl.jpg" width="30%">
  <img src="images/examples/plot_by_flow_noflow_ctrl.jpg" width="30%">
  <img src="images/examples/plot_by_flow_noflow_noctrl.jpg" width="30%">
</p>

<br>


plot_error_bars - Show error bars on Flow v. PID

**plot_by_vial - Plot color determined by vial #**  
&nbsp;&nbsp;"yes" (default) | "no"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Generally, setting this to "no" will only be used when comparing multiple trials of the same vial. Otherwise, you'll want all trials from the same vial to be the same color.

<p align="center">1. no ctrl (default) 2. ctrl, no flow 3. no flow, no ctrl</p>
<p align="center">
  <img src="images/examples/plot_by_flow_flow_noctrl.jpg" width="30%">
  <img src="images/examples/plot_by_flow_noflow_ctrl.jpg" width="30%">
  <img src="images/examples/plot_by_flow_noflow_noctrl.jpg" width="30%">
</p>



## Dependencies
- get_section_data