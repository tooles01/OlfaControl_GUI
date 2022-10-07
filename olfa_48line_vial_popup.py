import sys, logging, time
import os, csv, copy
from turtle import width
from PyQt5 import QtCore, QtSerialPort
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer
from serial.tools import list_ports
from datetime import datetime, timedelta
import numpy as np
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot, QTimer

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
def_calfile_name = 'A2_test_cal_file'
def_mfc_cal_value = '100'


# CREATE LOGGER
logger = logging.getLogger(name='vial popup')
logger.setLevel(logging.DEBUG)
if logger.hasHandlers():    logger.handlers.clear()     # removes duplicate log messages
console_handler = utils.create_console_handler()
logger.addHandler(console_handler)


class calibration_worker(QObject):
    def __init__(self):
        super().__init__()

        self.calibration_setpoint = 0

    @pyqtSlot()
    def read_flow_values(self):
        t_1 = time.time()
        t_2 = 0
        serial_values = []
        while t_2 < t_1 + 1:
            t_2 = time.time()
            this_read = 1
            serial_values.append(this_read)

        serial_converted = [float(i) for i in serial_values]



class VialDetailsPopup(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.full_vialNum = parent.full_vialNum
        
        self.create_ui_features()
        self.setWindowTitle('Vial ' + self.full_vialNum + ' - Details')

    def create_ui_features(self):
        self.vial_details_create_std_widgets_box()
        
        self.db_readflow_btn = QPushButton(text='Read flow values',checkable=True)
        self.db_readflow_btn.toggled.connect(lambda: self.parent.readFlow_btn_toggled(self.db_readflow_btn))
        self.db_advanced_btn = QPushButton(text='Enable Advanced Options',checkable=True,toggled=self.parent.toggled_advanced_settings,toolTip='ARE YOU SURE')     
        
        self.vial_details_create_flow_ctrl_box()
        self.vial_details_create_man_control_box()
        self.vial_details_create_calibration_box()

        # Values Received
        self.data_receive_lbl = QLabel(("Flow val (int), Flow (SCCM), Ctrl val (int)"))
        self.data_receive_box = QTextEdit(readOnly=True)

        # Layout
        layout_col1_widgets = QGridLayout()
        layout_col1_widgets.addWidget(self.db_std_widgets_box,0,0,1,2)  # row 0 col 0
        layout_col1_widgets.addWidget(self.cal_box,1,0,1,2)             # row 1 col 0
        layout_col1_widgets.addWidget(self.db_readflow_btn,2,0,1,1)     # row 2 col 0
        layout_col1_widgets.addWidget(self.db_advanced_btn,2,1,1,2)     # row 2 col 1
        layout_col1_widgets.addWidget(self.db_flow_control_box,3,0,1,1)     # row 3 col 0
        layout_col1_widgets.addWidget(self.db_manual_control_box,3,1,1,1)   # row 3 col 1
        layout_col2_data = QVBoxLayout()
        layout_col2_data.addWidget(self.data_receive_lbl)
        layout_col2_data.addWidget(self.data_receive_box)

        self.vial_debug_window_layout = QHBoxLayout()
        self.vial_debug_window_layout.addLayout(layout_col1_widgets)
        self.vial_debug_window_layout.addLayout(layout_col2_data)
        self.setLayout(self.vial_debug_window_layout)
        
        # set boxes to the same height
        h1 = self.db_flow_control_box.sizeHint().height()
        h2 = self.db_manual_control_box.sizeHint().height()
        h_to_use = max(h1,h2)
        self.db_flow_control_box.setFixedHeight(h_to_use)
        self.db_manual_control_box.setFixedHeight(h_to_use)

    def vial_details_create_std_widgets_box(self):
        self.db_std_widgets_box = QGroupBox()

        # Open Vial
        self.db_open_valve_wid = QLineEdit(text='5')        # pos change to spinbox so min/max can be set
        self.db_open_valve_btn = QPushButton('Open vial',checkable=True)
        self.db_open_valve_btn.toggled.connect(self.parent.debugwin_vialOpen_toggled)
        
        # Setpoint
        self.db_setpoint_value_box = QLineEdit(text=default_setpoint)
        self.db_setpoint_send_btn = QPushButton('Update Spt')
        self.db_setpoint_value_box.returnPressed.connect(lambda: self.parent.setpoint_btn_clicked(self.db_setpoint_value_box.text()))
        self.db_setpoint_send_btn.clicked.connect(lambda: self.parent.setpoint_btn_clicked(self.db_setpoint_value_box.text()))
        
        # Flow Calibration Table
        self.db_cal_table_combobox = QComboBox()
        self.db_cal_table_combobox.addItems(self.parent.olfactometer_parent_object.ard2Sccm_dicts)
        self.db_cal_table_combobox.setCurrentText(self.parent.cal_table)
        self.db_cal_table_combobox.currentIndexChanged.connect(lambda: self.parent.cal_table_updated(self.db_cal_table_combobox.currentText()))
        self.db_calibrate_sensor_btn = QPushButton(text='Calibrate')
        self.db_calibrate_sensor_btn.clicked.connect(self.parent.calibrate_flow_sensor_btn_clicked)

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

        self.db_Kp_wid = QLineEdit(text=str(self.parent.Kp_value))
        self.db_Ki_wid = QLineEdit(text=str(self.parent.Ki_value))
        self.db_Kd_wid = QLineEdit(text=str(self.parent.Kd_value))
        self.db_Kp_send = QPushButton(text='Send')
        self.db_Ki_send = QPushButton(text='Send')
        self.db_Kd_send = QPushButton(text='Send')
        self.db_Kp_send.clicked.connect(lambda: self.parent.K_parameter_update('P',self.db_Kp_wid.text()))
        self.db_Ki_send.clicked.connect(lambda: self.parent.K_parameter_update('I',self.db_Ki_wid.text()))
        self.db_Kd_send.clicked.connect(lambda: self.parent.K_parameter_update('D',self.db_Kd_wid.text()))

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
        self.db_PID_toggle_btn = QPushButton(text="Turn flow control off",checkable=True,toggled=self.parent.flowCtrl_toggled)
        self.db_PID_toggle_btn.setMinimumWidth(self.db_PID_toggle_btn.sizeHint().width())   # just for sizing
        self.db_PID_toggle_btn.setText('Turn flow control on')                              # just for sizing
        self.db_ctrl_toggle_btn = QPushButton(text="Open prop valve",checkable=True,toggled=self.parent.propValve_toggled)
        self.db_vlve_toggle_btn = QPushButton(text="Open Iso Valve",checkable=True)#,toggled=self.vialOpen_toggled) # TODO
        manual_debug_layout = QVBoxLayout()
        manual_debug_layout.addWidget(self.db_PID_toggle_btn)
        manual_debug_layout.addWidget(self.db_ctrl_toggle_btn)
        manual_debug_layout.addWidget(self.db_vlve_toggle_btn)
        self.db_manual_control_box.setLayout(manual_debug_layout)
        
        self.db_manual_control_box.setEnabled(False)     # disable until advanced options toggled
    
    def vial_details_create_calibration_box(self):
        self.cal_box = QGroupBox('Calibration')

        self.cal_file_name_lineedit = QLineEdit(text=def_calfile_name)
        self.cal_file_dir_lineedit = QLineEdit(text=self.parent.olfactometer_parent_object.flow_cal_dir)

        self.create_new_cal_file_btn = QPushButton(text='Create file',checkable=True)
        self.create_new_cal_file_btn.toggled.connect(self.create_new_cal_file_clicked)

        self.mfc_value_lineedit = QLineEdit(text=def_mfc_cal_value)
        self.mfc_value_set_btn = QPushButton(text='Start',checkable=True)
        #self.mfc_value_lineedit.returnPressed.connect(self.new_mfc_value_set)  # TODO
        self.mfc_value_set_btn.toggled.connect(self.new_mfc_value_set)
        self.mfc_value_lineedit.setEnabled(False)
        self.mfc_value_set_btn.setEnabled(False)
        
        layout_labels = QVBoxLayout()
        layout_labels.addWidget(QLabel('Directory:'))
        layout_labels.addWidget(QLabel('File Name:'))
        layout_labels.addWidget(QLabel('MFC value:'))
        layout_widgets = QFormLayout()
        layout_widgets.addRow(self.cal_file_dir_lineedit)
        layout_widgets.addRow(self.cal_file_name_lineedit,self.create_new_cal_file_btn)
        layout_widgets.addRow(self.mfc_value_lineedit,self.mfc_value_set_btn)
        layout_full = QHBoxLayout()
        layout_full.addLayout(layout_labels)
        layout_full.addLayout(layout_widgets)

        self.cal_box.setLayout(layout_full)

    
    def create_new_cal_file_clicked(self):
        # Clicked - create new file, start procedure
        if self.create_new_cal_file_btn.isChecked() == True:
            
            # UI THINGS
            self.create_new_cal_file_btn.setText('Done')
            self.create_new_cal_file_btn.setToolTip('Click to end calibration and save file')
            self.cal_file_dir_lineedit.setEnabled(False)
            self.cal_file_name_lineedit.setEnabled(False)
            self.db_std_widgets_box.setEnabled(False)
            self.db_flow_control_box.setEnabled(False)
            
            # Get file name & directory from GUI
            self.new_cal_file_name = self.cal_file_name_lineedit.text()
            self.new_cal_file_dir = self.cal_file_dir_lineedit.text() + '\\' + self.new_cal_file_name + '.csv'

            # Hopefully this file does not exist
            if not os.path.exists(self.new_cal_file_dir):
                logger.info('creating new calibration file at %s', self.new_cal_file_dir)
                file_created_time = utils.get_current_time()
                File = self.new_cal_file_name,file_created_time
                row_headers = 'SCCM','int'
                # Write file header
                with open(self.new_cal_file_dir,'a',newline='') as f:
                    writer = csv.writer(f,delimiter=',')
                    writer.writerow(File)
                    writer.writerow(row_headers)
                
                # enable the MFC stuff
                self.mfc_value_lineedit.setEnabled(True)
                self.mfc_value_set_btn.setEnabled(True)

            else:
                logger.error('this calibration file already exists!!!!!')
                self.create_new_cal_file_btn.setChecked(False)
  
        # Unclicked - done with calibration
        else:
            # UI THINGS
            self.create_new_cal_file_btn.setText('Create file')
            self.create_new_cal_file_btn.setToolTip('')
            self.cal_file_dir_lineedit.setEnabled(True)
            self.cal_file_name_lineedit.setEnabled(True)
            self.db_std_widgets_box.setEnabled(True)
            self.db_flow_control_box.setEnabled(True)


    def new_mfc_value_set(self):
        if self.mfc_value_set_btn.isChecked() == True:
            self.mfc_value_set_btn.setText('End early')

            self.this_cal_sccm_value = self.mfc_value_lineedit.text()
            logger.debug('starting calibration at %s sccm', self.this_cal_sccm_value)
            
            self.parent.olfactometer_parent_object.calibration_on = True
            self.serial_values = []
        else:
            self.mfc_value_set_btn.setText('Start')
    
    def read_value(self,incoming_value):
        #num_samples = 300    # 30 seconds is 300 samples (assuming we are sampling every 100ms)
        num_samples = 400

        # once we've collected enough samples
        if len(self.serial_values) >= num_samples:
            # check the range of values in the list
            min_val = min(self.serial_values)
            max_val = max(self.serial_values)
            full_range = max_val - min_val
            # if the range is not yet acceptable
            if full_range > 2:
                self.serial_values.pop(0)                       # pop the top value
                self.serial_values.append(int(incoming_value))  # append the new value
            # if the range is good:
            else:
                self.serial_converted = [float(i) for i in self.serial_values]
                
                # calculate mean
                self.this_cal_int_value = np.mean(self.serial_converted)
                
                # send the value to the table
                self.save_calibration_value()
                
        # if we have not yet collected enough data points:
        else:
            self.serial_values.append(int(incoming_value))
    
    def save_calibration_value(self):
        # write the MFC value and the integer value to the calibration table
        pair_to_write = self.this_cal_sccm_value,round(self.this_cal_int_value,2)
        logger.info('writing to cal file: %s', pair_to_write)
        with open(self.new_cal_file_dir,'a',newline='') as f:
            writer = csv.writer(f,delimiter=',')
            writer.writerow(pair_to_write)

        # clear lists
        self.serial_values = []
        self.serial_converted = []

        # reset
        self.parent.olfactometer_parent_object.calibration_on = False
        self.mfc_value_set_btn.setChecked(False)
    
    
    
    def closeEvent(self, event):
        self.parent.vial_details_btn.setChecked(False)