#
##

### analysis_get_and_parse_files

- load selected datafile
- parse header (PID gain, calibration tables)
	- (import calibration tables if necessary)
- adjust PID (set baseline to zero, divide by gain)
- convert flow to sccm
- convert ctrl to voltage
- save .mat file




### analysis_plot_olfa_and_pid

**options:**
- olfa:
	- flow or ctrl values
	- flow as int or sccm
	- ctrl as int or voltage
- pid:
	- plot or don't plot


- load .mat file
- plot olfa flow (or ctrl) & pid over time