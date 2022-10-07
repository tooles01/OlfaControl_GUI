

### analysis_get_and_parse_files

- load selected datafile
- parse header (PID gain, calibration tables)
	- (import calibration tables if necessary)
- adjust PID (set baseline to zero, divide by gain)
- convert flow to sccm
- convert ctrl to voltage
- save .mat file



##
### analysis_plot_olfa_and_pid

<dl>
<dt>options:</dt>
<dd>- olfa:</dd>
	<dd>- flow or ctrl values</dd>
	<dd>- flow as int or sccm</dd>
	<dd>- ctrl as int or voltage</dd>
</dd>
- pid:
	- plot or don't plot

</dl>

- load .mat file
- plot olfa flow (or ctrl) & pid over time