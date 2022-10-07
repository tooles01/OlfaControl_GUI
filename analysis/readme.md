
## get files:
### analysis_get_and_parse_files

- load selected datafile
- parse header (PID gain, calibration tables)
	- (import calibration tables if necessary)
- adjust PID (set baseline to zero, divide by gain)
- convert flow to sccm
- convert ctrl to voltage
- save .mat file




#

## for plotting (over time):

### analysis_plot_olfa

- load .mat file
- plot olfa flow

#### options:
- flow as int or sccm
- plot ctrl on right yaxis
- ctrl as int or voltage



#
### analysis_plot_olfa_and_pid

- load .mat file
- plot over time
	- left yaxis: olfa flow
	- right yaxis: olfa ctrl, pid, or output flow sensor


#### options:
- olfa:
	- flow or ctrl values
	- flow as int or sccm
	- ctrl as int or voltage
- pid:
	- plot or don't plot
- output flow:
	- plot or don't plot