# When running functions, Matlab directory must be '**OlfaControlGUI\analysis'

(*import_datafile.m* will not run otherwise)

<br>

# Load data files:
## analysis_get_and_parse_files.m
Get raw .csv datafile and save as .mat file.
<br>

More information [here](Documentation/README_analysis_get_and_parse_files.md)

<br>
<br>

# Plotting:

## a_plot_olfa_and_pid.m
Plot olfactometer & PID data over time

<br>

`a_plot_olfa_and_pid(a_thisfile_name)` creates a plot of the data in the given file over time.  
`a_plot_olfa_and_pid(a_thisfile_name,plot_opts)` specifies the plot options.  
<br>

More information [here](Documentation/README_a_plot_olfa_and_pid.md)

<br>


## a_plot_spt_char.m
Plot setpoint characterization of trial (Flow v. PID plot)

<br>

`a_plot_spt_char(filename)` plots the setpoint characterization figure (flow vs. PID) of the given file.  
`a_plot_spt_char(filename,plot_opts)` plots the setpoint characterization figure (flow vs. PID) of the given file using the additional plot options specified.  
<br>

### Example Figures

<!--didn't put them in yet  -->
<br>

### Further Information
More details [here](Documentation/README_a_plot_spt_char.md)

<br>


## analysis_plot_standard_olfa.m
Plot file from standard olfactometer

--> different file type: (data starts at 4th row of file)
- Column 1: vial number
- Column 2: flow rate
- Column 3 -> end: PID values

1. Loads .csv file (from *OlfaControlGUI\results_files\standard olfa*)
2. Calculates PID baseline value (minimum PID value recorded during first trial)
3. For each trial:
	- Adjust PID
		- remove missing cells
		- make array of time values
		- shift PID up to zero
	- Calculate mean PID
		- only use specific section of data:
			- beginning of dataset: cut off the # of seconds specified by user
			- end of dataset: 0.1sec before PID drops below 0.1V
	- Plot trial (if user selected to)
	- Add mean (& std) to the data structure
4. Create combined data structure
5. Save it to *C:\..\data (.mat files)*
6. Plot the spt char figure


