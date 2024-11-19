# a_plot_olfa_and_pid
Plot olfactometer & PID data over time

## Syntax
`a_plot_olfa_and_pid(fileName,plot_opts)`  

## Description
`a_plot_olfa_and_pid(filename)` plots the flow and PID data of the given file (over the duration of the trial).  
`a_plot_olfa_and_pid(filename,plot_opts)` plots the given file using the additional plot options specified.  


## Examples


## Function Details
** need to finish  
** need to do something about which can be on which axis  

1. **Adds necessary folders to MATLAB path** (datafiles & functions)  
	<details>

	- Check if current directory contains 'OlfaControl_GUI' (If not, display error message)  
	- Add datafiles to path: *"result_files\48-line olfa"*
	- Add functions to path: *"analysis\functions"*
	</details>

2. **Loads \*.mat file** from *OlfaControlGUI\analysis\data (.mat files)*  

3. **Plots selected data over time**
	- Create/set up figure
		- If selected: Set X limits (`f.x_lim`)
	- **Plot olfa flow**
		- For each vial:
			- Get data to plot (SCCM or int) (`plot_opts.flow_in_SCCM`)
			- If selected: Scale time (`f.scale_time`)
			- If selected: Change timescale to minutes (`plot_opts.plot_in_minutes`)
			- **Plot olfa flow**
	- If selected: **Plot olfa ctrl** (right yaxis, left if flow data is plotted) (`plot_opts.olfa_ctrl`)
		- For each vial:
			- Get data to plot (int or voltage) (`plot_opts.ctrl_in_V`)
			- If olfa flow is not plotted: put ctrl on left yaxis (`plot_opts.olfa_flow`)
				- If olfa flow is plotted, put ctrl on right yaxis
			- If selected: Scale time (`f.scale_time`)
			- If selected: Change timescale to minutes (`plot_opts.plot_in_minutes`)
			- **Plot olfa ctrl**
	- If selected: **Plot PID** (right yaxis) (`plot_opts.pid`)
		- If selected: Scale time (`f.scale_time`)
		- If selected: Change timescale to minutes (`plot_opts.plot_in_minutes`)
		- **Plot PID**
	- If selected: **Plot output flow sensor** (right yaxis) (`plot_opts.output_flow`)
	- If selected: **Plot calibration value** (left yaxis) (`f.calibration_value`)


## Input Arguments

**fileName - Name of file to be plotted**  
&nbsp;&nbsp;&nbsp;&nbsp;File must have already been parsed using [analysis_get_and_parse_files](analysis_get_and_parse_files.md)

### Data to plot
**olfa_flow - Plot olfa flow data**  
&nbsp;&nbsp;'yes' (default) | 'no'  
**olfa_ctrl - Plot olfa ctrl data**  
&nbsp;&nbsp;'no' (default) | 'yes'  
**pid - Plot PID data**  
&nbsp;&nbsp;'yes' (default) | 'no'  
**output_flow - Plot output flow sensor data**  
&nbsp;&nbsp;'no' (default) | 'yes'  
<br>

### Units  
**flow_in_SCCM - Plot flow values in SCCM**  
&nbsp;&nbsp;'yes' (default) | 'no'  
&nbsp;&nbsp;&nbsp;&nbsp;Plot flow values in SCCM - if 'no' is selected, integer values will be plotted.  
**ctrl_in_V - Plot ctrl values in V**  
&nbsp;&nbsp;'no' (default) | 'yes'  
&nbsp;&nbsp;&nbsp;&nbsp;Plot ctrl values in V - if 'no' is selected, integer values will be plotted.  
**plot_in_minutes - Plot trial over minutes instead of seconds**  
&nbsp;&nbsp;'no' (default) | 'yes'  
<br>

### Axis Limits  
**pid_ylims - Y-Limits for PID data**  
&nbsp;&nbsp;[0 3] (default) | two-element vector  
**flow_ylims - Y-Limits for Olfa flow data**  
&nbsp;&nbsp;two-element vector  
**ctrl_ylims - Y-Limits for Olfa ctrl data**  
&nbsp;&nbsp;[-5 260] (default) | two-element vector  
<br>

** need to finish shifting stuff over to input arguments probably
<br>


## Dependencies
- get_section_data