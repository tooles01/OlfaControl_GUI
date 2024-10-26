# analysis_plot_standard_olfa
**Plot standard olfactometer datafile**

## Description

## Examples

## Function Details

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

## Dependencies

