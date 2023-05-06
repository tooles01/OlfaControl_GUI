import sys, os, logging, csv, copy
#import time
from PyQt5 import QtCore, QtSerialPort
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import *
from serial.tools import list_ports
from datetime import datetime, timedelta

import utils, utils_olfa_48line, olfa_driver_48line_vial_popup


baudrate = 9600     # for communicating w/ master
vialsPerSlave = 8
noPort_msg = "no ports detected :/"
master_modes = ["6: verbose",
                "5: trace",
                "4: notice",
                "3: warning",
                "2: error",
                "1: fatal"]
slave_names = ['A','B','C','D','E','F']
cal_table_file_tyoe = '.txt'

##############################
# # DEFAULT VALUES
def_setpoint = '50'
def_open_duration = '5'
default_cal_table = 'Honeywell_3100V'
def_Kp_value = '0.0500'
def_Ki_value = '0.0001'
def_Kd_value = '0.0000'
def_manual_cmd = 'S_PV_150_A2'
##############################

##############################
# CREATE LOGGER
logger = logging.getLogger(name='olfactometer')
logger.setLevel(logging.DEBUG)
if logger.hasHandlers():    logger.handlers.clear()     # removes duplicate log messages
console_handler = utils.create_console_handler()
logger.addHandler(console_handler)
##############################

mfc_capacity = '200'

class Vial(QGroupBox):

    def __init__(self, parent, vialNum):
        super().__init__()
        self.slaveName = parent.name
        self.vialNum = vialNum
        self.full_vialNum = self.slaveName + self.vialNum
        self.olfactometer_parent_object = parent.parent
        
        self.setpoint = def_setpoint
        self.open_duration = def_open_duration
        self.cal_table = default_cal_table
        self.intToSccm_dict = self.olfactometer_parent_object.ard2Sccm_dicts.get(self.cal_table)
        self.sccmToInt_dict = self.olfactometer_parent_object.sccm2Ard_dicts.get(self.cal_table)
        self.Kp_value = def_Kp_value
        self.Ki_value = def_Ki_value
        self.Kd_value = def_Kd_value
        
        self.generate_stuff()
        
        self.vial_details_window.db_valve_open_wid.returnPressed.connect(lambda: self.vial_details_window.db_valve_open_btn.setChecked(True))        
        
        self.setLayout(self.layout)
        self.valve_open_btn.setMaximumWidth(60)
        max_width = self.sizeHint().width()
        #self.setMaximumWidth(max_width - 10)
        self.setMaximumWidth(max_width)
    
    
    # GUI FEATURES
    def generate_stuff(self):
        
        # VALVE OPEN
        self.valve_dur_spinbox = QSpinBox(value=int(def_open_duration))
        self.valve_dur_spinbox.valueChanged.connect(self.valve_open_dur_changed)
        self.valve_dur_lbl = QLabel("dur (s):")
        self.valve_open_btn = QPushButton(text=str("Open " + self.slaveName + self.vialNum),checkable=True)
        self.valve_open_btn.toggled.connect(self.vial_open_toggled)
        self.valve_open_dur_changed()
        self.open_valve_layout = QHBoxLayout()
        self.open_valve_layout.addWidget(self.valve_open_btn)
        self.open_valve_layout.addWidget(self.valve_dur_lbl)
        self.open_valve_layout.addWidget(self.valve_dur_spinbox)
        
        # SETPOINT PIANO
        self.setpoint_slider = QSlider()
        self.setpoint_slider.setMaximum(int(mfc_capacity))
        self.setpoint_slider.setToolTip('Adjusts flow set rate.')
        self.setpoint_slider.setTickPosition(3)

        self.setpoint_set_widget = QLineEdit()
        #setpoint_set_widget.setMaximumWidth(4)
        self.setpoint_set_widget.setAlignment(QtCore.Qt.AlignCenter)
        self.setpoint_set_widget.setToolTip('Set value')
        self.setpoint_set_widget.setStatusTip('Type to set flow rate')  # TODO this don't work

        self.setpoint_read_widget = QLCDNumber()
        self.setpoint_read_widget.setMinimumSize(50,50)
        self.setpoint_read_widget.setDigitCount(5)
        self.setpoint_read_widget.setToolTip('Current flow reading')
        self.setpoint_read_widget.setMaximumHeight(50)
        
        self.setpoint_slider.valueChanged.connect(lambda: self.update_text(value=self.setpoint_slider.value(),spt_set_wid=self.setpoint_set_widget))
        self.setpoint_slider.sliderReleased.connect(lambda: self.slider_released(self.setpoint_slider))
        #self.setpoint_set_widget.editingFinished.connect(self.text_changed) # return pressed OR line edit loses focus
        self.setpoint_set_widget.returnPressed.connect(self.text_changed)

        self.setpoint_slider_layout = QGridLayout()
        self.setpoint_slider_layout.addWidget(self.setpoint_slider,0,0,2,1)
        self.setpoint_slider_layout.addWidget(self.setpoint_set_widget,0,1,1,2)
        self.setpoint_slider_layout.addWidget(self.setpoint_read_widget,1,1,1,2)
        
        # READ FLOW VALUES
        self.read_flow_vals_btn = QPushButton(text="Read flow",checkable=True,toolTip = 'Start reading flow values')
        self.read_flow_vals_btn.toggled.connect(lambda: self.readFlow_btn_toggled(self.read_flow_vals_btn))
        
        # VIAL DETAILS WINDOW
        self.vial_details_window = olfa_driver_48line_vial_popup.VialDetailsPopup(self)
        self.vial_details_btn = QPushButton('Details',checkable=True)
        self.vial_details_btn.toggled.connect(self.vial_details_btn_toggled)
        self.vial_details_btn.setToolTip('Open Vial Details popup')
        
        # VIAL TIMER
        self.valveTimer_lbl = QLabel(self.full_vialNum + ' open:')
        self.valveTimer_duration_label = QLabel('00.000')
        self.valve_timer = QTimer()
        self.valve_timer.setTimerType(0)    # set to millisecond accuracy
        self.valve_timer.timeout.connect(self.show_valve_time)
        self.valveTimer_layout = QHBoxLayout()
        self.valveTimer_layout.addWidget(self.valveTimer_lbl)
        self.valveTimer_layout.addWidget(self.valveTimer_duration_label)
        self.valveTimer_layout.addWidget(QLabel('sec'))

        # LAYOUT
        self.layout = QFormLayout()
        self.layout.addRow(self.valveTimer_layout)
        self.layout.addRow(self.open_valve_layout)
        self.layout.addRow(self.setpoint_slider_layout)
        self.layout.addRow(self.read_flow_vals_btn,self.vial_details_btn)
        # height
        setpoint_set_read_height = 50
        self.setpoint_set_widget.setMaximumHeight(setpoint_set_read_height)
        self.setpoint_read_widget.setMaximumHeight(setpoint_set_read_height)
        self.setpoint_slider.setMaximumHeight(setpoint_set_read_height*2)
        # width
        half_col_width = self.read_flow_vals_btn.sizeHint().width()
        self.setpoint_slider.setFixedWidth(half_col_width)
        self.setpoint_set_widget.setMaximumWidth(half_col_width)
        self.setpoint_read_widget.setMaximumWidth(half_col_width)
        self.read_flow_vals_btn.setFixedWidth(self.read_flow_vals_btn.sizeHint().width())
        self.vial_details_btn.setFixedWidth(self.vial_details_btn.sizeHint().width())    
    
    # SETPOINT SLIDER
    # slider changed --> update setpoint set widget
    def update_text(self,value,spt_set_wid):
        spt_set_wid.setText(str(value))
        self.vial_details_window.setpoint_set_widget.setText(str(value))    # update vial details set widget
        self.vial_details_window.setpoint_slider.setValue(value)            # update vial details slider
    
    # send new setpoint to MFC
    def slider_released(self, setpoint_slider):
        val = setpoint_slider.value()   # get value of slider
        self.set_flowrate(val)          # set the flowrate
    
    def text_changed(self):
        # text of the line edit has changed -> sets the new MFC value
        try:
            value = float(self.setpoint_set_widget.text())
            self.set_flowrate(value)
            self.setpoint_slider.setValue(value)
        except ValueError as err:
            logger.error('error in setting MFC value: ' + err)    
    
    # ACTIONS / BUTTON FUNCTIONS
    def vial_details_btn_toggled(self, checked):
        if checked:
            # Show vial details window
            self.vial_details_window.show()
            self.vial_details_btn.setText('Close Details')
            # disable the other buttons
            self.valve_dur_spinbox.setEnabled(False)
            self.valve_open_btn.setEnabled(False)
            self.read_flow_vals_btn.setEnabled(False)
        else:
            # Close vial details window
            self.vial_details_window.hide()
            self.vial_details_btn.setText('Details')
            # enable the other buttons
            self.valve_dur_spinbox.setEnabled(True)
            self.valve_open_btn.setEnabled(True)
            self.read_flow_vals_btn.setEnabled(True)
    
    def cal_table_updated(self, new_cal_table):
        self.cal_table = new_cal_table
        logger.debug('cal table for %s set to %s', self.full_vialNum, self.cal_table)
        
        self.intToSccm_dict = self.olfactometer_parent_object.ard2Sccm_dicts.get(self.cal_table)
        self.sccmToInt_dict = self.olfactometer_parent_object.sccm2Ard_dicts.get(self.cal_table)
        
        self.set_flowrate(self.setpoint)    # update setpoint
    
    def open_vial(self, duration):
        # send to olfactometer_window (to send to Arduino)
        strToSend = 'S_OV_' + str(duration) + '_' + self.full_vialNum
        self.olfactometer_parent_object.send_to_master(strToSend)
        
        # send to main GUI window (to write to datafile)
        device = 'olfactometer ' + self.full_vialNum
        self.write_to_datafile(device,'OV',str(duration))

        # start valve timer
        self.start_valve_timer(duration)
    
    def close_vial(self):
        # if the button was toggled before the timer finished: send command to Arduino
        if self.valve_timer.isActive():
            logger.debug('vial ' + self.full_vialNum + ' was closed early')
            self.end_valve_timer()
            
            # send to olfactometer_window (to send to Arduino)
            strToSend = 'S_CV_' + self.full_vialNum
            self.olfactometer_parent_object.send_to_master(strToSend)
            
            # send to main GUI window (to write to datafile)
            device = 'olfactometer ' + self.full_vialNum
            self.write_to_datafile(device,'CV','0')
    
    # COMMANDS
    def K_parameter_update(self, Kx, value):
        strToSend = 'S_Kx_' + Kx + str(value) + '_' + self.full_vialNum
        self.olfactometer_parent_object.send_to_master(strToSend)
    
    def set_flowrate(self, value):
        # Convert from sccm to integer
        setpoint_sccm = value
        setpoint_integer = utils_olfa_48line.convertToInt(setpoint_sccm, self.sccmToInt_dict)
        logger.info('set ' + self.full_vialNum + ' to ' + str(setpoint_sccm) + ' sccm')
        
        # Send to olfactometer_window (to send to Arduino)
        strToSend = 'S_Sp_' + str(setpoint_integer) + '_' + self.full_vialNum
        self.olfactometer_parent_object.send_to_master(strToSend)
        
        # Send to main GUI window (to write to datafile)
        device = 'olfactometer ' + self.full_vialNum
        self.write_to_datafile(device,'Sp',setpoint_integer)
    
    def readFlow_btn_toggled(self, btn_to_check):
        if btn_to_check.isChecked():
            btn_to_check.setText("Stop reading ")
            btn_to_check.setToolTip('Stop reading flow values')
            strToSend = 'MS_debug_' + self.full_vialNum
            self.olfactometer_parent_object.send_to_master(strToSend)
        else:
            btn_to_check.setText("Read flow")
            btn_to_check.setToolTip('Start reading flow values')
            strToSend = 'MS_' + self.full_vialNum
            self.olfactometer_parent_object.send_to_master(strToSend)
    
    def vial_open_toggled(self, checked):
        if checked:
            self.valve_open_btn.setText('Close ' + self.full_vialNum)
            self.vial_details_window.db_valve_open_btn.setText('Close vial')
            self.open_vial(self.valve_dur_spinbox.value())
        else:
            self.valve_open_btn.setText('Open ' + self.full_vialNum)
            self.vial_details_window.db_valve_open_btn.setText('Open vial')
            self.close_vial()
    
    def calibrate_flow_sensor_btn_clicked(self):
        logger.error('calibrate flow sensor not set up yet')  # TODO
        '''
        value_to_calibrate = int(self.calibrate_vial_edit.text())
        # set MFC to this value

        # open proportional valve
        open_pv_command = 'S_OC_' + self.full_vialNum
        self.olfactometer_parent_object.send_to_master(open_pv_command)

        # open isolation valve
        open_iv_command = 'S_OV_5_' + self.full_vialNum
        self.olfactometer_parent_object.send_to_master(open_iv_command)

        # read flow values
        # TODO

        # skip

        '''
    
    def write_to_datafile(self,device,unit,value):
        try:
            self.olfactometer_parent_object.window().receive_data_from_device(device,unit,value)
        except AttributeError:
            pass    # main window not open
    
    # VALVE TIMER
    def start_valve_timer(self, duration):
        #logger.debug('starting valve timer')
        self.valve_open_time = datetime.now()
        self.valve_open_duration = timedelta(0,int(duration))
        self.valve_timer.start()
    
    def show_valve_time(self):
        current_time = datetime.now()
        current_valve_dur = current_time - self.valve_open_time
        if current_valve_dur >= self.valve_open_duration:
            self.end_valve_timer()
        valve_dur_display_value = str(current_valve_dur)
        valve_dur_display_value = valve_dur_display_value[5:]   # remove hour/minute display
        valve_dur_display_value = valve_dur_display_value[:-3]  # remove extra decimal point display
        self.valveTimer_duration_label.setText(valve_dur_display_value)
        self.vial_details_window.valveTimer_duration_label.setText(valve_dur_display_value)
    
    def end_valve_timer(self):
        self.valve_timer.stop()
        
        # check which button to untoggle
        if self.vial_details_window.db_valve_open_btn.isChecked():
            self.vial_details_window.db_valve_open_btn.toggle()
        if self.valve_open_btn.isChecked():
            self.valve_open_btn.toggle()
    
    # ~ just for user experience ~
    def valve_open_dur_changed(self):
        self.valve_open_btn.setToolTip("open " + self.full_vialNum + " for " + str(self.valve_dur_spinbox.value()) + " seconds")


class slave_8vials(QGroupBox):

    def __init__(self, parent, name):
        super().__init__()
        self.parent = parent
        self.name = name
        
        self.create_slaveInfo_box()
        self.create_vials_box()
        
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.slaveInfo_layout)
        self.mainLayout.addLayout(self.vials_layout)
        self.setLayout(self.mainLayout)
        self.setTitle(name)
    
    def create_slaveInfo_box(self):
        self.slave_info_box = QGroupBox()

        self.slave_address_label = QLabel(text='Slave address:')    # TODO slave address dictionary :/ where should it be located
        self.temp_label = QLabel("...,...,.slave active or not, slave info, whatever.,...")
        # TODO add a way to apply commands to multiple vials at once
        # ex: check the ones you want to apply this setpoint to
        
        self.slaveInfo_layout = QVBoxLayout()
        #self.slaveInfo_layout.addWidget(self.slave_address_label)
        self.slaveInfo_layout.addWidget(self.temp_label)
    
    def create_vials_box(self):
        self.vials = []
        for v in range(vialsPerSlave):
            v_vialNum = str(v+1)
            v_vial = Vial(parent=self, vialNum=v_vialNum)
            self.vials.append(v_vial)

        self.vials_layout = QHBoxLayout()
        for v in range(vialsPerSlave):
            self.vials_layout.addWidget(self.vials[v])

        # FOR TODAY (2/22/2023) since mixing chamber pinout is bad
        self.vials[0].setEnabled(False) # Vial 1: not connected to anything on the mixing chamber
        #self.vials[2].setEnabled(False) # Vial 3: connected to Vial 8
        self.vials[3].setEnabled(False) # Vial 4: isolation valve not working


class olfactometer_window(QGroupBox):
    
    def __init__(self):
        super().__init__()
        self.sccm2Ard_dicts = {}
        self.ard2Sccm_dicts = {}
        self.active_slaves = []
        self.calibration_on = False

        self.get_calibration_tables()
        self.generate_ui()
        
        self.master_groupbox.setEnabled(False)
        self.setTitle('Olfactometer')

        # JUST FOR TODAY (7/26/2022)
        self.slave_objects[0].setEnabled(True)
    
    
    def get_calibration_tables(self):
        self.flow_cal_dir = utils.find_olfaControl_directory() + '\\calibration_tables' # NOTE: this takes a super long time
        
        if os.path.exists(self.flow_cal_dir):
            logger.debug('loading flow sensor calibration tables (%s)', self.flow_cal_dir)
            
            # Get names of all .txt files in flow cal directory
            cal_file_names = os.listdir(self.flow_cal_dir)
            cal_file_names = [fn for fn in cal_file_names if fn.endswith(cal_table_file_tyoe)]    # only txt files # TODO: change to csv
            
            if cal_file_names != []:
                
                # Create dictionaries for holding the calibration tables
                new_sccm2Ard_dicts = {}
                new_ard2Sccm_dicts = {}
                
                # Parse each file
                for cal_file in cal_file_names:
                    idx_ext = cal_file.find('.')    # NOTE: pos fix: this won't work if the file name has a period in it.. but cmon who's gonna have a stupid file name like that
                    file_name = cal_file[:idx_ext]
                    cal_file_full_dir = self.flow_cal_dir + '\\' + cal_file
                    
                    thisfile_sccm2Ard_dict = {}
                    thisfile_ard2Sccm_dict = {}
                    with open(cal_file_full_dir, newline='') as f:
                        csv_reader = csv.reader(f)
                        firstLine = next(csv_reader)    # skip over header line
                        
                        # get the shit
                        reader = csv.DictReader(f, delimiter=',')
                        for row in reader:
                            try:
                                thisfile_sccm2Ard_dict[float(row['SCCM'])] = float(row['int'])
                                thisfile_ard2Sccm_dict[float(row['int'])] = float(row['SCCM'])
                            except KeyError as err:
                                # clear dictionaries, stop trying to read this file
                                logger.warning('error: %s',err)
                                logger.warning('%s does not have correct headings for calibration files', cal_file)
                                thisfile_sccm2Ard_dict = {}
                                thisfile_ard2Sccm_dict = {}
                                break
                            except ValueError as err:
                                # clear dictionaries, stop trying to read this file
                                logger.warning('missing some values, skipping calibration file %s', cal_file)
                                thisfile_sccm2Ard_dict = {}
                                thisfile_ard2Sccm_dict = {}
                                break
                    
                    # If this file was good (aka we got values), save it to the dict of dicts
                    if bool(thisfile_sccm2Ard_dict) == True:
                        new_sccm2Ard_dicts[file_name] = thisfile_sccm2Ard_dict
                        new_ard2Sccm_dicts[file_name] = thisfile_ard2Sccm_dict
                
                # If we got stuff from these files, replace the old dicts
                if len(new_sccm2Ard_dicts) != 0:
                    self.sccm2Ard_dicts = new_sccm2Ard_dicts
                    self.ard2Sccm_dicts = new_ard2Sccm_dicts
                else:
                    logger.info('no calibration files found in this directory')
            
            else:
                logger.warning('no cal files found :/')
        
        # If flow cal directory does not exist: print warning   # NOTE this is big issue if none found
        else:
            logger.error('Cannot find flow cal directory (searched in %s)', self.flow_cal_dir)
    
    def generate_ui(self):
        self.create_connect_box()
        self.create_master_groupbox()
        self.create_raw_comm_groupbox()
        self.create_slave_groupbox()
        
        col1_max_width = self.master_groupbox.sizeHint().width()
        self.connect_box.setFixedWidth(col1_max_width)
        self.master_groupbox.setFixedWidth(col1_max_width)
        
        self.connect_box.setMaximumHeight(self.connect_box.sizeHint().height())
        self.master_groupbox.setMaximumHeight(114)
        self.raw_comm_box.setMaximumHeight(202)
        
        mainLayout = QGridLayout()
        self.setLayout(mainLayout)
        mainLayout.addWidget(self.connect_box,0,0,1,1)
        mainLayout.addWidget(self.master_groupbox,1,0,1,1)
        mainLayout.addWidget(self.raw_comm_box,0,1,2,1)
        mainLayout.addWidget(self.slave_groupbox,2,0,1,2)
        
    def create_connect_box(self):
        self.connect_box = QGroupBox("Connect to master Arduino")
        self.port_widget = QComboBox(currentIndexChanged=self.port_changed)
        self.connect_btn = QPushButton(checkable=True,toggled=self.toggled_connect)
        self.refresh_btn = QPushButton(text="Refresh",clicked=self.get_ports,toolTip='refresh list of available com ports')
        self.get_ports()
        connect_box_layout = QHBoxLayout()
        connect_box_layout.addWidget(QLabel(text='Select Port:',toolTip='Select COM port for master Arduino'))
        connect_box_layout.addWidget(self.port_widget)
        connect_box_layout.addWidget(self.connect_btn)
        connect_box_layout.addWidget(self.refresh_btn)
        #connect_box_layout = QFormLayout()
        #connect_box_layout.addRow(QLabel(text="Select Port:"),self.port_widget)
        #connect_box_layout.addRow(self.refresh_btn,self.connect_btn)
        self.connect_box.setLayout(connect_box_layout)

    def create_master_groupbox(self):
        self.master_groupbox = QGroupBox('Master Settings')

        self.m_check_addr_btn = QPushButton(text="Get Slave Addresses",clicked=lambda: self.get_slave_addresses())

        self.m_mode_dropdown = QComboBox()
        self.m_mode_dropdown.addItems(master_modes)
        self.m_mode_btn = QPushButton(text="Send", clicked=lambda: self.send_master_mode(self.m_mode_dropdown.currentText()))
        m_mode_layout = QHBoxLayout()
        m_mode_layout.addWidget(self.m_check_addr_btn)
        m_mode_layout.addWidget(QLabel(text='Change master logging mode:'))
        m_mode_layout.addWidget(self.m_mode_dropdown)
        m_mode_layout.addWidget(self.m_mode_btn)

        self.m_timebtreqs = QLineEdit(text='100',#self.defTimebt,
            returnPressed=lambda:self.send_to_master('MM_timebt_' + self.m_timebtreqs.text()))
        self.m_timebtreqs_btn = QPushButton(text="Send", clicked=lambda:self.send_to_master('MM_timebt_' + self.m_timebtreqs.text()))
        timebt_layout = QHBoxLayout()
        timebt_layout.addWidget(QLabel(text="Time b/t requests to slave (ms):"))
        timebt_layout.addWidget(self.m_timebtreqs)
        timebt_layout.addWidget(self.m_timebtreqs_btn)

        self.m_manualcmd = QLineEdit(text=def_manual_cmd,
            returnPressed=lambda: self.send_to_master(self.m_manualcmd.text()))
        self.m_manualcmd_btn = QPushButton(text="Send",
            clicked=lambda: self.send_to_master(self.m_manualcmd.text()))
        manualcmd_layout = QHBoxLayout()
        manualcmd_layout.addWidget(QLabel(text="Send manual command:"))
        manualcmd_layout.addWidget(self.m_manualcmd)
        manualcmd_layout.addWidget(self.m_manualcmd_btn)
        

        layout = QVBoxLayout()
        layout.addLayout(m_mode_layout)
        layout.addLayout(timebt_layout)
        layout.addLayout(manualcmd_layout)
        self.master_groupbox.setLayout(layout)
        
    def create_raw_comm_groupbox(self):
        self.raw_comm_box = QGroupBox("Raw Communication Data")

        self.raw_write_display = QTextEdit(readOnly=True)
        raw_write_layout = QVBoxLayout()
        raw_write_layout.addWidget(QLabel('written to serial port:'))
        raw_write_layout.addWidget(self.raw_write_display)

        self.raw_read_display = QTextEdit(readOnly=True)
        raw_read_layout = QVBoxLayout()
        raw_read_layout.addWidget(QLabel('received from serial port:'))
        raw_read_layout.addWidget(self.raw_read_display)

        raw_comm_layout = QHBoxLayout()
        raw_comm_layout.addLayout(raw_read_layout)
        raw_comm_layout.addLayout(raw_write_layout)
        self.raw_comm_box.setLayout(raw_comm_layout)

        self.raw_write_display.setMinimumWidth(230)
        self.raw_read_display.setMinimumWidth(230)
        
    def create_slave_groupbox(self):
        self.slave_groupbox = QGroupBox('Slaves')
        
        # Create slave object for each item listed in slave_names
        self.slave_objects = []
        for s in slave_names:
            new_slave_object = slave_8vials(parent=self,name=s)
            self.slave_objects.append(new_slave_object)
        
        # Add slave objects to layout
        self.slave_layout = QVBoxLayout()
        for s in self.slave_objects:
            self.slave_layout.addWidget(s)
            s.setEnabled(False)
        
        self.slave_widget = QWidget()                           # widget to put into QScrollArea
        self.slave_widget.setLayout(self.slave_layout)
        self.slave_scrollArea = QScrollArea()
        self.slave_scrollArea.setWidget(self.slave_widget)
        self.nothing_layout = QHBoxLayout()                     # layout for putting QScrollArea into self.slave_groupbox
        self.nothing_layout.addWidget(self.slave_scrollArea)
        
        self.slave_groupbox.setLayout(self.nothing_layout)
        #self.slave_groupbox.setMinimumWidth(self.slave_scrollArea.sizeHint().width())
        self.slave_groupbox.setMinimumWidth(self.slave_widget.sizeHint().width() + 40)


    # CONNECT FUNCTIONS
    def get_ports(self):
        self.port_widget.clear()
        ports = list_ports.comports()
        if ports:
            for ser in ports:
                port_device = ser[0]
                port_description = ser[1]
                if port_device in port_description:
                    idx1 = port_description.find(port_device)
                    port_description = port_description[:idx1-2]
                ser_str = ('{}: {}').format(port_device,port_description)
                self.port_widget.addItem(ser_str)
        else:
            self.port_widget.addItem(noPort_msg)
        # # TODO ooooh what if this could be a lil list of items
        
        # if an Arduino is connected, set the widget default value to that
        for port_list_idx in range(0,self.port_widget.count()):
            this_port = self.port_widget.itemText(port_list_idx)
            if 'Arduino' in this_port:
                self.port_widget.setCurrentIndex(port_list_idx)
                break
    
    def port_changed(self):
        if self.port_widget.count() != 0:
            self.port = self.port_widget.currentText()
            if self.port == noPort_msg:
                self.connect_btn.setEnabled(False)
                self.connect_btn.setText(noPort_msg)
            else:
                self.portStr = self.port[:self.port.index(':')]
                self.connect_btn.setEnabled(True)
                #self.connect_btn.setText("Connect to " + self.portStr)
                self.connect_btn.setText("Connect")
                self.connect_btn.setToolTip("Connect to " + self.portStr)
    
    def toggled_connect(self, checked):
        if checked:
            i = self.port.index(':')
            self.comPort = self.port[:i]
            self.serial = QtSerialPort.QSerialPort(self.comPort,baudRate=baudrate,readyRead=self.receive)
            if not self.serial.isOpen():
                if self.serial.open(QtCore.QIODevice.ReadWrite):
                    self.set_connected(True)
                else:
                    self.set_connected(False)
            else:
                self.set_connected(True)
        else:
            try:
                self.set_connected(False)
                self.serial.close()
            except AttributeError as err:
                logger.error("error :( --> %s", err)
    
    def set_connected(self, connected):
        if connected == True:
            logger.info('connected to ' + self.port_widget.currentText())
            self.get_slave_addresses()
            self.master_groupbox.setEnabled(True)
            self.connect_btn.setText("Disconnect")
            self.connect_btn.setToolTip("Disconnect from " + self.portStr)
            #self.connect_btn.setText('Disconnect from ' + self.portStr)
            self.refresh_btn.setEnabled(False)
            self.port_widget.setEnabled(False)
        
        else:
            logger.info('disconnected from ' + self.port_widget.currentText())
            self.master_groupbox.setEnabled(False)
            self.connect_btn.setText("Connect")
            #self.connect_btn.setText('Connect to ' + self.portStr)
            self.connect_btn.setChecked(False)
            self.refresh_btn.setEnabled(True)
            self.port_widget.setEnabled(True)
            '''
            # this seems unnecessary - ST 1/30/2023
            # set vials of all currently active slaves to not debug --> do this in a thread
            for slave in self.active_slaves:
                for vial in range(0,vialsPerSlave):
                    strToSend = 'MS_' + slave + str(vial+1)
                    self.send_to_master(strToSend)
                    time.sleep(.3)
            '''  
    
    def get_slave_addresses(self):
        self.prev_active_slaves = copy.copy(self.active_slaves)
        self.active_slaves = []
        logger.info('Checking slave addresses')
        self.send_to_master('C')        
        '''
        # once received, remove inactive slaves
        for s_name in slave_names:
            # if name is not in active slaves list: remove its groupbox
            if s_name in self.active_slaves:
                # you can keep it
                x=2
            else:
                # get rid of it
                x=2
        '''
    
    def send_master_mode(self, newMode):
        if newMode == master_modes[0]:  mode_value = 6
        if newMode == master_modes[1]:  mode_value = 5
        if newMode == master_modes[2]:  mode_value = 4
        if newMode == master_modes[3]:  mode_value = 3
        if newMode == master_modes[4]:  mode_value = 2
        if newMode == master_modes[5]:  mode_value = 1
        
        m_mode_string = 'MM_mode_' + str(mode_value)
        self.send_to_master(m_mode_string)

    def receive(self):
        if self.serial.canReadLine() == True:
            text = self.serial.readLine(1024)
            try:
                text = text.decode("utf-8")
                text = text.rstrip('\r\n')
                self.raw_read_display.append(text)

                # IF NAME/ADDRESS WERE SENT: enable this slave
                strToFind = 'name: '
                if strToFind in text:
                    text=text[3:]       # remove logging info
                    
                    # find name
                    strToFind = 'name: '
                    beginning_idx = text.find(strToFind)
                    charsToRemove = len(strToFind)
                    c = text[charsToRemove:]
                    slash_idx = c.find('\t')
                    slave_name_received = c[:slash_idx]
                    self.active_slaves.append(slave_name_received)

                    # find address
                    strToFind = 'address: '
                    beginning_idx = text.find(strToFind)
                    charsToRemove = len(strToFind) + beginning_idx
                    slave_address = text[charsToRemove:]
                    
                    '''
                    for s in self.slave_objects:
                        if s.name == slave_name_received:
                            self.slave_layout.addWidget(s)
                            self.slave_scrollArea.setWidget(self.slave_widget)
                            self.nothing_layout.addWidget(self.slave_scrollArea)
                            self.slave_groupbox.setLayout(self.nothing_layout)
                    '''
                    # enable groupbox for this slave & add the address
                    for s in self.slave_objects:
                        if s.name == slave_name_received:
                            s.setEnabled(True)
                            address_label = 'Slave Address: {}'.format(slave_address)
                            s.slave_address_label.setText(address_label)
                    
                    # if program selected reads "no active slaves" --> update the combobox
                    try:
                        if self.window().p_slave_select_wid.currentText() == 'no active slaves pls connect olfa or something':
                            self.window().active_slave_refresh()
                    except AttributeError:  # if no main window
                        pass

                        
                # IF FLOW UPDATE WAS SENT: send to main GUI window (to write to datafile)
                if len(text) == 17:
                    text = text[3:]     # remove arduino logging info
                    
                    # split up for writing to datafile
                    slave_vial = text[0:2]  # 'A1'
                    flowVal = text[2:6]     # '0148'
                    ctrlVal = text[6:10]    # '0255'

                    # send flow value to main GUI
                    device = 'olfactometer ' + slave_vial
                    unit = 'FL'
                    value = flowVal
                    try:
                        self.window().receive_data_from_device(device,unit,value)
                    except AttributeError as err:   # if main window is not open
                        pass

                    # send ctrl value to main GUI
                    unit = 'Ctrl'
                    value = ctrlVal
                    try:
                        self.window().receive_data_from_device(device,unit,value)
                    except AttributeError as err:   # if main window is not open
                        pass

                    
                    # write it to the vial details box
                    for s in self.slave_objects:    # find out which vial this is
                        for v in s.vials:
                            if v.full_vialNum == slave_vial:
                                # convert to sccm
                                flowVal_raw = int(flowVal)
                                flowVal_sccm = utils_olfa_48line.convertToSCCM(flowVal_raw,v.intToSccm_dict)
                                
                                # write it to the vial details box
                                dataStr = str(flowVal) + '\t' + str(flowVal_sccm) + '\t' + str(ctrlVal)
                                v.vial_details_window.data_receive_box.append(dataStr)
                                
                                # write it to the setpoint read widget
                                v.setpoint_read_widget.display(round(flowVal_sccm))
                                
                                # write it to the setpoint read widget in the details box
                                v.vial_details_window.setpoint_read_widget.display(round(flowVal_sccm))
                                
                                # if calibration is on: send it to the vial details popup
                                if self.calibration_on == True:
                                    v.vial_details_window.read_value(flowVal)
            
            except UnicodeDecodeError:
                logger.warning("Serial read error")

    def send_to_master(self, strToSend):
        bArr_send = strToSend.encode()
        try:
            if self.serial.isOpen():
                self.serial.write(bArr_send)                # send to Arduino
                self.raw_write_display.append(strToSend)    # display string that was sent
            else:
                logger.warning('Serial port not open, cannot send parameter: %s', strToSend)
        except AttributeError as err:
            logger.warning('(Attribute Error) Serial port not open, cannot send parameter: %s', strToSend)


if __name__ == "__main__":
    logger.debug('opening window')
    app1 = QApplication(sys.argv)
    theWindow = olfactometer_window()
    theWindow.show()
    theWindow.setWindowTitle('48-line olfactometer')
    sys.exit(app1.exec_())