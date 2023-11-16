
## get files:
### analysis_get_and_parse_files
**gets raw .csv datafile, saves as .mat file**

1. loads selected datafile (from OlfaControlGUI\result_files\48-line olfa)
2. parses header (PID gain & calibration tables)
	- imports calibration tables if necessary (from OlfaControlGUI\calibration_tables)
3. adjusts PID (divides by gain & sets baseline to zero)
4. converts flow to sccm
5. converts ctrl to voltage
6. smooths PID (moving average over 50ms window)
7. splits into sections (for each OV event)
	- for each section (longer than 1 second):
		- cuts first 50 ms
		- gets all flow & PID data (& calculates mean)
8. saves .mat file

<details>
<summary>dependencies:</summary>

- get_section_data
- import_cal_table
- import_datafile
- int_to_SCCM
</details>

#
#
## for plotting:

### analysis_plot_olfa
**plots olfactometer data over time**

1. loads .mat file (from OlfaControlGUI\analysis\data (.mat files))
2. plots olfactometer flow data (over time)


<details>
<summary>options:</summary>

- flow:
	- int or sccm
- ctrl (proportional valve):
	- plot on right yaxis
	- int or voltage
</details>

<details>
<summary>dependencies:</summary>

- *none*
</details>


#
### analysis_plot_olfa_and_pid
**plots olfactometer & pid data over time**

1. loads .mat file (from OlfaControlGUI\analysis\data (.mat files))
2. plots selected data over time
	- left yaxis: olfa flow
	- right yaxis: user selects one: olfa ctrl, pid, or output flow sensor


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
</details>


<details>
<summary>dependencies:</summary>

- *none*
</details>


#
### analysis_spt_char
**plots flow v. pid**

1. loads .mat file (from OlfaControlGUI\analysis\data (.mat files))
2. cuts additional time from each event section (user specifies how many seconds)
	- recalculates means & standard deviations, adds them back into the structs
2. plots flow & PID data over time
3. if selected, plots each event section individually
4. plots mean flow values v. mean PID values
	- if selected, plot error bars


<details>
<summary>options:</summary>

- plot each individual event
	- show mean flow/PID on that figure
- flow as int or sccm 
</details>


<details>
<summary>dependencies:</summary>

- get_section_data
</details>



#
### analysis_plot_standard_olfa
**plots file from standard olfa**

--> different file type: (data starts at 4th row of file)
- Column 1: vial number
- Column 2: flow rate
- Column 3 -> end: PID values



1. loads .csv file (from OlfaControlGUI\results_files\standard olfa)
2. calculates PID baseline value (minimum PID value recorded during first trial)
3. for each trial:
	- adjust PID
		- remove missing cells
		- make array of time values
		- shift PID up to zero
	- calculate mean PID
		- only use specific section of data:
			- beginning of dataset: cut off the # of seconds specified by user
			- end of dataset: 0.1sec before PID drops below 0.1V
	- plot trial (if user selected to)
	- add mean (& std) to the data structure
4. create combined data structure
5. save it to C:\..\data (.mat files)
6. plot the spt char figure

