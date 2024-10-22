# analysis_get_and_parse_files

### Get raw *.csv datafile and save as *.mat file

## Description

<!--** add where it gets the file from and where it saves it to-->

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
8. Creates sorted data structure of viable "open vial" events (*d_olfa_data_combined*)
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
