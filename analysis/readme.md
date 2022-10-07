
## analysis_get_and_parse_files

- load selected datafile
- parse header (PID gain, calibration tables)
	- (import calibration tables if necessary)
- adjust PID (set baseline to zero, divide by gain)
- convert flow to sccm
- convert ctrl to voltage
- save .mat file