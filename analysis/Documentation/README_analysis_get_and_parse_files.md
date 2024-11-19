# analysis_get_and_parse_files

**Get raw \*.csv datafile and save as \*.mat file**  
<!--** add where it gets the file from and where it saves it to-->

## Function Details

1. **Adds necessary folders to MATLAB path** (datafiles & functions)
	<details>

	- Check if current directory contains 'OlfaControl_GUI' (If not, display error message)  
	- Add datafiles to matlab path (*"result_files\48-line olfa"*)
	- Add functions to matlab path (*"analysis\functions"*)
	</details>

2. **Loads selected datafile** (from "*OlfaControlGUI\result_files\48-line olfa*")  
	*Note:* User must manually enter datafile name here (& PID units, if recorded in mV)
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

3. **Parses header**  
	Gets calibration table names & PID gain from header  
	Saves to *c.this_exp_cal_tables* and *c.pid_gain*  

4. **Parses data**  
	Converts time to seconds  
	Sorts each line into a data structure depending on the instrument (PID, flow sensor, olfactometer)  
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

5. **Gets calibration table names/values**
	<details>
	
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
	</details>

6. **Adjusts PID**  
	Divides by gain, sets baseline to zero  
	<details>
	
	- Divide by PID gain
	- Set baseline to zero
		- Calculate the mean of the PID data up until the first OV event
		- Subtract from all PID data
	- If selected: Convert from mV to V (*c.PID_in_V*)
	</details>

7. **Converts flow values to SCCM**  
	<details>

	- For each vial:
		- If there are flow values (*d_olfa_flow.flow.flow_int*):
			- Use the calibration table to convert to SCCM (**int_to_SCCM**)
	</details>

8. **Converts ctrl values to voltage**  
	(Probably unnecessary because we never use this)
	<details>

	- For each vial:
		- If there are ctrl values (*d_olfa_flow.ctrl.ctrl_int*):
			- Convert to voltage
	</details>

9. **Smooths PID** (moving average over 50ms window)
	<details>

	- If there is PID data:
		- Remove any data points with duplicate time values (**removeDuplicates_**)
		- Do the moving average over 50ms window
	</details>

10. **Splits into sections** (each open vial event)
	<details>
	<br>
	
	**Get stats for each event**
	- For each vial:
		- Get event data (*d_olfa_flow.events.OV*), flow data, and initialize empty structures
		- For each event:
			- If the event was longer than 1 second:
				- Cut first 50 ms
				- Get flow & PID data for this section
				- Calculate mean flow & PID, add to *int_means* and *sccm_means*
				- Add other stats you just calculated to *e_new_event_struct*
			- Add *e_new_event_struct* to *d_olfa_flow.events.OV*:
			<p align="center"><img src="images/data structures/d_olfa_flow.events.OV_after_loop.png" width="70%"></p>
			
			- Add *int_means* and *sccm_means* to *d_olfa_flow*:  
			<p align="center"><img src="images/data structures/int_sccm_means.png" width="40%"></p>

	**Copy legitimate events into OV_keep**
	- Remove empty rows: events longer than 1sec go into OV_keep  
		Truly unclear when I had events less than 1 second, unless this was for fuckups/pressurization?  
		- For each vial:
			- Get event data (*d_olfa_flow.events.OV*)
				- For each event: copy all the information into *d_olfa_flow.events.OV_keep*
				<p align="center"><img src="images/data structures/d_olfa_flow.events.OV_keep.png" width="70%"></p>
	</details>

11. **Creates sorted data structure** of viable "open vial" events (*d_olfa_data_combined*)
	<details>

	- For each vial:
		- Put *OV_keep* events into *sourceStructArray*
		- For each event, copy `flow_mean_sccm`, `pid_mean`, and `data` into *targetStructArray*  
		<p align="center"><img src="images/data structures/targetStructArray.png" width="35%"></p>

		- Sort events from lowest-->highest flow (*d_olfa_data_sorted*)
		<p align="center"><img src="images/data structures/d_olfa_data_sorted_2.png" width="35%"></p>

		- Create *d_olfa_data_combined* (using *flow_inc* entered at beginning of file)
		<p align="center"><img src="images/data structures/d_olfa_data_combined_2.png" width="35%"></p>
	</details>

12. **Saves .mat file** to "*OlfaControl_GUI\analysis\data (.mat files)*"  
<p align="center"><img src="images/data structures/file_saved.png" width="50%"></p>
<br>

**Note:**  
User will need to enter **data file name** (line 57).  
--> Optional: Enter a note describing the file (will save to .mat file; is used as caption/description when running plot functions)
<br>
<!-- move this to where it belongs ^^^^^^-->


## Dependencies:
- get_section_data
- import_cal_table
- import_datafile
- int_to_SCCM
- removeDuplicates_