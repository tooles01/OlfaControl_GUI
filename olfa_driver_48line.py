import sys, logging, time
import os, csv, copy
from turtle import width
from PyQt5 import QtCore, QtSerialPort
from PyQt5.QtWidgets import *
from serial.tools import list_ports

import utils, utils_olfa_48line

baudrate = 9600     # for communicating w/ master
vialsPerSlave = 8
noPort_msg = "no ports detected :/"
master_modes = ["6: verbose",
                "5: trace",
                "4: notice",
                "3: warning",
                "2: error",
                "1: fatal"]
slave_names = ['A',
                'B',
                'C',
                'D',
                'E',
                'F']

# DEFAULT VALUES
default_setpoint = '50'
default_cal_table = 'Honeywell_3100V'
def_Kp_value = '0.0500'
def_Ki_value = '0.0001'
def_Kd_value = '0.0000'


# CREATE LOGGER
logger = logging.getLogger(name='olfactometer')
logger.setLevel(logging.DEBUG)
if logger.hasHandlers():    logger.handlers.clear()     # removes duplicate log messages
console_handler = utils.create_console_handler()
logger.addHandler(console_handler)


class Vial(QGroupBox):

    def __init__(self, parent, vialNum):
        super().__init__()
        self.parent = parent
        self.slaveName = parent.name
        self.vialNum = vialNum
        self.full_vialNum = self.slaveName + self.vialNum
        self.olfactometer_parent_object = self.parent.parent
        
        self.cal_table = default_cal_table
        self.Kp_value = def_Kp_value
        self.Ki_value = def_Ki_value
        self.Kd_value = def_Kd_value

        self.generate_stuff()

        self.setLayout(self.layout)
        self.valve_open_btn.setMaximumWidth(60)
        self.setpoint_send_btn.setMaximumWidth(60)
        max_width = self.sizeHint().width()
        self.setMaximumWidth(max_width - 15)
        
    
    def generate_stuff(self):
        # VALVE OPEN DURATION
        self.valve_duration_spinbox = QSpinBox(value=5)
        self.valve_open_btn = QPushButton(text=str("Open " + self.slaveName + self.vialNum),
            #checkable=True,
            toolTip="open vial")
        self.valve_open_btn.clicked.connect(lambda: self.vial_button_clicked())
        self.open_valve_layout = QHBoxLayout()
        self.open_valve_layout.addWidget(QLabel("dur(s):"))
        self.open_valve_layout.addWidget(self.valve_duration_spinbox)
        self.open_valve_layout.addWidget(self.valve_open_btn)
        
        # SETPOINT
        self.setpoint_value_box = QSpinBox(maximum=200,value=int(default_setpoint))
        self.setpoint_send_btn = QPushButton(text="Update\nSpt")
        self.setpoint_send_btn.clicked.connect(lambda: self.setpoint_btn_clicked(self.setpoint_value_box.value()))
        self.setpoint_layout = QHBoxLayout()
        self.setpoint_layout.addWidget(QLabel("sccm:"))
        self.setpoint_layout.addWidget(self.setpoint_value_box)
        self.setpoint_layout.addWidget(self.setpoint_send_btn)
        
        # CALIBRATION TABLE
        self.cal_table_combobox = QComboBox()
        self.cal_table_combobox.addItems(self.olfactometer_parent_object.sccm2Ard_dicts)
        self.cal_table_combobox.setCurrentText(self.cal_table)  # TODO: change this to cycle through and find that cal table, set the index to that
        self.cal_table_combobox.currentIndexChanged.connect(lambda: self.cal_table_updated(self.cal_table_combobox.currentText()))
        self.cal_table_layout = QVBoxLayout()
        self.cal_table_layout.addWidget(QLabel(text='Calibration Table:'))
        self.cal_table_layout.addWidget(self.cal_table_combobox)
        self.cal_table_updated(self.cal_table_combobox.currentText())
        
        # READ FLOW VALUES
        self.read_flow_vals_btn = QPushButton(text="read flow vals", checkable=True, toggled=self.readFlow_btn_toggled)
        
        # VIAL DETAILS
        self.create_vial_details_window()
        self.vial_details_btn = QPushButton('Vial Details',checkable=True,toggled=self.vial_details_btn_toggled)
        
        '''
        self.calibrate_vial_edit = QLineEdit(text='100')
        self.calibrate_vial_btn = QPushButton(text="calibrate")
        self.calibrate_vial_btn.clicked.connect(self.calibrate_flow_sensor)
        self.calibration_layout = QHBoxLayout()
        self.calibration_layout.addWidget(self.calibrate_vial_edit)
        self.calibration_layout.addWidget(self.calibrate_vial_btn)
        '''
        # - current flow value (?)
        
        # LAYOUT
        self.layout = QFormLayout()
        self.layout.addRow(self.open_valve_layout)
        self.layout.addRow(self.setpoint_layout)
        self.layout.addRow(self.cal_table_layout)
        self.layout.addRow(self.read_flow_vals_btn)
        self.layout.addRow(self.vial_details_btn)
    
    def create_vial_details_window(self):
        self.vial_details_window = QWidget()
        self.vial_details_window.setWindowTitle('Vial ' + self.full_vialNum + ' - Debug')
        
        self.vial_details_create_std_widgets_box()
        self.db_advanced_btn = QPushButton(text='Enable Advanced Options',checkable=True,toggled=self.toggled_advanced_settings)    #self.db_advanced_btn.toggled.connect(self.toggled_advanced_settings)        
        self.vial_details_create_flow_ctrl_box()
        self.vial_details_create_man_control_box()
        
        # Values Received
        self.data_receive_lbl = QLabel(("Flow val (int), Flow (SCCM), Ctrl val (int)"))
        self.data_receive_box = QTextEdit(readOnly=True)
        
        # Layout
        layout_col1_widgets = QGridLayout()
        layout_col1_widgets.addWidget(self.db_std_widgets_box,0,0,1,2)
        layout_col1_widgets.addWidget(self.db_advanced_btn,1,0,1,2)
        layout_col1_widgets.addWidget(self.db_flow_control_box,2,0,1,1)
        layout_col1_widgets.addWidget(self.db_manual_control_box,2,1,1,1)
        layout_col2_data = QVBoxLayout()
        layout_col2_data.addWidget(self.data_receive_lbl)
        layout_col2_data.addWidget(self.data_receive_box)

        self.vial_debug_window_layout = QHBoxLayout()
        self.vial_debug_window_layout.addLayout(layout_col1_widgets)
        self.vial_debug_window_layout.addLayout(layout_col2_data)
        self.vial_details_window.setLayout(self.vial_debug_window_layout)
        
        self.vial_details_window.hide()
    
    def vial_details_create_std_widgets_box(self):
        self.db_std_widgets_box = QGroupBox()

        # Open Vial
        self.db_open_valve_wid = QLineEdit(text='5',returnPressed=lambda: self.vial_button_clicked)        # pos change to spinbox so min/max can be set
        self.db_open_valve_btn = QPushButton('Open vial')
        self.db_open_valve_btn.clicked.connect(self.vial_button_clicked)
        
        # Setpoint
        self.db_setpoint_value_box = QLineEdit(text=default_setpoint,returnPressed=lambda: self.setpoint_btn_clicked(self.db_setpoint_value_box.text()))
        self.db_setpoint_send_btn = QPushButton('Update Spt')
        self.db_setpoint_send_btn.clicked.connect(lambda: self.setpoint_btn_clicked(self.db_setpoint_value_box.text()))
        
        # Flow Calibration Table
        self.db_cal_table_combobox = QComboBox()
        self.db_cal_table_combobox.addItems(self.olfactometer_parent_object.ard2Sccm_dicts)
        self.db_cal_table_combobox.setCurrentText(self.cal_table)
        self.db_cal_table_combobox.currentIndexChanged.connect(lambda: self.cal_table_updated(self.db_cal_table_combobox.currentText()))
        self.db_calibrate_sensor_btn = QPushButton(text='Calibrate')
        self.db_calibrate_sensor_btn.clicked.connect(self.calibrate_flow_sensor_btn_clicked)

        # set second widgets to the same width
        width_to_use = self.db_cal_table_combobox.sizeHint().width()
        self.db_open_valve_wid.setMinimumWidth(width_to_use)
        self.db_setpoint_value_box.setMinimumWidth(width_to_use)
        self.db_cal_table_combobox.setMinimumWidth(width_to_use)
        self.db_open_valve_wid.setFixedWidth(width_to_use)
        self.db_setpoint_value_box.setFixedWidth(width_to_use)
        self.db_cal_table_combobox.setFixedWidth(width_to_use)
        
        # Layout
        layout_labels = QVBoxLayout()
        layout_labels.addWidget(QLabel('Duration to open (s):'))
        layout_labels.addWidget(QLabel('Setpoint (sccm):'))
        layout_labels.addWidget(QLabel('Calibration table:'))
        layout_widgets = QFormLayout()
        layout_widgets.addRow(self.db_open_valve_wid,self.db_open_valve_btn)
        layout_widgets.addRow(self.db_setpoint_value_box,self.db_setpoint_send_btn)
        layout_widgets.addRow(self.db_cal_table_combobox,self.db_calibrate_sensor_btn)

        layout_full = QHBoxLayout()
        layout_full.addLayout(layout_labels)
        layout_full.addLayout(layout_widgets)
        self.db_std_widgets_box.setLayout(layout_full)
        self.db_std_widgets_box.setFixedHeight(layout_widgets.sizeHint().height() + 24)
        
    def vial_details_create_flow_ctrl_box(self):
        self.db_flow_control_box = QGroupBox('Flow control parameters')

        self.db_Kp_wid = QLineEdit(text=str(self.Kp_value))
        self.db_Ki_wid = QLineEdit(text=str(self.Ki_value))
        self.db_Kd_wid = QLineEdit(text=str(self.Kd_value))
        self.db_Kp_send = QPushButton(text='Send')
        self.db_Ki_send = QPushButton(text='Send')
        self.db_Kd_send = QPushButton(text='Send')
        self.db_Kp_send.clicked.connect(lambda: self.K_parameter_update('P',self.db_Kp_wid.text()))
        self.db_Ki_send.clicked.connect(lambda: self.K_parameter_update('I',self.db_Ki_wid.text()))
        self.db_Kd_send.clicked.connect(lambda: self.K_parameter_update('D',self.db_Kd_wid.text()))

        self.db_Kp_wid.setMaximumWidth(100)
        self.db_Ki_wid.setMaximumWidth(100)
        self.db_Kd_wid.setMaximumWidth(100)
        self.db_Kp_send.setMaximumWidth(80)
        self.db_Ki_send.setMaximumWidth(80)
        self.db_Kd_send.setMaximumWidth(80)
        
        flow_control_lbls = QVBoxLayout()
        flow_control_lbls.addWidget(QLabel('Kp:'))
        flow_control_lbls.addWidget(QLabel('Ki:'))
        flow_control_lbls.addWidget(QLabel('Kd:'))
        flow_control_wids = QFormLayout()
        flow_control_wids.addRow(self.db_Kp_wid,self.db_Kp_send)
        flow_control_wids.addRow(self.db_Ki_wid,self.db_Ki_send)
        flow_control_wids.addRow(self.db_Kd_wid,self.db_Kd_send)
        
        flow_control_layout = QHBoxLayout()
        flow_control_layout.addLayout(flow_control_lbls)
        flow_control_layout.addLayout(flow_control_wids)
        self.db_flow_control_box.setLayout(flow_control_layout)
        self.db_flow_control_box.setMinimumWidth(self.db_flow_control_box.sizeHint().width())
        self.db_flow_control_box.setFixedHeight(flow_control_wids.sizeHint().height() + 24)
        
        self.db_flow_control_box.setEnabled(False)     # disable until advanced options toggled

    def vial_details_create_man_control_box(self):
        self.db_manual_control_box = QGroupBox('Manual Controls')
        self.db_PID_toggle_btn = QPushButton(text="Turn flow control on",checkable=True,toggled=self.toggled_PID)
        self.db_ctrl_toggle_btn = QPushButton(text="Open prop valve",checkable=True,toggled=self.toggled_ctrlOpen)
        self.db_vlve_toggle_btn = QPushButton(text="Open Iso Valve",checkable=True,toggled=self.toggled_valveOpen)
        manual_debug_layout = QVBoxLayout()
        manual_debug_layout.addWidget(self.db_PID_toggle_btn)
        manual_debug_layout.addWidget(self.db_ctrl_toggle_btn)
        manual_debug_layout.addWidget(self.db_vlve_toggle_btn)
        self.db_manual_control_box.setLayout(manual_debug_layout)
        
        self.db_manual_control_box.setEnabled(False)     # disable until advanced options toggled
    
    def vial_details_btn_toggled(self, checked):
        if checked:
            # show vial details window
            self.vial_details_window.show()
            # disable the other buttons
            self.valve_duration_spinbox.setEnabled(False)
            self.valve_open_btn.setEnabled(False)
            self.setpoint_value_box.setEnabled(False)
            self.setpoint_send_btn.setEnabled(False)
            self.cal_table_combobox.setEnabled(False)
            self.read_flow_vals_btn.setEnabled(False)
        else:
            # hide vial details window
            self.vial_details_window.hide()
            # enable the other buttons
            self.valve_duration_spinbox.setEnabled(True)
            self.valve_open_btn.setEnabled(True)
            self.setpoint_value_box.setEnabled(True)
            self.setpoint_send_btn.setEnabled(True)
            self.cal_table_combobox.setEnabled(True)
            self.read_flow_vals_btn.setEnabled(True)
    
    
    # ACTIONS
    def K_parameter_update(self, Kx, value):
        strToSend = 'S_Kx_' + Kx + str(value) + '_' + self.full_vialNum
        self.olfactometer_parent_object.send_to_master(strToSend)
    
    def setpoint_btn_clicked(self, value):
        # - convert from sccm to integer
        setpoint_sccm = value
        setpoint_integer = utils_olfa_48line.convertToInt(setpoint_sccm, self.sccmToInt_dict)
        
        # send to olfactometer_window (to send to Arduino)
        strToSend = 'S_Sp_' + str(setpoint_integer) + '_' + self.slaveName + self.vialNum
        self.olfactometer_parent_object.send_to_master(strToSend)    
        
        # send to main GUI window (to write to datafile)
        device = 'olfactometer ' + self.full_vialNum
        self.write_to_datafile(device,'Sp',setpoint_integer)
        
    def vial_button_clicked(self):
        # TODO: sync this with the other vial button toggled function
        
        # send to olfactometer_window (to send to Arduino)
        strToSend = 'S_OV_' + str(self.valve_duration_spinbox.value()) + '_' + self.parent.name + self.vialNum
        self.olfactometer_parent_object.send_to_master(strToSend)   # TODO toggle it until the duration has passed
        logger.debug('Opening %s for %s seconds',self.parent.name + self.vialNum, self.valve_duration_spinbox.value())
        
        # send to main GUI window (to write to datafile)
        device = 'olfactometer ' + self.full_vialNum
        value = str(self.valve_duration_spinbox.value())
        self.write_to_datafile(device,'OV',value)
    
    
    def readFlow_btn_toggled(self, checked):
        if checked:
            self.read_flow_vals_btn.setText("stop getting flow vals")
            strToSend = 'MS_debug_' + self.parent.name + self.vialNum
            self.olfactometer_parent_object.send_to_master(strToSend)
        else:
            self.read_flow_vals_btn.setText("read flow vals")
            strToSend = 'MS_' + self.parent.name + self.vialNum
            self.olfactometer_parent_object.send_to_master(strToSend)
        
    def toggled_PID(self):
        # TODO
        logger.info('PID toggled (not set up)')
        
    def toggled_ctrlOpen(self):
        # TODO
        logger.info('prop valve open toggled (not set up)')
    
    def toggled_valveOpen(self):
        # TODO
        logger.info('isolation valve open toggled (not set up)')
        
    def calibrate_flow_sensor_btn_clicked(self):
        # TODO
        logger.warning('calibrate flow sensor not set up yet')
    
    def toggled_advanced_settings(self, checked):
        if checked:
            self.db_flow_control_box.setEnabled(True)
            self.db_manual_control_box.setEnabled(True)
            self.db_advanced_btn.setText('Disable Advanced Options')
        else:
            self.db_flow_control_box.setEnabled(False)
            self.db_manual_control_box.setEnabled(False)
            self.db_advanced_btn.setText('Enable Advanced Options')
    
    '''
    def calibrate_flow_sensor(self):
        value_to_calibrate = int(self.calibrate_vial_edit.text())
        # set MFC to this value

        # open proportional valve
        open_pv_command = 'S_OC_' + self.parent.name + self.vialNum
        self.olfactometer_parent_object.send_to_master(open_pv_command)

        # open isolation valve
        open_iv_command = 'S_OV_5_' + self.parent.name + self.vialNum
        self.olfactometer_parent_object.send_to_master(open_iv_command)

        # read flow values
        # TODO

    '''
    
    def cal_table_updated(self, new_cal_table): # TODO
        self.cal_table = self.cal_table_combobox.currentText()

        self.intToSccm_dict = self.olfactometer_parent_object.ard2Sccm_dicts.get(self.cal_table)
        self.sccmToInt_dict = self.olfactometer_parent_object.sccm2Ard_dicts.get(self.cal_table)
    
    def write_to_datafile(self,device,unit,value):
        try:
            self.olfactometer_parent_object.window().receive_data_from_device(device,unit,value)
        except AttributeError:
            pass    # main window not open


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

        self.slave_address_label = QLabel(text='Slave address:')
        self.temp_label = QLabel("slave active, whatever")
        # add a way to apply commands to multiple vials at once # TODO
        # ex: check the ones you want to apply this setpoint to

        self.slaveInfo_layout = QVBoxLayout()
        self.slaveInfo_layout.addWidget(self.slave_address_label)
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


class olfactometer_window(QGroupBox):
    
    def __init__(self):
        super().__init__()
        self.sccm2Ard_dicts = {}
        self.ard2Sccm_dicts = {}
        self.active_slaves = []

        self.get_calibration_tables()
        self.generate_ui()
        
        self.master_groupbox.setEnabled(False)
        # TODO: upon first connect: set all vials to not debug
        self.setTitle('Olfactometer')

        # JUST FOR TODAY (7/26/2022)
        self.slave_objects[0].setEnabled(True)
    
    def get_calibration_tables(self):
        '''
        #self.flow_cal_dir = 'C:\\Users\\SB13FLLT004\\Dropbox (NYU Langone Health)\\OlfactometerEngineeringGroup (2)\\Control\\a_software\\OlfaControl_GUI\\calibration_tables'
        self.flow_cal_dir = 'C:\\Users\\Admin\\Dropbox (NYU Langone Health)\\OlfactometerEngineeringGroup (2)\\Control\\a_software\\OlfaControl_GUI\\calibration_tables'
        '''
        self.flow_cal_dir = utils.find_olfaControl_directory() + '\\calibration_tables' # NOTE: this takes a super long time
        
        if os.path.exists(self.flow_cal_dir):
            logger.debug('loading flow sensor calibration tables (%s)', self.flow_cal_dir)

            file_type = '.txt'
            cal_file_names = os.listdir(self.flow_cal_dir)
            cal_file_names = [fn for fn in cal_file_names if fn.endswith(file_type)]    # only txt files # TODO: change to csv
            if cal_file_names == []:
                logger.warning('no cal files found')
            else:
                # create dictionaries
                new_sccm2Ard_dicts = {}
                new_ard2Sccm_dicts = {}
                for cal_file in cal_file_names:
                    x = 0       # what is this
                    idx_ext = cal_file.find('.')
                    file_name = cal_file[:idx_ext]
                    sccm2Ard = {}
                    ard2Sccm = {}
                    cal_file_full_dir = self.flow_cal_dir + '\\' + cal_file
                    with open(cal_file_full_dir, newline='') as f:
                        # skip over header line
                        csv_reader = csv.reader(f)
                        firstLine = next(csv_reader)
                        # get the shit
                        reader = csv.DictReader(f, delimiter=',')
                        for row in reader:
                            if x == 0:
                                try:
                                    sccm2Ard[int(row['SCCM'])] = int(row['int'])
                                    ard2Sccm[int(row['int'])] = int(row['SCCM'])
                                except KeyError as err:
                                    logger.warning('error: %s',err)
                                    logger.warning('%s does not have correct headings for calibration files', cal_file)
                                    x = 1   # don't keep trying to read this file
                    if bool(sccm2Ard) == True:
                        new_sccm2Ard_dicts[file_name] = sccm2Ard
                        new_ard2Sccm_dicts[file_name] = ard2Sccm
                
                # if new dicts are not empty, replace the old ones
                if len(new_sccm2Ard_dicts) != 0:
                    self.sccm2Ard_dicts = new_sccm2Ard_dicts
                    self.ard2Sccm_dicts = new_ard2Sccm_dicts
                else:
                    logger.info('no calibration files found in this directory')
            
        else:
            logger.warning('Cannot find flow cal directory (searched in %s)', self.flow_cal_dir)   # TODO this is big issue if none found
    
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
        self.refresh_btn = QPushButton(text="Refresh",clicked=self.get_ports)
        self.get_ports()
        connect_box_layout = QFormLayout()
        connect_box_layout.addRow(QLabel(text="Select Port:"),self.port_widget)
        connect_box_layout.addRow(self.refresh_btn,self.connect_btn)
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
        timebt_layout.addWidget(QLabel(text="Time b/t requests for slave data (ms):"))
        timebt_layout.addWidget(self.m_timebtreqs)
        timebt_layout.addWidget(self.m_timebtreqs_btn)

        self.m_manualcmd = QLineEdit(text='xx',#defManualCmd,
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
        raw_write_layout.addWidget(QLabel('wrote to serial port:'))
        raw_write_layout.addWidget(self.raw_write_display)

        self.raw_read_display = QTextEdit(readOnly=True)
        raw_read_layout = QVBoxLayout()
        raw_read_layout.addWidget(QLabel('read from serial port:'))
        raw_read_layout.addWidget(self.raw_read_display)

        raw_comm_layout = QHBoxLayout()
        raw_comm_layout.addLayout(raw_read_layout)
        raw_comm_layout.addLayout(raw_write_layout)
        self.raw_comm_box.setLayout(raw_comm_layout)

        self.raw_write_display.setMinimumWidth(230)
        self.raw_read_display.setMinimumWidth(230)
        
    def create_slave_groupbox(self):
        self.slave_groupbox = QGroupBox('Slaves')

        self.slave_objects = []
        for s in slave_names:
            create_slave = slave_8vials(parent=self,name=s)
            self.slave_objects.append(create_slave)

        self.slave_layout = QVBoxLayout()
        for s in self.slave_objects:
            self.slave_layout.addWidget(s)
            s.setEnabled(False)
        
        self.slave_widget = QWidget()
        self.slave_widget.setLayout(self.slave_layout)

        self.slave_scrollArea = QScrollArea()
        self.slave_scrollArea.setWidget(self.slave_widget)

        self.nothing_layout = QHBoxLayout()
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
    
    def port_changed(self):
        if self.port_widget.count() != 0:
            self.port = self.port_widget.currentText()
            if self.port == noPort_msg:
                self.connect_btn.setEnabled(False)
                self.connect_btn.setText(noPort_msg)
            else:
                self.portStr = self.port[:self.port.index(':')]
                self.connect_btn.setEnabled(True)
                self.connect_btn.setText("Connect to  " + self.portStr)
    
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
            logger.debug('connected to Arduino')
            self.get_slave_addresses()
            self.master_groupbox.setEnabled(True)
            self.connect_btn.setText('Stop communication w/ ' + self.portStr)
            self.refresh_btn.setEnabled(False)
            self.port_widget.setEnabled(False)
        else:
            logger.debug('disconnected from Arduino')
            self.master_groupbox.setEnabled(False)
            self.connect_btn.setText('Connect to ' + self.portStr)
            self.connect_btn.setChecked(False)
            self.refresh_btn.setEnabled(True)
            self.port_widget.setEnabled(True)

            # set vials of all currently active slaves to not debug TODO do this in a thread
            for slave in self.active_slaves:
                for vial in range(0,vialsPerSlave):
                    strToSend = 'MS_' + slave + str(vial+1)
                    self.send_to_master(strToSend)
                    time.sleep(.3)

    def get_slave_addresses(self):
        self.prev_active_slaves = copy.copy(self.active_slaves)
        self.active_slaves = []
        logger.info('Checking slave addresses')
        self.send_to_master('C')
        # TODO update program

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
                        
                # IF FLOW UPDATE WAS SENT: send to main GUI window (to write to datafile)
                if len(text) == 17:
                    text = text[3:]     # remove arduino logging info

                    # split up for writing to datafile
                    slave_vial = text[0:2]
                    flowVal = text[2:6]
                    ctrlVal = text[6:10]

                    # send to main GUI
                    device = 'olfactometer ' + slave_vial
                    unit = 'FL'
                    value = flowVal
                    try:
                        self.window().receive_data_from_device(device,unit,value)
                    except AttributeError as err:   # if main window is not open
                        pass
            
            except UnicodeDecodeError as err:
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

    '''
    # LOGGING
    logger = logging.getLogger(name='olfactometer')
    logger.setLevel(logging.DEBUG)
    # console handler
    console_handler_level = logging.DEBUG
    console_handler_formatter = logging.Formatter('%(name)-14s: %(levelname)-8s: %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_handler_level)
    console_handler.setFormatter(console_handler_formatter)
    logger.addHandler(console_handler)
    '''

    
    # MAIN APP
    logger.debug('opening window')
    app1 = QApplication(sys.argv)
    theWindow = olfactometer_window()
    theWindow.show()
    sys.exit(app1.exec_())