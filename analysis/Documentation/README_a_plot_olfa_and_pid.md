# a_plot_olfa_and_pid
Plot olfactometer & PID data over time

## Syntax
`a_plot_olfa_and_pid(fileName,plot_opts)`  

## Description





## Function Details
** need to finish

1. Loads .mat file (from *OlfaControlGUI\analysis\data (.mat files)*)
2. Plots selected data over time
	- left yaxis: olfa flow
	- right yaxis: user selects one: olfa ctrl, pid, or output flow sensor  
<br>



## Examples




## Input Arguments


**fileName - Name of file to be plotted**  
&nbsp;&nbsp;&nbsp;&nbsp;File must have already been parsed using [analysis_get_and_parse_files](analysis_get_and_parse_files.md)

olfa_flow
olfa_ctrl
pid
output_flow
flow_in_SCCM
ctrl_in_V
plot_in_minutes
ctrl_ylims
pid_ylims






## Other

<br>
<details>
<summary>options:</summary>

- olfa:
	- flow as int or sccm
	- plot ctrl values on right yaxis
		- ctrl as int or voltage
- pid:
	- plot or don't plot
- output flow:
	- plot or don't plot
- time scale in seconds or minutes
</details>

<details>
<summary>dependencies:</summary>

- *none*
</details>
<br>

