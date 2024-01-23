import sys, os, logging, csv, copy, json
from PyQt5 import QtCore, QtSerialPort
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import *
from serial.tools import list_ports
from datetime import datetime, timedelta

import utils, utils_olfa_48line, olfa_driver_48line_vial_popup
import config_olfa_48line as config_olfa
import plot_widget

##############################
# CREATE LOGGER
logger = logging.getLogger(name='olfactometer')
logger.setLevel(logging.DEBUG)
if logger.hasHandlers():    logger.handlers.clear()     # removes duplicate log messages
console_handler = utils.create_console_handler()
logger.addHandler(console_handler)

# add file handler
main_datafile_directory = utils.find_log_directory()
if not os.path.exists(main_datafile_directory): os.mkdir(main_datafile_directory)   # if folder doesn't exist, make it
file_handler = utils.create_file_handler(main_datafile_directory)
logger.addHandler(file_handler)
##############################


'''
import math, time
import config_main
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot

class fake_open_worker(QObject):
    finished = pyqtSignal()
    worker_send_command_to_master = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.threadON = False

        self.fake_open_dur = 0
        self.real_open_dur = 0
        self.full_vialNum = 'E1'
    
    @pyqtSlot()
    def open_this_vial(self):
        if self.threadON == True:

            # create string for fake open command
            worker_strToSend = 'S_OV_' + str(self.fake_open_dur) + '_' + self.full_vialNum
            # send fake open command
            self.worker_send_command_to_master.emit(worker_strToSend)

            # wait that duration
            time.sleep(self.fake_open_dur)

            # wait a little bit longer
            time.sleep(config_main.waitBtSpAndOV)

            # TODO add a check to make sure there's enough time between commands sent to master Arduino (ChatGPT says it takes 2.08ms)
            
            ## REAL OPEN
            # send real command
            logger.info('Opening %s (%s seconds)',self.full_vialNum,self.real_open_dur)
            # TODO start the valve timer here
            worker_strToSend = 'S_OV_' + str(self.real_open_dur) + '_' + self.full_vialNum
            self.worker_send_command_to_master.emit(worker_strToSend)

            self.finished.emit()
'''

class Vial(QGroupBox):

    def __init__(self, parent, vialNum):
        super().__init__()
        self.slaveName = parent.name
        self.vialNum = vialNum
        self.full_vialNum = self.slaveName + self.vialNum
        self.olfactometer_parent_object = parent.parent
        
        # Default Values
        self.flow_value_int = '0'
        self.flow_value_sccm = '0'
        self.ctrl_value_int = '0'
        self.setpoint = int(config_olfa.def_setpoint)
        self.open_duration = config_olfa.def_open_duration
        self.cal_table = config_olfa.default_cal_table
        self.intToSccm_dict = self.olfactometer_parent_object.ard2Sccm_dicts.get(self.cal_table)
        self.sccmToInt_dict = self.olfactometer_parent_object.sccm2Ard_dicts.get(self.cal_table)
        self.Kp_value = config_olfa.def_Kp_value
        self.Ki_value = config_olfa.def_Ki_value
        self.Kd_value = config_olfa.def_Kd_value

        # For Plot Widget
        self.plot_flow_btn = QPushButton(self.full_vialNum, checkable=True)
        self.plot_flow_btn.toggled.connect(self.plot_flow_btn_toggled)
        self.plot_ctrl_btn = QPushButton(self.full_vialNum, checkable=True)
        self.plot_ctrl_btn.toggled.connect(self.plot_ctrl_btn_toggled)
        
        self.generate_stuff()
        
        self.vial_details_window.db_valve_open_wid.returnPressed.connect(lambda: self.vial_details_window.db_valve_open_btn.setChecked(True))        
        
        self.setLayout(self.layout)
        self.valve_open_btn.setMaximumWidth(60)
        max_width = self.sizeHint().width()
        #self.setMaximumWidth(max_width - 10)
        self.setMaximumWidth(max_width)
        '''
        # SET UP WORKER THREAD WHATEVER
        self.obj_fake_open_worker = fake_open_worker()
        self.thread_fake_open = QThread()
        self.obj_fake_open_worker.moveToThread(self.thread_fake_open)
        
        self.obj_fake_open_worker.worker_send_command_to_master.connect(self.olfactometer_parent_object.send_to_master)
        self.obj_fake_open_worker.finished.connect(self.threadIsFinished)
        self.thread_fake_open.started.connect(self.obj_fake_open_worker.open_this_vial)
        '''
    '''
    def threadIsFinished(self):
        logger.debug('thread is finished')
        self.obj_fake_open_worker.threadON = False
        self.thread_fake_open.exit()
    '''
    
    # GUI FEATURES
    def generate_stuff(self):
        
        # VALVE OPEN
        self.valve_dur_spinbox = QSpinBox(value=int(config_olfa.def_open_duration))
        self.valve_dur_spinbox.valueChanged.connect(self.valve_open_dur_changed)
        self.valve_dur_lbl = QLabel("dur (s):")
        self.valve_open_btn = QPushButton(text=str("Open " + self.slaveName + self.vialNum),checkable=True)
        self.valve_open_btn.toggled.connect(self.vial_open_toggled)
        self.valve_open_dur_changed()
        
        # SETPOINT PIANO
        self.setpoint_slider = QSlider()
        self.setpoint_slider.setMaximum(int(config_olfa.mfc_capacity))
        self.setpoint_slider.setToolTip('Adjusts flow set rate.')
        self.setpoint_slider.setTickPosition(3)     # draw tick marks on both sides
        self.setpoint_set_lineedit = QLineEdit()
        self.setpoint_set_lineedit.setAlignment(QtCore.Qt.AlignCenter)
        self.setpoint_set_lineedit.setPlaceholderText('Set value')
        self.setpoint_set_lineedit.setStatusTip('Type to set flow rate')
        self.setpoint_read_widget = QLCDNumber()
        self.setpoint_read_widget.setMinimumSize(50,50)
        self.setpoint_read_widget.setDigitCount(5)
        self.setpoint_read_widget.setToolTip('Current flow reading')
        
        self.setpoint_slider_layout = QGridLayout()
        self.setpoint_slider_layout.addWidget(self.setpoint_slider,0,0,2,1)
        self.setpoint_slider_layout.addWidget(self.setpoint_set_lineedit,0,1,1,2)
        self.setpoint_slider_layout.addWidget(self.setpoint_read_widget,1,1,1,2)
        
        self.setpoint_slider.valueChanged.connect(lambda: self.slider_changed(value=self.setpoint_slider.value(),spt_set_wid=self.setpoint_set_lineedit))
        self.setpoint_slider.sliderReleased.connect(lambda: self.slider_released(self.setpoint_slider))
        self.setpoint_set_lineedit.returnPressed.connect(self.text_changed)
        
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
        self.layout.addRow(self.valve_open_btn)
        self.layout.addRow(self.valve_dur_lbl,self.valve_dur_spinbox)
        self.layout.addRow(self.setpoint_slider_layout)
        self.layout.addRow(self.read_flow_vals_btn,self.vial_details_btn)
        # height
        setpoint_set_read_height = 50
        self.setpoint_set_lineedit.setMaximumHeight(setpoint_set_read_height)
        self.setpoint_read_widget.setMaximumHeight(setpoint_set_read_height)
        self.setpoint_slider.setFixedHeight(setpoint_set_read_height*2)
        # width
        half_col_width = self.read_flow_vals_btn.sizeHint().width()
        self.valve_open_btn.setMaximumWidth(half_col_width)
        #self.setpoint_slider.setFixedWidth(half_col_width)
        self.setpoint_set_lineedit.setMaximumWidth(half_col_width)
        self.setpoint_read_widget.setMaximumWidth(half_col_width)
        self.read_flow_vals_btn.setMaximumWidth(self.read_flow_vals_btn.sizeHint().width())
        #self.vial_details_btn.setFixedWidth(self.vial_details_btn.sizeHint().width())
        #self.setpoint_slider.setFixedWidth(32)
    
    # SETPOINT SLIDER
    # Slider changed --> Update setpoint set widget
    def slider_changed(self,value,spt_set_wid):
        spt_set_wid.setText(str(value))
        self.vial_details_window.setpoint_set_lineedit.setText(str(value))  # update vial details set widget
        self.vial_details_window.setpoint_slider.setValue(value)            # update vial details slider
    
    # Send new setpoint to MFC
    def slider_released(self, setpoint_slider):
        val = setpoint_slider.value()   # get value of slider
        self.set_flowrate(val)          # set the flowrate
    
    def text_changed(self):
        try:
            value = int(self.setpoint_set_lineedit.text())
            self.set_flowrate(value)
        except ValueError:
            pass    # if something other than an integer was entered
    
    # ACTIONS / BUTTON FUNCTIONS
    def plot_flow_btn_toggled(self, checked):
        if checked:
            # Make sure it's already set to debug mode
            if self.read_flow_vals_btn.isChecked() == False:
                self.read_flow_vals_btn.setChecked(True)
            
            # Tell plot window this vial needs to be plotted
            self.olfa_plot_object = self.parent().parent.flow_plot_window
            flag = 0
            for idx in range(len(self.olfa_plot_object.vials_to_plot)):
                if self.olfa_plot_object.vials_to_plot[idx] == '-':
                    self.olfa_plot_object.vials_to_plot[idx] = self
                    self.olfa_plot_object.vials_to_plot_names[idx] = self.full_vialNum
                    flag = 1
                    break
            if flag == 0:
                logger.debug('only 4 vials can be plotted at once')
                self.plot_flow_btn.setChecked(False)
        
        else:
            # Remove from vials_to_plot
            list_of_vials_to_plot_names = self.parent().parent.flow_plot_window.vials_to_plot_names
            if self.full_vialNum in list_of_vials_to_plot_names:
                index = list_of_vials_to_plot_names.index(self.full_vialNum)
                self.parent().parent.flow_plot_window.vials_to_plot[index] = '-'
                self.parent().parent.flow_plot_window.vials_to_plot_names[index] = '-'
    
    def plot_ctrl_btn_toggled(self, checked):
        if checked:
            self.slave_plot_object = self.parent().slave_plot_window
            # Make sure it's already set to debug mode
            if self.read_flow_vals_btn.isChecked() == False:
                self.read_flow_vals_btn.setChecked(True)

            # Tell plot window this vial needs to be plotted
            flag = 0
            for idx in range(len(self.slave_plot_object.vials_to_plot)):
                if self.slave_plot_object.vials_to_plot[idx] == '-':
                    self.slave_plot_object.vials_to_plot[idx] = self
                    self.slave_plot_object.vials_to_plot_names[idx] = self.full_vialNum
                    flag = 1
                    break
            if flag == 0:
                logger.debug('only 4 vials can be plotted at once')

            if self.slave_plot_object.vials_to_plot[0] == '-':
                self.slave_plot_object.vials_to_plot[0] = self
                self.slave_plot_object.vials_to_plot_names[0] = self.full_vialNum
    
    def vial_details_btn_toggled(self, checked):
        if checked: # TODO this often freezes the whole window if done while a program is running 1/11/2024
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
        
        if self.setpoint  != 0:
            self.set_flowrate(self.setpoint)    # update setpoint
    
    def open_vial(self, duration):
        '''
        # calculate how long we need to do the little fake vial open
        # parameters:
        # - tube radius
        # - tube length
        # - flow rate

        tube_radius_inch = 0.03125  # for 1/16" ID tubing
        tube_radius_cm = .079375
        tube_length_cm = 22
        this_setpoint_sccm = self.setpoint
        
        flow_rate_per_second = float(this_setpoint_sccm/60)
        fake_open_duration = (math.pi * (tube_radius_cm*tube_radius_cm) * tube_length_cm) / flow_rate_per_second
        fake_open_duration = round(fake_open_duration,1)
        logger.info('doing fake open for %s seconds', str(fake_open_duration))
        
        # SEND PARAMETERS TO WORKER
        self.obj_fake_open_worker.fake_open_dur = fake_open_duration
        self.obj_fake_open_worker.real_open_dur = duration
        self.obj_fake_open_worker.full_vialNum = self.full_vialNum
        
        # START WORKER THREAD
        self.obj_fake_open_worker.threadON = True
        logger.debug('starting fake worker thread')
        self.thread_fake_open.start()        '''
        
        # Send to olfactometer_window (to send to Arduino)
        strToSend = 'S_OV_' + str(duration) + '_' + self.full_vialNum
        self.olfactometer_parent_object.send_to_master(strToSend)
        logger.info('Opening %s for %s seconds',self.full_vialNum,duration)
        
        # Send to main GUI window (to write to datafile)
        device = 'olfactometer ' + self.full_vialNum
        self.write_to_datafile(device,'OV',str(duration))

        # Start valve timer
        self.start_valve_timer(duration)
    
    def close_vial(self):
        # If the button was toggled before the timer finished: send command to Arduino
        if self.valve_timer.isActive():
            logger.debug('vial ' + self.full_vialNum + ' was closed early')
            self.end_valve_timer()
            
            # Send to olfactometer_window (to send to Arduino)
            strToSend = 'S_CV_' + self.full_vialNum
            self.olfactometer_parent_object.send_to_master(strToSend)
            
            # Send to main GUI window (to write to datafile)
            device = 'olfactometer ' + self.full_vialNum
            self.write_to_datafile(device,'CV','0')
    
    # COMMANDS
    def K_parameter_update(self, Kx, value):
        strToSend = 'S_Kx_' + Kx + str(value) + '_' + self.full_vialNum
        self.olfactometer_parent_object.send_to_master(strToSend)
        logger.info('K parameters updated for %s: %s', self.full_vialNum, strToSend)
    
    def set_flowrate(self, value):
        # Check if out of range
        if (value >= 0) and (value <= int(config_olfa.mfc_capacity)):
            if self.sccmToInt_dict != None:
                # Convert from sccm to integer
                setpoint_sccm = value
                setpoint_integer = utils_olfa_48line.convertToInt(setpoint_sccm, self.sccmToInt_dict)
                logger.info('set ' + self.full_vialNum + ' to ' + str(setpoint_sccm) + ' sccm')
                self.setpoint = setpoint_sccm
                
                # Send to olfactometer_window (to send to Arduino)
                strToSend = 'S_Sp_' + str(setpoint_integer) + '_' + self.full_vialNum
                self.olfactometer_parent_object.send_to_master(strToSend)
                
                # Send to main GUI window (to write to datafile)
                device = 'olfactometer ' + self.full_vialNum
                self.write_to_datafile(device,'Sp',setpoint_integer)
            else:
                msg_box = QMessageBox()
                msg_box.setWindowTitle(self.full_vialNum)
                msg_box.setText('No valid calibration table entered for ' + self.full_vialNum + '\n\n'
                                'Please load calibration tables in order to send setpoints to this MFC')
                msg_box.setStandardButtons(QMessageBox.Ok)
                msg_box.exec()
                self.setpoint_slider.setValue(0)
                self.setpoint_set_lineedit.setText('0')
                self.setpoint_set_lineedit.setPlaceholderText('Set value')
        
        if (value < 0) or (value > int(config_olfa.mfc_capacity)):
            if value > int(config_olfa.mfc_capacity):
                logger.warning(str(value) + ' is greater than mfc capacity: try again')
                if self.sccmToInt_dict != None:
                    # Convert from sccm to integer
                    setpoint_sccm = int(config_olfa.mfc_capacity)
                    setpoint_integer = utils_olfa_48line.convertToInt(setpoint_sccm, self.sccmToInt_dict)
                    logger.info('Set ' + self.full_vialNum + ' to ' + str(setpoint_sccm) + ' sccm')
                    self.setpoint = setpoint_sccm
                    # TODO replace the text entered in the box

                    # Send to olfactometer_window (to send to Arduino)
                    strToSend = 'S_Sp_' + str(setpoint_integer) + '_' + self.full_vialNum
                    self.olfactometer_parent_object.send_to_master(strToSend)

                    # Send to main GUI window (to write to datafile)
                    device = 'olfactometer ' + self.full_vialNum
                    self.write_to_datafile(device,'Sp',setpoint_integer)
            
            if value < 0:
                logger.warning('cannot enter negative flow rate: try again')        
    
    def readFlow_btn_toggled(self, btn_to_check):
        if btn_to_check.isChecked():
            btn_to_check.setText("Stop reading ")
            btn_to_check.setToolTip('Stop reading flow values')
            strToSend = 'MS_debug_' + self.full_vialNum
            self.olfactometer_parent_object.send_to_master(strToSend)
            '''
            if self.read_flow_vals_btn.isChecked() == False:
                self.read_flow_vals_btn.setChecked(True)
            if self.vial_details_window.db_readflow_btn.isChecked() == False:
                self.vial_details_window.db_readflow_btn.setChecked(True)
            '''
            
        else:
            btn_to_check.setText("Read flow")
            btn_to_check.setToolTip('Start reading flow values')
            strToSend = 'MS_' + self.full_vialNum
            self.olfactometer_parent_object.send_to_master(strToSend)
            '''
            if self.read_flow_vals_btn.isChecked() == True:
                self.read_flow_vals_btn.setChecked(False)
            if self.vial_details_window.db_readflow_btn.isChecked() == True:
                self.vial_details_window.db_readflow_btn.setChecked(False)
            '''
            
    def vial_open_toggled(self, checked):
        if checked:
            self.valve_open_btn.setText('Close ' + self.full_vialNum)
            self.vial_details_window.db_valve_open_btn.setText('Close vial')
            self.open_vial(self.valve_dur_spinbox.value())
        else:
            self.valve_open_btn.setText('Open ' + self.full_vialNum)
            self.vial_details_window.db_valve_open_btn.setText('Open vial')
            self.close_vial()
    
    def write_to_datafile(self,device,unit,value):
        try:
            self.olfactometer_parent_object.window().receive_data_from_device(device,unit,value)
        except AttributeError:
            pass    # main window not open
    
    # VALVE TIMER
    def start_valve_timer(self, duration):
        self.time_valve_opened_at = datetime.now()
        self.timedelta_valve_open_full_dur = timedelta(0,int(duration))
        self.valve_timer.start()
    
    def show_valve_time(self):
        time_current_time = datetime.now()
        timedelta_current_valve_dur = time_current_time - self.time_valve_opened_at
        if timedelta_current_valve_dur >= self.timedelta_valve_open_full_dur:
            self.end_valve_timer()
        valve_dur_display_value = str(timedelta_current_valve_dur)
        valve_dur_display_value = valve_dur_display_value[5:]   # Remove hour/minute display
        valve_dur_display_value = valve_dur_display_value[:-3]  # Remove extra decimal point display
        self.valveTimer_duration_label.setText(valve_dur_display_value)
        self.vial_details_window.valveTimer_duration_label.setText(valve_dur_display_value)
    
    def end_valve_timer(self):
        self.valve_timer.stop()
        
        # Check which button to untoggle
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
        # TODO add a way to apply commands to multiple vials at once (ex: check the ones you want to apply this setpoint to)
        
        self.slave_address_label = QLabel(text='Slave address:')    # TODO slave address dictionary :/ where should it be located
        self.temp_label = QLabel("...,...,.slave active or not, slave info, whatever.,...")
        
        self.slaveInfo_layout = QVBoxLayout()
        #self.slaveInfo_layout.addWidget(self.slave_address_label)
        self.slaveInfo_layout.addWidget(self.temp_label)
    
    def create_vials_box(self):
        self.vials = []
        for v in range(config_olfa.vialsPerSlave):
            v_vialNum = str(v+1)
            v_vial = Vial(parent=self, vialNum=v_vialNum)
            self.vials.append(v_vial)

        self.vials_layout = QHBoxLayout()
        for v in range(config_olfa.vialsPerSlave):
            self.vials_layout.addWidget(self.vials[v])


class olfactometer_window(QGroupBox):
    
    def __init__(self):
        super().__init__()
        self.sccm2Ard_dicts = {}
        self.ard2Sccm_dicts = {}
        self.active_slaves = []
        self.def_timebt = config_olfa.def_timebt
        self.vialsPerSlave = config_olfa.vialsPerSlave
        
        # look for calibration table directory
        self.flow_cal_dir = utils.find_calibration_table_directory()
        if os.path.exists(self.flow_cal_dir):
            self.get_calibration_tables()
        else:
            logger.error('Could not find flow calibration directory (searched \'%s\')', self.flow_cal_dir)
            self.flow_cal_dir = ''
        
        self.generate_ui()
        
        self.master_groupbox.setEnabled(False)
        self.setTitle('Olfactometer')
    
    def get_calibration_tables(self):
        logger.debug('loading flow sensor calibration tables from (%s)', self.flow_cal_dir)
        
        # Get names of all .txt files in flow cal directory
        cal_file_names = os.listdir(self.flow_cal_dir)
        cal_file_names = [fn for fn in cal_file_names if fn.endswith(config_olfa.cal_table_file_tyoe)]    # only txt files # TODO: change to csv
        
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
                        except TypeError:
                            pass
                        except KeyError as err:
                            # Clear dictionaries & stop trying to read this file
                            logger.error('got a KeyError: %s',err)
                            logger.error('%s does not have correct headings for calibration files', cal_file)
                            thisfile_sccm2Ard_dict = {}
                            thisfile_ard2Sccm_dict = {}
                            break
                        except ValueError as err:
                            # Clear dictionaries & stop trying to read this file
                            logger.debug('missing some values, skipping calibration file %s', cal_file)
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
                logger.warning('no calibration files found in this directory')
        
        else:
            # If flow cal directory does not exist: print warning --> this is big issue if none found
            # TODO some kind of error message if there are no calibration tables. or disable all the slave devices or something, bc you won't be able to send setpoints
            logger.warning('no .txt files found in this directory :/')    
    
    def generate_ui(self):
        self.create_connect_box()
        self.create_master_groupbox()
        self.create_slave_groupbox()
        self.create_settings_groupbox()
        self.create_raw_comm_groupbox()
        
        mainLayout = QGridLayout()
        self.setLayout(mainLayout)
        mainLayout.addWidget(self.connect_box,          0,0,1,1)      # row, column, rowSpan, columnSpan
        mainLayout.addWidget(self.master_groupbox,      1,0,1,1)
        mainLayout.addWidget(self.settings_groupbox,    0,1,2,1)
        mainLayout.addWidget(self.raw_comm_box,         0,2,2,1)
        mainLayout.addWidget(self.slave_groupbox,       2,0,1,3)
        
        col1_max_width = self.connect_box.sizeHint().width()
        self.connect_box.setFixedWidth(col1_max_width)
        self.master_groupbox.setFixedWidth(col1_max_width)
        
        self.connect_box.setFixedHeight(self.connect_box.sizeHint().height())
        self.master_groupbox.setFixedHeight(self.master_groupbox.sizeHint().height())
        self.raw_comm_box.setMaximumHeight(self.raw_comm_box.sizeHint().height())
        self.slave_groupbox.setMinimumWidth(self.slave_widget.size().width() + 56)  # this is the exact size for the scroll area to have no horizontal anything
        
    def create_connect_box(self):
        self.connect_box = QGroupBox("Connect to master Arduino")
        self.port_widget = QComboBox(currentIndexChanged=self.port_changed)
        self.connect_btn = QPushButton(checkable=True,toggled=self.toggled_connect)
        self.refresh_btn = QPushButton(text="Refresh",clicked=self.get_ports,toolTip='Refresh list of available COM ports')
        self.get_ports()
        connect_box_layout = QHBoxLayout()
        connect_box_layout.addWidget(QLabel(text='Select Port:',toolTip='Select COM port for master Arduino'))
        connect_box_layout.addWidget(self.port_widget)
        connect_box_layout.addWidget(self.connect_btn)
        connect_box_layout.addWidget(self.refresh_btn)
        self.connect_box.setLayout(connect_box_layout)

    def create_master_groupbox(self):
        self.master_groupbox = QGroupBox('Master Settings')

        self.m_check_addr_btn = QPushButton(text="Get Slave Addresses")
        self.m_check_addr_btn.clicked.connect(self.get_slave_addresses)

        self.m_mode_lbl = QLabel("Logging:")
        self.m_mode_wid = QComboBox()
        self.m_mode_wid.addItems(config_olfa.master_modes)
        self.m_mode_wid.setCurrentIndex(2)  # matches master Arduino default level (4: notice)
        self.m_mode_btn = QPushButton(text="Send")
        self.m_mode_lbl.setToolTip("Master Arduino logging level")
        self.m_mode_wid.setToolTip("Master Arduino logging level")
        self.m_mode_btn.clicked.connect(lambda: self.send_master_mode(self.m_mode_wid.currentText()))
        m_mode_layout = QHBoxLayout()
        m_mode_layout.addWidget(self.m_check_addr_btn)
        m_mode_layout.addWidget(self.m_mode_lbl)
        m_mode_layout.addWidget(self.m_mode_wid)
        m_mode_layout.addWidget(self.m_mode_btn)

        self.m_timebtreqs_lbl = QLabel("Time b/t reqs (ms):")
        self.m_timebtreqs_wid = QLineEdit(text=self.def_timebt)
        self.m_timebtreqs_btn = QPushButton(text="Send")
        self.m_timebtreqs_lbl.setToolTip("Duration between requests to slave Arduinos \n(i.e. how frequently to ask for flow values)")
        self.m_timebtreqs_wid.setToolTip("Duration between requests to slave Arduinos \n(i.e. how frequently to ask for flow values)")
        self.m_timebtreqs_wid.returnPressed.connect(lambda: self.send_to_master('MM_timebt_' + self.m_timebtreqs_wid.text()))
        self.m_timebtreqs_btn.clicked.connect(lambda: self.send_to_master('MM_timebt_' + self.m_timebtreqs_wid.text()))
        timebt_layout = QHBoxLayout()
        timebt_layout.addWidget(self.m_timebtreqs_lbl)
        timebt_layout.addWidget(self.m_timebtreqs_wid)
        timebt_layout.addWidget(self.m_timebtreqs_btn)

        self.m_manualcmd_lbl = QLabel("Manual:")
        self.m_manualcmd_wid = QLineEdit(text=config_olfa.def_manual_cmd)
        self.m_manualcmd_btn = QPushButton(text="Send")
        self.m_manualcmd_lbl.setToolTip("Manually send command to master Arduino")
        self.m_manualcmd_wid.setToolTip("Manually send command to master Arduino")
        self.m_manualcmd_wid.returnPressed.connect(lambda: self.send_to_master(self.m_manualcmd_wid.text()))
        self.m_manualcmd_btn.clicked.connect(lambda: self.send_to_master(self.m_manualcmd_wid.text()))
        manualcmd_layout = QHBoxLayout()
        manualcmd_layout.addWidget(self.m_manualcmd_lbl)
        manualcmd_layout.addWidget(self.m_manualcmd_wid)
        manualcmd_layout.addWidget(self.m_manualcmd_btn)
        
        layout = QVBoxLayout()
        layout.addLayout(m_mode_layout)
        layout.addLayout(timebt_layout)
        layout.addLayout(manualcmd_layout)
        self.master_groupbox.setLayout(layout)
        
    def create_settings_groupbox(self):
        self.settings_groupbox = QGroupBox('Other Settings')
        
        # Select config file
        self.load_config_btn = QPushButton('Load olfa config',checkable=True)
        self.load_config_btn.setToolTip('Load olfa config file containing calibration tables')
        self.load_config_btn.toggled.connect(self.load_config_btn_toggled)
        
        # Select directory where flow calibration tables are stored
        self.flow_cal_dir_btn = QPushButton('Select Calibration Table Directory',checkable=True)
        self.flow_cal_dir_btn.setToolTip('Select directory for flow calibration tables')
        self.flow_cal_dir_btn.toggled.connect(self.flow_cal_dir_btn_toggled)
        
        # Show flow plot
        self.show_flow_plot_btn = QPushButton('Show flow plot', checkable=True)
        self.show_flow_plot_btn.toggled.connect(self.show_flow_plot_toggled)
        self.flow_plot_window = plot_widget.plot_window_all(self)
        self.flow_plot_window.hide()

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.load_config_btn)
        layout.addWidget(self.flow_cal_dir_btn)
        layout.addWidget(self.show_flow_plot_btn)
        self.settings_groupbox.setLayout(layout)

    def show_flow_plot_toggled(self, checked):
        if checked:
            #logger.debug('show flow plot toggled')
            self.show_flow_plot_btn.setText('Hide flow plot')
            self.flow_plot_window.update_vial_select_groupbox()
            self.flow_plot_window.show()
            self.flow_plot_window.timer_start()

        else:
            self.show_flow_plot_btn.setText('Show flow plot')
            self.flow_plot_window.hide()

    def flow_cal_dir_btn_toggled(self,checked): # TODO finish debugging/cleaning this up
        if checked:
            dlg = QFileDialog()
            dlg.setFileMode(QFileDialog.Directory)
            if dlg.exec_():
                directory_selected = dlg.selectedFiles()
                # now get all the files in this directory
                self.flow_cal_dir = directory_selected[0]
                self.get_calibration_tables()
                self.flow_cal_dir_btn.setChecked(False)

        else:
            pass
    
    def load_config_btn_toggled(self,checked):  # TODO load a default one at the beginning
        if checked:
            dlg = QFileDialog()
            dlg.setFileMode(QFileDialog.ExistingFile)   # The name of a single existing file
            if dlg.exec_():
                
                # load the config file
                file_selected = dlg.selectedFiles()
                self.config_file_dir = file_selected[0]
                with open(self.config_file_dir) as f:
                    self.config_obj = json.load(f)   # dict
                self.config_olfa = self.config_obj['Olfactometers']     # list
                self.config_olfa = self.config_olfa[0]                  # dict
                self.config_cal_tables = self.config_obj['Calibration tables']  # dict
                
                # update vial calibration tables
                for s in self.slave_objects:
                    for v in s.vials:
                        vial_name = v.full_vialNum
                        if vial_name in self.config_cal_tables:
                            cal_table = self.config_cal_tables.get(vial_name)
                            wid = v.vial_details_window.db_cal_table_combobox
                            cal_table_options_list = [wid.itemText(i) for i in range(wid.count())]
                            if cal_table in cal_table_options_list:
                                v.cal_table = cal_table
                                v.vial_details_window.db_cal_table_combobox.setCurrentText(v.cal_table)
                            else:
                                logger.debug('config file has an invalid cal table: %s', cal_table)
            
            self.load_config_btn.setChecked(False)
    
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
        for s in config_olfa.slave_names:
            new_slave_object = slave_8vials(parent=self,name=s)
            self.slave_objects.append(new_slave_object)
        
        # Add slave objects to layout
        self.slave_layout = QVBoxLayout()
        for s in self.slave_objects:
            self.slave_layout.addWidget(s)
            s.setEnabled(False)
        
        self.slave_widget = QWidget()                           # Widget to put into QScrollArea
        self.slave_widget.setLayout(self.slave_layout)
        self.slave_scrollArea = QScrollArea()
        self.slave_scrollArea.setWidget(self.slave_widget)
        self.nothing_layout = QHBoxLayout()                     # Layout for putting QScrollArea into self.slave_groupbox
        self.nothing_layout.addWidget(self.slave_scrollArea)
        self.slave_groupbox.setLayout(self.nothing_layout)
    
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
            self.port_widget.addItem(config_olfa.noPort_msg)
        
        # Set toolTip for each item
        for port_list_idx in range(0,self.port_widget.count()):
            this_port = self.port_widget.itemText(port_list_idx)
            self.port_widget.setItemData(port_list_idx,this_port,QtCore.Qt.ToolTipRole)
        
        # If an Arduino is connected, set the widget default value to that
        for port_list_idx in range(0,self.port_widget.count()):
            this_port = self.port_widget.itemText(port_list_idx)
            if 'Arduino' in this_port:
                self.port_widget.setCurrentIndex(port_list_idx)
                break
    
    def port_changed(self):
        if self.port_widget.count() != 0:
            self.port = self.port_widget.currentText()
            if self.port == config_olfa.noPort_msg:
                self.connect_btn.setEnabled(False)
                self.connect_btn.setText(config_olfa.noPort_msg)
            else:
                self.portStr = self.port[:self.port.index(':')]
                self.connect_btn.setEnabled(True)
                self.connect_btn.setText("Connect")
                self.connect_btn.setToolTip("Connect to " + self.portStr)
    
    def toggled_connect(self, checked):
        if checked:
            i = self.port.index(':')
            self.comPort = self.port[:i]
            self.serial = QtSerialPort.QSerialPort(self.comPort,baudRate=config_olfa.baudrate,readyRead=self.receive)
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
            self.refresh_btn.setEnabled(False)
            self.port_widget.setEnabled(False)
        
        else:
            logger.info('disconnected from ' + self.port_widget.currentText())
            self.master_groupbox.setEnabled(False)
            self.connect_btn.setText("Connect")
            self.connect_btn.setChecked(False)
            self.refresh_btn.setEnabled(True)
            self.port_widget.setEnabled(True)
    
    def get_slave_addresses(self):
        self.prev_active_slaves = copy.copy(self.active_slaves)
        self.active_slaves = []
        logger.debug('Checking slave addresses')
        self.send_to_master('C')
    
    def send_master_mode(self, newMode):
        if newMode == config_olfa.master_modes[0]:  mode_value = 6
        if newMode == config_olfa.master_modes[1]:  mode_value = 5
        if newMode == config_olfa.master_modes[2]:  mode_value = 4
        if newMode == config_olfa.master_modes[3]:  mode_value = 3
        if newMode == config_olfa.master_modes[4]:  mode_value = 2
        if newMode == config_olfa.master_modes[5]:  mode_value = 1
        
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
                    # Enable groupbox for this slave & add the address
                    for s in self.slave_objects:
                        if s.name == slave_name_received:
                            s.setEnabled(True)
                            address_label = 'Slave Address: {}'.format(slave_address)
                            s.slave_address_label.setText(address_label)
                    
                    # If program selected reads "no active slaves" --> update the combobox
                    try:
                        if self.window().p_slave_select_wid.currentText() == 'no active slaves pls connect olfa or something':
                            self.window().active_slave_refresh()
                    except AttributeError:  # if no main window
                        pass

                        
                # IF FLOW UPDATE WAS SENT: Send to main GUI window (to write to datafile)
                if len(text) == 17:
                    text = text[3:]     # Remove arduino logging info
                    
                    # Split up for writing to datafile
                    slave_vial = text[0:2]  # 'A1'
                    flowVal = text[2:6]     # '0148'
                    ctrlVal = text[6:10]    # '0255'

                    # Send flow value to main GUI
                    device = 'olfactometer ' + slave_vial
                    unit = 'FL'
                    value = flowVal
                    try:
                        self.window().receive_data_from_device(device,unit,value)
                    except AttributeError as err:   # if main window is not open
                        pass

                    # Send ctrl value to main GUI
                    unit = 'Ctrl'
                    value = ctrlVal
                    try:
                        self.window().receive_data_from_device(device,unit,value)
                    except AttributeError as err:   # if main window is not open
                        pass

                    
                    # Write it to the vial details box
                    for s in self.slave_objects:    # find out which vial this is
                        for v in s.vials:
                            if v.full_vialNum == slave_vial:
                                if v.intToSccm_dict != None:
                                    # Convert to sccm
                                    flowVal_raw = int(flowVal)
                                    flowVal_sccm = utils_olfa_48line.convertToSCCM(flowVal_raw,v.intToSccm_dict)
                                    
                                    # Write it to the vial details box
                                    flowVal_sccm_str = str(flowVal_sccm)
                                    if len(str(flowVal_sccm)) < 5:
                                        if len(str(flowVal_sccm)) == 4: flowVal_sccm_str = '0' + str(flowVal_sccm)
                                        if len(str(flowVal_sccm)) == 3: flowVal_sccm_str = '00' + str(flowVal_sccm)
                                    dataStr = str(flowVal) + '\t' + flowVal_sccm_str + '\t' + str(ctrlVal)
                                    v.vial_details_window.data_receive_box.append(dataStr)
                                    
                                    # Write it to the setpoint read widget
                                    v.setpoint_read_widget.display(round(flowVal_sccm))
                                    
                                    # Write it to the setpoint read widget (in the vial details box)
                                    v.vial_details_window.setpoint_read_widget.display(round(flowVal_sccm))
                                    
                                    # If calibration is on: write it to the vial details popup
                                    if v.vial_details_window.calibration_on == True:
                                        # Append it to the current list of values
                                        v.vial_details_window.serial_values.append(int(flowVal))
                                        v.vial_details_window.collected_values_window.append(str(flowVal))

                                    # Write it to the vial object
                                    v.flow_value_int = flowVal_raw
                                    v.flow_value_sccm = flowVal_sccm
                                    v.ctrl_value_int = ctrlVal
                                
                                else:
                                    # stop reading flow
                                    logger.debug('no longer reading flow from %s', v.full_vialNum)
                                    if v.read_flow_vals_btn.isChecked(): v.read_flow_vals_btn.setChecked(False)
                                    
                                    msg_box = QMessageBox()
                                    msg_box.setWindowTitle(v.full_vialNum)
                                    msg_box.setText('No valid calibration table entered for ' + v.full_vialNum + '\n\n'
                                                    'Please load calibration tables in order to read flow value')
                                    msg_box.setStandardButtons(QMessageBox.Ok)
                                    msg_box.exec()
            
            except UnicodeDecodeError:
                logger.warning("Serial read error")

    def send_to_master(self, strToSend):
        bArr_send = strToSend.encode()
        try:
            if self.serial.isOpen():
                self.serial.write(bArr_send)                # Send to Arduino
                self.raw_write_display.append(strToSend)    # Display string that was sent
            else:
                logger.warning('Serial port not open, cannot send parameter: %s', strToSend)
        except AttributeError as err:
            logger.warning('(Attribute Error) Serial port not open, cannot send parameter: %s', strToSend)


if __name__ == "__main__":
    app1 = QApplication(sys.argv)
    theWindow = olfactometer_window()
    theWindow.show()
    theWindow.setWindowTitle('48-line olfactometer')
    sys.exit(app1.exec_())