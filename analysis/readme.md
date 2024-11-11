# When running functions, Matlab directory must be '**OlfaControlGUI\analysis'

(*import_datafile.m* will not run otherwise)

<br>

# Load data files:
## analysis_get_and_parse_files.m
**Get raw \*.csv datafile and save as \*.mat file.**  

<details><summary>
Description:</summary>

- Loads *.csv datafile from *OlfaControl_GUI\result_files\48-line olfa*  
- Saves raw file to *OlfaControl_GUI\analysis\data files (raw)*  
- Parses file, converts units, creates data structures, etc  
- Saves parsed file to *OlfaControl_GUI\analysis\data (.mat files)*  

**Note:** User must enter datafile name (line 57ish)
</details>

<details><summary>
Dependencies:</summary>

- get_section_data
- import_cal_table
- import_datafile
- int_to_SCCM
- removeDuplicates_
</details><br>

**More details [here](Documentation/README_analysis_get_and_parse_files.md)**  
<br>
<br>

# Plotting:

## a_plot_olfa_and_pid.m
**Plot olfactometer & PID data over time**  

**Syntax**  
`a_plot_olfa_and_pid(a_thisfile_name)` creates a plot of the data in the given file over time.  
`a_plot_olfa_and_pid(a_thisfile_name,plot_opts)` specifies the plot options.  
<br>

**Example:**  
`a_plot_olfa_and_pid('2023-11-02_datafile_04',pid_ylims=[0 3.5]);`<p align="center"><img src="Documentation/images/examples/plot_olfapid_default.jpg" width="50%"></p>

<details><summary>
Dependencies:</summary>

- get_section_data
</details><br>

**More details [here](Documentation/README_a_plot_olfa_and_pid.md)**  
<br>


## a_plot_spt_char.m
**Plot setpoint characterization of trial** (Flow v. PID plot)  

**Syntax**  
`a_plot_spt_char(filename)` plots the setpoint characterization figure (flow vs. PID) of the given file.  
`a_plot_spt_char(filename,plot_opts)` plots the setpoint characterization figure (flow vs. PID) of the given file using the additional plot options specified.  
<br>

**Example:**  
`a_plot_spt_char('2024-01-09_datafile_01');`<p align="center"><img src="Documentation/images/examples/spt_char_default.jpg" width="40%"></p>

<details><summary>
Dependencies:</summary>

- get_section_data
</details><br>

**More details [here](Documentation/README_a_plot_spt_char.md)**  
<br>

## a_plot_on_top
**Plot a bunch of files on top of each other**

**Syntax**  
`a_plot_spt_char(file_names,a_title,a_subtitle)` plots the files in the array `file_names`  

<details><summary>
Dependencies:</summary>

</details><br>

### Example:


### More details [here](Documentation/README_a_plot_on_top.md)

## analysis_plot_standard_olfa.m
**Plot file from standard olfactometer**

<details><summary>
Description:</summary>

- Loads \*.csv file (from *OlfaControl_GUI\results_files\standard olfa*)
- Parses file & saves to *OlfaControl_GUI\analysis\data (.mat files)*
- Plots the setpoint characterization figure
</details>

<details><summary>
Dependencies:</summary>

- get_section_data
</details><br>

**More details [here](Documentation/README_plot_standard_olfa.md)**  