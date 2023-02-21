import os, logging, csv, copy, time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer
from datetime import datetime, timedelta
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
import numpy as np

import utils, utils_olfa_48line


##############################
# DEFAULT VALUES
default_setpoint = '50'
def_open_duration = '5'
default_cal_table = 'Honeywell_3100V'
def_Kp_value = '0.0500'
def_Ki_value = '0.0001'
def_Kd_value = '0.0000'
def_calfile_name = 'A2_test_cal_file'
def_mfc_cal_value = '100'
##############################

##############################
# CREATE LOGGER
logger = logging.getLogger(name='vial popup')
logger.setLevel(logging.DEBUG)
if logger.hasHandlers():    logger.handlers.clear()     # removes duplicate log messages
console_handler = utils.create_console_handler()
logger.addHandler(console_handler)
##############################


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

    # GUI FEATURES
    def create_ui_features(self):
        self.vial_details_create_settings_box()
        
        self.db_readflow_btn = QPushButton(text='Read flow values',checkable=True)
        self.db_readflow_btn.toggled.connect(lambda: self.parent.readFlow_btn_toggled(self.db_readflow_btn))
        self.db_advanced_btn = QPushButton(text='Advanced',checkable=True,toggled=self.parent.toggled_advanced_settings)
        self.db_advanced_btn.setToolTip('Enable advanced flow control settings\n\nARE YOU SURE YOU WANT TO DO THIS')
        
        self.vial_details_create_flow_ctrl_box()
        self.vial_details_create_man_control_box()
        self.vial_details_create_calibration_box()

        # Values Received
        self.data_receive_lbl = QLabel(("Flow val (int), Flow (SCCM), Ctrl val (int)"))
        self.data_receive_box = QTextEdit(readOnly=True)
        self.data_receive_box.setFixedWidth(220)

        # Layout
        layout_col1_widgets = QGridLayout()
        layout_col1_widgets.addWidget(self.db_std_widgets_box,0,0,1,2)      # row 0 col 0
        layout_col1_widgets.addWidget(self.db_readflow_btn,1,0,1,1)         # row 1 col 0
        layout_col1_widgets.addWidget(self.db_advanced_btn,1,1,1,2)         # row 1 col 1
        layout_col1_widgets.addWidget(self.db_flow_control_box,2,0,1,1)     # row 2 col 0
        layout_col1_widgets.addWidget(self.db_manual_control_box,2,1,1,1)   # row 2 col 1
        layout_col1_widgets.addWidget(self.cal_box,3,0,1,2)                 # row 3 col 0
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

    def vial_details_create_settings_box(self):
        self.db_std_widgets_box = QGroupBox("Settings")
        
        # VALVE OPEN
        self.db_valve_open_lbl = QLabel('Duration to open (s):')
        self.db_valve_dur_wid = QLineEdit(text=def_open_duration)        # pos change to spinbox so min/max can be set (& to match olfa driver)
        self.db_valve_open_btn = QPushButton('Open vial',checkable=True)
        #self.db_valve_open_btn.toggled.connect(self.parent.debugwin_vialOpen_toggled)
        self.db_valve_open_btn.toggled.connect(self.vialOpen_toggled)
        
        # SETPOINT
        self.db_setpoint_lbl = QLabel('Setpoint (sccm):')
        self.db_setpoint_value_box = QLineEdit(text=default_setpoint)
        self.db_setpoint_send_btn = QPushButton('Update Spt')
        self.db_setpoint_value_box.returnPressed.connect(lambda: self.parent.setpoint_btn_clicked(self.db_setpoint_value_box.text()))
        self.db_setpoint_send_btn.clicked.connect(lambda: self.parent.setpoint_btn_clicked(self.db_setpoint_value_box.text()))
        
        # FLOW CALIBRATION TABLE
        self.db_cal_table_lbl = QLabel('Calibration table:')
        self.db_cal_table_combobox = QComboBox()
        self.db_cal_table_combobox.addItems(self.parent.olfactometer_parent_object.ard2Sccm_dicts)
        self.db_cal_table_combobox.setCurrentText(self.parent.cal_table)    # set default to this vial's calibration table
        self.db_cal_table_combobox.currentIndexChanged.connect(lambda: self.parent.cal_table_updated(self.db_cal_table_combobox.currentText()))
        self.db_calibrate_sensor_btn = QPushButton(text='Calibrate')
        self.db_calibrate_sensor_btn.clicked.connect(self.parent.calibrate_flow_sensor_btn_clicked)
        
        # set second widgets to the same width (to mimic a QFormLayout)
        width_to_use = self.db_cal_table_combobox.sizeHint().width()
        self.db_valve_dur_wid.setFixedWidth(width_to_use)
        self.db_setpoint_value_box.setFixedWidth(width_to_use)
        self.db_cal_table_combobox.setFixedWidth(width_to_use)
        
        # LAYOUT
        layout_labels = QVBoxLayout()
        layout_labels.addWidget(self.db_valve_open_lbl)
        layout_labels.addWidget(self.db_setpoint_lbl)
        layout_labels.addWidget(self.db_cal_table_lbl)
        layout_widgets = QFormLayout()
        layout_widgets.addRow(self.db_valve_dur_wid,self.db_valve_open_btn)
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
        
        self.db_ctrl_toggle_btn = QPushButton(text="Open prop valve",checkable=True,toggled=self.prop_valve_toggled)
        self.db_vlve_toggle_btn = QPushButton(text="Open Iso Valve",checkable=True,toggled=self.iso_valve_toggled)
        self.db_PID_toggle_btn = QPushButton(text="Turn flow control off",checkable=True,toggled=self.flow_control_toggled)
        self.db_PID_toggle_btn.setMinimumWidth(self.db_PID_toggle_btn.sizeHint().width())   # just for sizing
        self.db_PID_toggle_btn.setText('Turn flow control on')                              # just for sizing
        #self.db_ctrl_toggle_btn.toggled.connect(self.prop_valve_toggled)
        #self.db_vlve_toggle_btn.toggled.connect(self.iso_valve_toggled)
        #self.db_PID_toggle_btn.toggled.connect(self.flow_control_toggled)
        
        manual_debug_layout = QVBoxLayout()
        manual_debug_layout.addWidget(self.db_ctrl_toggle_btn)
        manual_debug_layout.addWidget(self.db_vlve_toggle_btn)
        manual_debug_layout.addWidget(self.db_PID_toggle_btn)
        self.db_manual_control_box.setLayout(manual_debug_layout)
        
        self.db_manual_control_box.setEnabled(False)     # disable until advanced options toggled
    
    def vial_details_create_calibration_box(self):
        self.cal_box = QGroupBox('Flow Sensor Calibration')

        self.cal_file_name_wid = QLineEdit(text=def_calfile_name)
        self.cal_file_dir_wid = QLineEdit(text=self.parent.olfactometer_parent_object.flow_cal_dir)
        self.create_new_cal_file_btn = QPushButton(text='Create file',checkable=True,toggled=self.create_new_cal_file_toggled)
        
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
        layout_widgets.addRow(self.cal_file_dir_wid)
        layout_widgets.addRow(self.cal_file_name_wid,self.create_new_cal_file_btn)
        layout_widgets.addRow(self.mfc_value_lineedit,self.mfc_value_set_btn)
        layout_full = QHBoxLayout()
        layout_full.addLayout(layout_labels)
        layout_full.addLayout(layout_widgets)

        self.cal_box.setLayout(layout_full)
    
    
    # COMMANDS
    def vialOpen_toggled(self, checked):
        if checked:
            self.parent.open_vial(self.db_valve_dur_wid.text())
            self.db_valve_open_btn.setText('Close vial')
        else:
            self.parent.close_vial()
    
    def flow_control_toggled(self, checked):
        # Turn PID (flow control) on
        if checked:
            logger.debug('flow control manually turned on')
            self.db_PID_toggle_btn.setText('Turn flow control off')
            strToSend = 'S_ON_' + self.full_vialNum
            self.parent.parent().parent.send_to_master(strToSend)
        # Turn PID (flow control) off
        else:
            logger.debug('flow control manually turned off')
            self.db_PID_toggle_btn.setText('Turn flow control on')
            strToSend = 'S_OF_' + self.full_vialNum
            self.parent.parent().parent.send_to_master(strToSend)
    
    def prop_valve_toggled(self, checked):
        # Open proportional valve
        if checked:
            logger.debug('proportional valve manually opened')
            self.db_ctrl_toggle_btn.setText('Close prop valve')
            strToSend = 'S_OC_' + self.full_vialNum
            self.parent.parent().parent.send_to_master(strToSend)
        # Close proportional valve
        else:
            logger.debug('proportional valve manually closed')
            self.db_ctrl_toggle_btn.setText('Open prop valve')
            strToSend = 'S_CC_' + self.full_vialNum
            self.parent.parent().parent.send_to_master(strToSend)
    
    def iso_valve_toggled(self,checked):
        # Open isolation valve
        if checked:
            logger.debug('isolation valve manually opened')
            self.db_vlve_toggle_btn.setText("Close Iso Valve")
            strToSend = 'S_OI_' + self.full_vialNum
            self.parent.parent().parent.send_to_master(strToSend)
        # Close isolation valve
        else:
            logger.debug('isolation valve manually closed')
            self.db_vlve_toggle_btn.setText("Open Iso Valve")
            strToSend = 'S_CI_' + self.full_vialNum
            self.parent.parent().parent.send_to_master(strToSend)
    
    def create_new_cal_file_toggled(self):
        # Create new file, start procedure
        if self.create_new_cal_file_btn.isChecked() == True:
            # UI THINGS
            self.create_new_cal_file_btn.setText('Done calibrating')
            self.create_new_cal_file_btn.setToolTip('Click to end calibration and save file')
            self.cal_file_dir_wid.setEnabled(False)
            self.cal_file_name_wid.setEnabled(False)
            self.db_std_widgets_box.setEnabled(False)
            self.db_flow_control_box.setEnabled(False)
            
            # Get file name & directory from GUI
            self.new_cal_file_name = self.cal_file_name_wid.text()
            self.new_cal_file_dir = self.cal_file_dir_wid.text() + '\\' + self.new_cal_file_name + '.csv'

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
                logger.error('cannot create calibration file, ' + self.new_cal_file_name + ' already exists!!!!!')
                self.create_new_cal_file_btn.setChecked(False)
        
        # Done with calibration
        else:    
            # UI THINGS
            self.create_new_cal_file_btn.setText('Create file')
            self.create_new_cal_file_btn.setToolTip('')
            self.cal_file_dir_wid.setEnabled(True)
            self.cal_file_name_wid.setEnabled(True)
            self.db_std_widgets_box.setEnabled(True)
            self.db_flow_control_box.setEnabled(True)
    
    
    def new_mfc_value_set(self):
        if self.mfc_value_set_btn.isChecked() == True:
            self.this_cal_sccm_value = self.mfc_value_lineedit.text()
            logger.debug('starting calibration at %s sccm', self.this_cal_sccm_value)
            
            # TODO check that proportional valve is open
            self.parent.olfactometer_parent_object.calibration_on = True
            self.serial_values = []
            self.serial_values_std = []
            self.start_of_good_values = []
            self.duration_of_good_values = timedelta(0,10)  # 10 sec
            self.all_std_devs = []
            self.values_means = []

            self.mfc_value_set_btn.setText('End early')
        
        else:
            self.mfc_value_set_btn.setText('Start')
    
    def read_value(self,incoming_value):
        # wait until this many seconds have passed
        samples_per_sec = 10
        sec_to_wait = 40
        num_samples = sec_to_wait * samples_per_sec  # 10 samples per second (assuming 100ms sampling rate)

        moving_mean_over = 10  # calculate moving mean over 10 points
        
        # once 30 seconds has passed
        if len(self.serial_values) >= num_samples:

            # if we haven't done any calculations yet, get the first set of them
            if self.values_means == []:
                for m in range(0,num_samples):
                    # calculate moving mean over the first 10 points and append
                    idx_1 = m
                    idx_2 = idx_1 + moving_mean_over
                    this_range = copy.copy(self.serial_values[idx_1:idx_2])
                    this_mean = np.mean(this_range)
                    self.values_means.append(this_mean)
            
            # check the last 30 moving means and see if the range is greater than .2
            min_mean = min(self.values_means)
            max_mean = max(self.values_means)
            range_means = max_mean-min_mean

            # if data looks stable: # TODO might need to alter this for setpoints that are in between integers? figure this out
            if range_means < .5:
                self.serial_converted = [float(i) for i in self.serial_values]
                self.this_cal_int_value = np.mean(self.serial_converted)    # calculate mean
                self.save_calibration_value()                               # save value to calibration table
            
            # if it wasn't good:
            else:
                # pop serial values
                self.serial_values.pop(0)
                self.serial_values.append(int(incoming_value))
                
                # calculate means again
                self.values_means = []
                for m in range(0,num_samples):
                    # calculate moving mean over the first 10 points and append
                    idx_1 = m
                    idx_2 = idx_1 + moving_mean_over
                    this_range = copy.copy(self.serial_values[idx_1:idx_2])
                    this_mean = np.mean(this_range)
                    self.values_means.append(this_mean)

                # check the last 30 moving means and see if the range is greater than .2
                min_mean = min(self.values_means)
                max_mean = max(self.values_means)
                range_means = max_mean-min_mean

                # if data looks stable:
                if range_means < .5:
                    self.serial_converted = [float(i) for i in self.serial_values]
                    self.this_cal_int_value = np.mean(self.serial_converted)    # calculate mean
                    self.save_calibration_value()                               # save value to calibration table
            
            '''
            # moving average (over 10 points I think)
            #this_mean=np.convolve(self.serial_values,np.ones(10),'valid')/10
            range_to_iterate = int((num_samples/samples_per_sec)+1)
            idx_2 = 0
            for m in range(1,range_to_iterate):
                idx_1 = idx_2 + 1
                idx_2 = idx_1 + samples_per_sec
                this_range = copy.copy(self.serial_values[idx_1:idx_2])
                this_range_mean = np.mean(this_range)
                values_means.append(this_range_mean)

            # check the range of values in the list
            min_val = min(self.serial_values)
            max_val = max(self.serial_values)
            full_range = max_val - min_val

            num_std_dev_datapoints = 100
            self.test_std_dev = copy.copy(self.serial_values[num_samples-num_std_dev_datapoints:num_samples])
            self.all_std_devs.append(np.std(self.test_std_dev,ddof=1))
            
            # if the range is less than 2 ints
            if full_range < 2:
                # calculate std dev over the past 10sec of datapoints
                num_std_dev_datapoints = 100
                
                # get the most recent 10 seconds
                self.serial_values_std = copy.copy(self.serial_values[num_samples-num_std_dev_datapoints:num_samples])
                this_std_dev = np.std(self.serial_values_std)   # calculate the std dev
                print(this_std_dev)
                # if this is less than .2, we are good
                if this_std_dev < .2:
                    # if it's the first value under .2
                    if self.start_of_good_values == []:
                        self.start_of_good_values = datetime.now()
                        logger.debug('%s first period std dev is under .2',utils.get_current_time()[:-1])
                    # if there other values there already
                    else:
                        # if it's been 10 seconds since good values started
                        current_time = datetime.now()
                        if (current_time-self.start_of_good_values) >= self.duration_of_good_values:
                            logger.debug('%s: for the past 10 seconds, the std dev (over 5 seconds of data) has been under .2')
                            self.serial_converted = [float(i) for i in self.serial_values]
                            self.this_cal_int_value = np.mean(self.serial_converted)    # calculate mean
                            self.save_calibration_value()                               # save value to calibration table

                else:
                    self.start_of_good_values = []  # need to reset
                    
            '''
            '''
                self.serial_converted = [float(i) for i in self.serial_values]
                self.this_cal_int_value = np.mean(self.serial_converted)    # calculate mean
                self.save_calibration_value()   # save value to calibration table
            '''
            '''
            # if the range is not yet acceptable
            else:
                self.serial_values.pop(0)                       # pop the top value
                self.serial_values.append(int(incoming_value))  # append the new value
            '''
                
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
        # Untoggle button in olfa GUI
        self.parent.vial_details_btn.setChecked(False)