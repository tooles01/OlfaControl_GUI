# When running functions, Matlab directory must be '**OlfaControlGUI\analysis'

(*import_datafile.m* will not run otherwise)

<br><br>

# Load data files:
### Get raw *.csv datafile and save as *.mat file
**analysis_get_and_parse_files.m**
1. Loads selected datafile (from *OlfaControlGUI\result_files\48-line olfa*)
2. Parses header (PID gain & calibration tables)
	- Imports calibration tables if necessary (from *OlfaControlGUI\calibration_tables*)
3. Adjusts PID (divides by gain & sets baseline to zero)
4. Converts flow values to sccm
5. Converts ctrl values to voltage
6. Smooths PID (moving average over 50ms window)
7. Splits into sections (for each open vial event)
	- For each event (longer than 1 second):
		- Cuts first 50 ms
		- Gets all flow & PID data (& calculates mean)
8. Saves .mat file  
<br>

**Note:**  
User will need to enter **data file name** (line 57).  
--> Optional: Enter a note describing the file (will save to .mat file; is used as caption/description when running plot functions)
<br>
<details>
<summary>dependencies:</summary>

- get_section_data
- import_cal_table
- import_datafile
- int_to_SCCM
</details>
<br>
<br>

# Plotting:

## Plot olfactometer data over time
**analysis_plot_olfa.m**
1. Loads .mat file (from *OlfaControlGUI\analysis\data (.mat files)*)
2. Plots olfactometer flow data (over time)  
<br>

**Note:**  
User will need to enter **data file name** (line 69).  

<details>
<summary>options:</summary>

- flow: plot as int or sccm
- ctrl (proportional valve):
	- plot (or don't) on right yaxis
	- plot as integer or voltage
</details>

<details>
<summary>dependencies:</summary>

- *none*
</details>
<br>

## Plot olfactometer & PID data over time
**analysis_plot_olfa_and_pid.m**
1. Loads .mat file (from *OlfaControlGUI\analysis\data (.mat files)*)
2. Plots selected data over time
	- left yaxis: olfa flow
	- right yaxis: user selects one: olfa ctrl, pid, or output flow sensor  
<br>

**Note:**  
User will need to enter **data file name** (line 63).  

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

## Plot flow v. PID
**analysis_spt_char.m**

1. Loads .mat file (from *OlfaControlGUI\analysis\data (.mat files)*)
2. Cuts additional time from each event section (user specifies how many seconds)
	- Recalculates means & standard deviations, adds them back into the structs
2. Plots flow & PID data over time
3. If selected, plots each event section individually
4. Plots mean flow values v. mean PID values
	- If selected, plot error bars  
<br>

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
<br>

## Plot file from standard olfactometer
**analysis_plot_standard_olfa.m**

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

