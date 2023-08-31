
##############################
# HAS TO MATCH THE ARDUINO CODE
baudrate = 9600     # for communicating w/ master
##############################



##############################
# DONT CHANGE THIS STUFF
vialsPerSlave = 8
master_modes = ["6: verbose",
                "5: trace",
                "4: notice",
                "3: warning",
                "2: error",
                "1: fatal"]
slave_names = ['A','B','C','D','E','F']
cal_table_file_tyoe = '.txt'
##############################



##############################
# # DEFAULT VALUES
# TODO: find a way to ensure this matches what the Arduino has
# (or have the slave send back what it has stored, then update the GUI)
def_timebt = '100'
def_setpoint = '50'
def_open_duration = '5'
default_cal_table = 'Honeywell_3100V'
def_Kp_value = '0.0500'
def_Ki_value = '0.0001'
def_Kd_value = '0.0000'
def_manual_cmd = 'S_PV_150_A2'
##############################


# other stuff
noPort_msg = "no ports detected :/"
mfc_capacity = '200'