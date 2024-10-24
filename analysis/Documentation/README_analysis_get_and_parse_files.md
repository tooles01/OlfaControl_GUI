# analysis_get_and_parse_files

### Get raw *.csv datafile and save as *.mat file

## Description

<!--** add where it gets the file from and where it saves it to-->

1. **Adds necessary folders to path** (datafiles & functions)
	<details>

	- Check if current directory contains 'OlfaControl_GUI' (If not, display error message)  
	- Add datafiles to matlab path (*"result_files\48-line olfa"*)
	- Add functions to matlab path (*"analysis\functions"*)
	</details>
<br>

2. **Loads selected datafile** (from *OlfaControlGUI\result_files\48-line olfa*)
	- *Note:* User must enter datafile name (& PID units, if recorded in mV)
	
	<details>
	
	- Parse out file date & get full directory for this file
		- *OlfaControl_GUI\result_files\48line olfa\\<a_thisfile_date>*
		- **Note:** All datafile names must begin with the date and be in the folder for that date (Ex: '2024-10-24_datafile_00')
	- Get the .mat file
		- **import_datafile.m**
			- Get path to where this raw datafile should be (*analysis\data files (raw)\file_name.mat*)
			- If the raw datafile does not exist yet:
				- Get full directory to this .csv file
				- Read .csv file & save as .mat file (*datafiles (raw)*)
			- If it does exist: Load the .mat file
	</details>
<br>

3. **Parses header** (PID gain & calibration tables)
	- Get calibration table names & PID gain from header, save to *c.this_exp_cal_tables* and *c.pid_gain*

4. **Parses data**
	- Convert time into seconds
	- Sort each line into a data structure depending on the instrument (PID, flow sensor, olfactometer)
		<details>
		
		- PID: data_pid_raw
		- Flow sensor: data_fsens_raw 
		- Olfactometer:
			- Get the vial number
			- If it was only one vial:
				- If this is the first line of data for this vial: Initialize empty data structures for this vial
				- Check what type of data this is (flow, ctrl, event) and then add to corresponding structure
			- If it was multiple vials: (we assume it was an 'OV' event)
				- For each vial affected, add to *d_olfa_flow(vial).events.OV*
				- Add this line to d_olfa_events.OV <!-- do we need this?-->
		</details>
<br>

5. **Gets calibration table names/values**
	- For each vial we have collected data for:
		- Get the name of this vial's calibration table
		- Add calibration table name to *d_olfa_flow(vial).cal_table_name* (If no calibration table was listed for this vial, use default_cal_table)
		- Get the calibration table data
			- **import_cal_table** <!--very similar to import_datafile-->
				- Get path to where this calibration table (*.mat) should be (*analysis\cal tables (imported)\file_name.mat*)
				- If the file does not exist yet:
					- Get full directory to this .csv OR .txt file
					- Read .csv/.txt file & save as .mat file (*cal tables (imported)*)
				- If it does exist: Load the .mat file
		- Add the calibration table data to *d_olfa_flow(vial).cal_table*

4. **Adjusts PID** (divides by gain & sets baseline to zero)

5. Converts flow values to sccm
6. Converts ctrl values to voltage
7. Smooths PID (moving average over 50ms window)
7. Splits into sections (for each open vial event)
	- For each event (longer than 1 second):
		- Cuts first 50 ms
		- Gets all flow & PID data (& calculates mean)
8. Creates sorted data structure of viable "open vial" events (*d_olfa_data_combined*)
9. Saves .mat file  
<br>

**Note:**  
User will need to enter **data file name** (line 57).  
--> Optional: Enter a note describing the file (will save to .mat file; is used as caption/description when running plot functions)
<br>


## Dependencies:
- get_section_data
- import_cal_table
- import_datafile
- int_to_SCCM

<!--
<details>
<summary>dependencies:</summary>

- get_section_data
- import_cal_table
- import_datafile
- int_to_SCCM
</details>
<br>
<br>
-->