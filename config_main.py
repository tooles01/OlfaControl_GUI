# Config variables for main.py

##############################
# PARAMETERS FOR 48-LINE OLFACTOMETER
no_active_slaves_warning = 'no active slaves pls connect olfa or something'

default_pid_gain = '1x'        # write to datafile

# PROGRAMS
default_dur_ON = 8
default_dur_OFF = 20
default_numTrials = 2
default_setpoint = '10,20,30,40,50,60,70,80,90,100'
waitBtSpAndOV = .5      # setpoint characterization
#waitBtSps = 1           # additive

##############################


# Location for log file directory (for utils.py)
# TODO move this back to utils?
result_file_folder_name = 'result_files'
calibration_file_dir_name = 'calibration_tables'
