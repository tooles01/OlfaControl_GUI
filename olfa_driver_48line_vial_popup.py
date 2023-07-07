import os, logging, csv, copy, time
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer
from datetime import datetime, timedelta
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
import numpy as np

import utils


##############################
# DEFAULT VALUES
default_setpoint = '50'
def_open_duration = '5'
def_pressurize_duration = '1'
default_cal_table = 'Honeywell_3100V'
def_Kp_value = '0.0500'
def_Ki_value = '0.0001'
def_Kd_value = '0.0000'
#def_calfile_name = 'A2_test_cal_file'
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


mfc_capacity = '200'            # flow sensor max flow
def_calibration_duration = '3'  # calibration per flow rate

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
        self.calibration_on = False
        
        self.create_ui_features()
        self.setWindowTitle('Vial ' + self.full_vialNum + ' - Details')

    # GUI FEATURES
    def create_ui_features(self):        
        self.create_std_widgets_box()
        self.create_setpoint_box()
        self.create_flow_ctrl_box()
        self.create_man_control_box()
        self.create_calibration_box()

        # Values Received
        self.data_receive_lbl = QLabel(("Flow val (int), Flow (SCCM), Ctrl val (int)"))
        self.data_receive_box = QTextEdit(readOnly=True)
        self.data_receive_box.setFixedWidth(220)

        # Layout
        layout_col1_widgets = QGridLayout()
        layout_col1_widgets.addWidget(self.db_std_widgets_box,0,0,1,1)      # row 0 col 0
        layout_col1_widgets.addWidget(self.db_setpoint_groupbox,0,1,1,1)    # row 0 col 1
        layout_col1_widgets.addWidget(self.db_flow_control_box,1,0,1,1)     # row 1 col 0
        layout_col1_widgets.addWidget(self.db_manual_control_box,1,1,1,1)   # row 1 col 1
        layout_col1_widgets.addWidget(self.db_cal_box,2,0,1,2)              # row 2 col 0
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

    def create_std_widgets_box(self):
        self.db_std_widgets_box = QGroupBox("Settings")
        
        # VALVE OPEN
        self.db_valve_open_lbl = QLabel('Duration (s):')
        self.db_valve_open_wid = QLineEdit(text=def_open_duration)        # pos change to spinbox so min/max can be set (& to match olfa driver)
        self.db_valve_open_btn = QPushButton('Open vial',checkable=True)
        self.db_valve_open_btn.toggled.connect(self.vial_open_toggled)

        # VALVE TIMER
        self.valveTimer_duration_label = QLabel('00.000')
        
        # FLOW CALIBRATION TABLE
        self.db_cal_table_lbl = QLabel('Calibration table:')
        self.db_cal_table_combobox = QComboBox()
        self.db_cal_table_combobox.addItems(self.parent.olfactometer_parent_object.ard2Sccm_dicts)
        self.db_cal_table_combobox.setCurrentText(self.parent.cal_table)    # TODO: change this to cycle through and find that cal table, set the index to that
        self.db_cal_table_combobox.currentIndexChanged.connect(lambda: self.parent.cal_table_updated(self.db_cal_table_combobox.currentText()))
        
        # PRESSURIZE VIAL
        self.db_pressurize_lbl = QLabel('Duration (s):')
        self.db_pressurize_wid = QLineEdit(text=def_pressurize_duration)
        self.db_pressurize_btn = QPushButton('Pressurize',checkable=True)
        self.db_pressurize_wid.returnPressed.connect(lambda: self.db_pressurize_btn.setChecked(True))
        self.db_pressurize_btn.toggled.connect(self.pressurizeVial_toggled)

        # PRESSURE TIMER
        self.pressureTimer_lbl = QLabel(self.full_vialNum + ' xxxxx')
        self.pressureTimer_duration_label = QLabel('00.000')
        self.pressure_timer = QTimer()
        self.pressure_timer.setTimerType(0)
        self.pressure_timer.timeout.connect(self.show_pressure_time)
        self.pressureTimer_layout = QHBoxLayout()
        self.pressureTimer_layout.addWidget(self.pressureTimer_lbl)
        self.pressureTimer_layout.addWidget(self.pressureTimer_duration_label)
        self.pressureTimer_layout.addWidget(QLabel('sec'))
        
        # READ FLOW
        self.db_readflow_btn = QPushButton(text='Read flow',checkable=True)
        self.db_readflow_btn.toggled.connect(lambda: self.parent.readFlow_btn_toggled(self.db_readflow_btn))
        
        # ENABLE ADVANCED SETTINGS
        self.db_advanced_btn = QPushButton(text='Enable Advanced Options',checkable=True,toggled=self.toggled_advanced_settings)
        self.db_advanced_btn.setToolTip('Enable advanced flow control settings\n\nARE YOU SURE YOU WANT TO DO THIS')
        
        # LAYOUT
        layout_1 = QGridLayout()
        layout_1.addWidget(self.db_valve_open_lbl,0,0)
        layout_1.addWidget(self.db_valve_open_wid,0,1)
        layout_1.addWidget(self.db_valve_open_btn,0,2)
        layout_1.addWidget(self.valveTimer_duration_label,0,3)
        layout_1.addWidget(self.db_pressurize_lbl,1,0)
        layout_1.addWidget(self.db_pressurize_wid,1,1)
        layout_1.addWidget(self.db_pressurize_btn,1,2)
        layout_1.addWidget(self.pressureTimer_duration_label,1,3)

        layout_cal = QHBoxLayout()
        layout_cal.addWidget(self.db_cal_table_lbl)
        layout_cal.addWidget(self.db_cal_table_combobox)
        self.db_cal_table_lbl.setFixedWidth(self.db_cal_table_lbl.sizeHint().width())
        
        layout_btns = QHBoxLayout()
        layout_btns.addWidget(self.db_readflow_btn)
        layout_btns.addWidget(self.db_advanced_btn)
        
        layout_full = QVBoxLayout()
        layout_full.addLayout(layout_1)
        layout_full.addLayout(layout_cal)
        layout_full.addLayout(layout_btns)
        
        self.db_std_widgets_box.setLayout(layout_full)
        #self.db_std_widgets_box.setFixedHeight(layout_widgets.sizeHint().height() + 24)
    
    def create_setpoint_box(self):
        self.db_setpoint_groupbox = QGroupBox('Setpoint')
        self.setpoint_slider = QSlider()
        self.setpoint_slider.setMaximum(int(mfc_capacity))
        self.setpoint_slider.setToolTip('Adjusts flow set rate.')
        self.setpoint_slider.setTickPosition(3)     # draw tick marks on both sides
        self.setpoint_set_widget = QLineEdit()
        #setpoint_set_widget.setMaximumWidth(4)
        self.setpoint_set_widget.setAlignment(QtCore.Qt.AlignCenter)
        self.setpoint_set_widget.setPlaceholderText('Set value')
        self.setpoint_set_widget.setStatusTip('Type to set flow rate')
        self.setpoint_read_widget = QLCDNumber()
        self.setpoint_read_widget.setMinimumSize(50,50)
        self.setpoint_read_widget.setDigitCount(5)
        self.setpoint_read_widget.setToolTip('Current flow reading')
        self.setpoint_read_widget.setMaximumHeight(50)
        self.setpoint_slider.valueChanged.connect(lambda: self.update_text(value=self.setpoint_slider.value(),spt_set_wid=self.setpoint_set_widget))
        self.setpoint_slider.sliderReleased.connect(lambda: self.slider_released(self.setpoint_slider))
        self.setpoint_set_widget.returnPressed.connect(self.text_changed)
        
        layout_setpoint = QGridLayout()
        layout_setpoint.addWidget(self.setpoint_slider,0,0,2,1)
        layout_setpoint.addWidget(self.setpoint_set_widget,0,1,1,2)
        layout_setpoint.addWidget(self.setpoint_read_widget,1,1,1,2)
        # height
        setpoint_set_read_height = 50
        self.setpoint_set_widget.setMaximumHeight(setpoint_set_read_height)
        self.setpoint_read_widget.setMaximumHeight(setpoint_set_read_height)
        self.setpoint_slider.setMaximumHeight(setpoint_set_read_height*2)
        self.db_setpoint_groupbox.setLayout(layout_setpoint)
        self.db_setpoint_groupbox.setMaximumWidth(120)
    
    def create_flow_ctrl_box(self):
        self.db_flow_control_box = QGroupBox('Flow control parameters')

        self.db_Kp_wid = QLineEdit(text=str(self.parent.Kp_value))
        self.db_Ki_wid = QLineEdit(text=str(self.parent.Ki_value))
        self.db_Kd_wid = QLineEdit(text=str(self.parent.Kd_value))
        self.db_Kp_wid.returnPressed.connect(lambda: self.parent.K_parameter_update('P',self.db_Kp_wid.text()))
        self.db_Ki_wid.returnPressed.connect(lambda: self.parent.K_parameter_update('I',self.db_Ki_wid.text()))
        self.db_Kd_wid.returnPressed.connect(lambda: self.parent.K_parameter_update('D',self.db_Kd_wid.text()))
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
    
    def create_man_control_box(self):
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
    
    def create_calibration_box(self):
        self.db_cal_box = QGroupBox('Flow Sensor Calibration')

        cal_file_name = self.full_vialNum + '_' + utils.currentDate
        self.cal_file_name_wid = QLineEdit(text=cal_file_name)
        self.cal_file_dir_wid = QLineEdit(text=self.parent.olfactometer_parent_object.flow_cal_dir)
        self.create_new_cal_file_btn = QPushButton(text='Create file',checkable=True,toggled=self.create_new_cal_file_toggled)
        
        self.mfc_value_lineedit = QLineEdit(text=def_mfc_cal_value)
        self.start_calibration_btn = QPushButton(text='Start',checkable=True,toolTip='Start calibration at this value')
        #self.mfc_value_lineedit.returnPressed.connect(self.new_mfc_value_set)  # TODO
        self.start_calibration_btn.toggled.connect(self.new_mfc_value_set)
        self.mfc_value_lineedit.setEnabled(False)
        self.start_calibration_btn.setEnabled(False)
        
        # Widget for duration of calibration (& timer for visual)
        self.calibration_duration_lineedit = QLineEdit(text=def_calibration_duration)
        self.calibration_duration_timer = QTimer()
        self.calibration_duration_timer.setTimerType(0) # set to millisecond accuracy
        self.calibration_duration_timer.timeout.connect(self.show_cal_duration_time)
        self.calibration_duration_label = QLabel('00.000')
        
        self.cal_file_output_display = QTextEdit(readOnly=True)
        self.instructions_window = QTextEdit(readOnly=True)
        
        # Layout
        layout_directory = QFormLayout()
        layout_directory.addRow(QLabel('Directory:'),self.cal_file_dir_wid)
        layout_widgets = QFormLayout()
        layout_widgets.addRow(QLabel('File Name:'),self.cal_file_name_wid)
        layout_widgets.addRow(QLabel('MFC value:'),self.mfc_value_lineedit)
        layout_widgets.addRow(QLabel('Duration (s):'),self.calibration_duration_lineedit)
        layout_widgets.addRow(self.calibration_duration_label)
        layout_widgets.addRow(self.create_new_cal_file_btn,self.start_calibration_btn)
        layout_full = QGridLayout()
        layout_full.addLayout(layout_directory,0,0,1,3)
        layout_full.addLayout(layout_widgets,1,0)
        layout_full.addWidget(self.instructions_window,1,1)
        layout_full.addWidget(self.cal_file_output_display,1,2)
        
        self.db_cal_box.setLayout(layout_full)
        
        # Sizing
        self.instructions_window.setMaximumHeight(80)
        self.cal_file_output_display.setMaximumHeight(80)
        self.instructions_window.setMaximumWidth(200)
        self.cal_file_output_display.setMaximumWidth(90)
        self.db_cal_box.setMaximumHeight(self.db_cal_box.sizeHint().height())
        
        self.instructions_window.append('--> To begin calibration, create file')
    
    # PRESSURIZE TIMER
    def start_pressurize(self, duration):
        logger.debug('pressurizing ' + self.full_vialNum + '...')

        # send to olfactometer_window (to send to Arduino)
        strToSend = 'S_OC_' + self.full_vialNum
        self.parent.olfactometer_parent_object.send_to_master(strToSend)

        # start pressurize timer
        self.start_pressure_timer(float(duration))
    
    def start_pressure_timer(self, duration):
        #logger.debug('starting pressurization timer')
        self.pressure_open_time = datetime.now()
        self.pressure_open_duration = timedelta(0,int(duration))
        self.pressure_timer.start()
    
    def show_pressure_time(self):
        current_time = datetime.now()
        current_pressure_dur = current_time - self.pressure_open_time
        if current_pressure_dur >= self.pressure_open_duration:
            self.end_pressure_timer()
        pressure_dur_display_value = str(current_pressure_dur)
        pressure_dur_display_value = pressure_dur_display_value[5:]
        pressure_dur_display_value = pressure_dur_display_value[:-3]
        self.pressureTimer_duration_label.setText(pressure_dur_display_value)
    
    def end_pressure_timer(self):
        logger.debug('pressurization done - closing prop valve ' + self.full_vialNum)
        
        # stop timer
        self.pressure_timer.stop()
        
        # untoggle button
        self.db_pressurize_btn.setChecked(False)
        self.db_pressurize_btn.setText('Pressurize')

    # SETPOINT SLIDER
    # slider changed --> update setpoint set widget
    def update_text(self,value,spt_set_wid):
        spt_set_wid.setText(str(value))
        self.parent.setpoint_set_widget.setText(str(value))     # update main vial set widget
        self.parent.setpoint_slider.setValue(value)             # update main vial slider        
    
    # send new setpoint to MFC
    def slider_released(self, setpoint_slider):
        val = setpoint_slider.value()   # get value of slider
        self.parent.set_flowrate(val)   # set the flowrate
    
    def text_changed(self):
        # text of the line edit has changed -> sets the new MFC value
        try:
            value = float(self.setpoint_set_widget.text())
            self.parent.set_flowrate(value)
            self.setpoint_slider.setValue(value)
        except ValueError as err:
            logger.error('error in setting MFC value: ' + err)    
    

    # COMMANDS
    def vial_open_toggled(self, checked):
        if checked:
            self.parent.open_vial(self.db_valve_open_wid.text())
            self.db_valve_open_btn.setText('Close vial')
        else:
            self.parent.close_vial()
            self.db_valve_open_btn.setText('Open vial')
    
    def pressurizeVial_toggled(self, checked):
        if checked:
            self.db_pressurize_btn.setText('Stop')
            self.start_pressurize(self.db_pressurize_wid.text())
        else:
            self.db_pressurize_btn.setText('Pressurize')
            logger.debug(self.full_vialNum + ' pressurization ended early')
            
            # stop timer
            self.end_pressure_timer()
            
            # send to olfactometer window (to send to Arduino) 
            strToSend = 'S_CC_' + self.full_vialNum
            self.parent.olfactometer_parent_object.send_to_master(strToSend)
        
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
    

    # ADVANCED SETTINGS TOGGLED
    def toggled_advanced_settings(self,checked):
        if checked:
            self.db_flow_control_box.setEnabled(True)
            self.db_manual_control_box.setEnabled(True)
            self.db_advanced_btn.setText('Disable Advanced')
            self.db_advanced_btn.setToolTip('Disable advanced flow control settings')
        else:
            self.db_flow_control_box.setEnabled(False)
            self.db_manual_control_box.setEnabled(False)
            self.db_advanced_btn.setText('Enable Advanced Options')
            self.db_advanced_btn.setToolTip('Enable advanced flow control settings\n\nARE YOU SURE YOU WANT TO DO THIS')
    
    # FLOW CALIBRATION TIMER
    def start_cal_duration_timer(self, duration):
        self.calibration_start_time = datetime.now()
        self.calibration_full_duration = timedelta(0,int(duration))
        self.calibration_duration_timer.start(int(duration))
    
    def show_cal_duration_time(self):
        current_time = datetime.now()
        current_cal_dur = current_time - self.calibration_start_time
        if current_cal_dur >= self.calibration_full_duration:
            self.end_cal_duration_timer()
        
        cal_dur_display_value = str(current_cal_dur)
        cal_dur_display_value = cal_dur_display_value[5:]
        cal_dur_display_value = cal_dur_display_value[:-3]
        self.calibration_duration_label.setText(cal_dur_display_value)
    
    def end_cal_duration_timer(self):
        self.calibration_duration_timer.stop()
        self.calibration_on == False
        self.parent.olfactometer_parent_object.send_to_master('S_CC_' + self.full_vialNum)
        self.analyze_cal_session()
    
    # FLOW CALIBRATION
    def create_new_cal_file_toggled(self):
        # Create new file, start procedure
        if self.create_new_cal_file_btn.isChecked() == True:
            # UI THINGS
            self.create_new_cal_file_btn.setText('End && Save file')
            self.create_new_cal_file_btn.setToolTip('End calibration and save file')
            self.cal_file_dir_wid.setEnabled(False)
            self.cal_file_name_wid.setEnabled(False)
            self.db_std_widgets_box.setEnabled(False)
            self.db_setpoint_groupbox.setEnabled(False)
            self.db_flow_control_box.setEnabled(False)
            
            # Get calibration file name & directory
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
                self.start_calibration_btn.setEnabled(True)

                # check that vial is set to debug (read flow values)
                self.db_readflow_btn.setChecked(True)
                
                # tell user what to do next
                self.instructions_window.clear()
                self.instructions_window.append('--> Disconnect flow sensor output')
                self.instructions_window.append('--> Shut off air to mixing chamber')
                self.instructions_window.append('--> Manually set MFC value')
                self.instructions_window.append('--> Press Start')

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
            self.db_setpoint_groupbox.setEnabled(True)
            
            # Disable the MFC stuff
            self.mfc_value_lineedit.setEnabled(False)
            self.start_calibration_btn.setEnabled(False)
        
    def new_mfc_value_set(self):
        if self.start_calibration_btn.isChecked() == True:
            # Get sccm value & duration
            self.this_cal_sccm_value = self.mfc_value_lineedit.text()
            self.this_cal_duration = self.calibration_duration_lineedit.text()  # TODO check if we have already done this sccm value
            
            logger.debug('starting calibration at %s sccm', self.this_cal_sccm_value)
            logger.warning('~~this not totally finished yet~~')
            
            # Instructions for user
            self.instructions_window.clear()
            self.instructions_window.append('--> Calibrating')
            
            # Fix the GUI
            self.create_new_cal_file_btn.setEnabled(False)
            self.start_calibration_btn.setText('End early')
            
            # Check that olfactometer is connected
            if self.parent.olfactometer_parent_object.connect_btn.isChecked() == False:
                logger.warning('not connected to olfactometer')     # TODO do something about this
            
            # Check that vial is set to debug (read flow values)
            if self.db_readflow_btn.isChecked() == False:
                logger.info('setting ' + self.full_vialNum + ' to debug mode')
                self.db_readflow_btn.setChecked(True)
            else:
                logger.debug(self.full_vialNum + ' is already set to debug mode')
            
            # Open proportional valve
            strToSend = 'S_OC_' + self.full_vialNum
            self.parent.olfactometer_parent_object.send_to_master(strToSend)
            
            # Initialize empty data arrays
            self.serial_values = []
            self.serial_values_std = []
            self.start_of_good_values = []
            self.duration_of_good_values = timedelta(0,10)  # 10 sec
            self.all_std_devs = []
            self.values_means = []
            
            # Set calibration object to ON (start getting calibration values from olfactometer window)
            #self.parent.olfactometer_parent_object.calibration_on = True
            self.calibration_on = True
            
            # Start calibration timer
            self.start_cal_duration_timer(int(self.this_cal_duration))
        
        else:
            self.start_calibration_btn.setText('Start')
            self.create_new_cal_file_btn.setEnabled(True)
            
            # TODO stop the timer
            if self.calibration_duration_timer.isActive() == True:
                self.end_cal_duration_timer()
    
    '''
    def read_value(self, incoming_value):
        # wait until this many seconds have passed
        samples_per_sec = 10
        sec_to_wait = 10        # duration of calibration
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
        
        # if we have not yet collected enough data points:
        else:
            self.serial_values.append(int(incoming_value))
    '''
    
    def analyze_cal_session(self):
        flowVal_median = np.median(self.serial_values)
        # TODO drop the max and min values
        flow_min = min(self.serial_values)
        flow_max = max(self.serial_values)
        flow_range = flow_max - flow_min
        logger.info('range of int values: ' + str(flow_range))
        self.this_cal_int_value = flowVal_median
        self.save_calibration_value()
        # clear the array
        self.serial_values = [] 
    
    def save_calibration_value(self):
        # write the MFC value and the integer value to the calibration table
        pair_to_write = self.this_cal_sccm_value,round(self.this_cal_int_value,2)
        logger.info('writing to cal file: %s', pair_to_write)
        with open(self.new_cal_file_dir,'a',newline='') as f:
            writer = csv.writer(f,delimiter=',')
            writer.writerow(pair_to_write)

        # display what we wrote to the table
        str_to_display = self.this_cal_sccm_value + ', ' + str(round(self.this_cal_int_value,2))
        self.cal_file_output_display.append(str_to_display)
        
        # clear lists
        self.serial_values = []
        self.serial_converted = []

        # reset
        #self.parent.olfactometer_parent_object.calibration_on = False
        self.calibration_on = False
        self.start_calibration_btn.setChecked(False)
        
        # tell user what to do
        self.instructions_window.clear()
        str_to_display = '--> Completed calibration at ' + str(self.this_cal_sccm_value) + ' sccm'
        self.instructions_window.append(str_to_display)
        self.instructions_window.append('-----------------------')
        self.instructions_window.append('--> Enter new MFC value')
        self.instructions_window.append('--> Manually set MFC value')
        self.instructions_window.append('--> Press Start')
    
    
    
    def closeEvent(self, event):
        # Untoggle button in olfa GUI
        self.parent.vial_details_btn.setChecked(False)