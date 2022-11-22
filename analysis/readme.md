
## get files:
### analysis_get_and_parse_files
**gets raw .csv datafile, saves as .mat file**

1. loads selected datafile (from OlfaControlGUI\result_files)
2. parses header (PID gain, calibration tables)
	- imports calibration tables if necessary
3. adjusts PID (sets baseline to zero, divide by gain)
4. converts flow to sccm
5. converts ctrl to voltage
6. saves .mat file

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