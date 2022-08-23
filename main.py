#!/usr/bin/env python
from gc import isenabled
import sys, os, logging, csv
from numpy import full
import numpy.matlib as np
import random, time
import copy

from PyQt5 import sip
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot, QTimer

import utils
import olfa_driver_48line
import NiDAQ_driver
import olfa_driver_original
import flow_sensor_driver
import olfa_original_procedures
#import programs_48lineolfa
import utils_olfa_48line


programs_48line = ['setpoint characterization','additive']
programs_orig = ['the program']


# PARAMETERS FOR 48-LINE OLFACTOMETER
vials = ['1','2','3','4','5','6','7','8']
#default_setpoint = '10,20,30,40,50,60,70,80,90,100'
default_setpoint = '10,20,30,40,50'
default_dur_ON = 5
default_dur_OFF = 5
default_numTrials = 5
no_active_slaves_warning = 'no active slaves pls connect olfa or something'
waitBtSpAndOV = .5
default_pid_gain = '10x'

current_date = utils.currentDate

# LOGGING
main_datafile_directory = utils.find_datafile_directory()
if not os.path.exists(main_datafile_directory): os.mkdir(main_datafile_directory)   # if folder doesn't exist, make it
logger = logging.getLogger(name='main')
logger.setLevel(logging.DEBUG)
if logger.hasHandlers():    logger.handlers.clear()     # removes duplicate log messages
console_handler = utils.create_console_handler()
file_handler = utils.create_file_handler(main_datafile_directory)
logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.debug('log file located at: %s', main_datafile_directory)



class worker_sptChar(QObject):
    finished = pyqtSignal()
    w_sendThisSp = pyqtSignal(str,int)
    w_send_OpenValve = pyqtSignal(str,int)
    w_incProgBar = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setpoint = 0
        self.threadON = False
        self.complete_stimulus_list = []

        self.duration_on = 5
        self.duration_off = 5
        self.sccm2Ard_dict = []
        self.ard2Sccm_dict = []
    
    @pyqtSlot()
    def exp(self):
        # wait so olfa has time to set vial to debug mode
        time.sleep(waitBtSpAndOV)
        time.sleep(waitBtSpAndOV)

        # do an off duration so we have a better baseline
        time.sleep(self.duration_off)
        
        # iterate through stimulus list
        for stimulus in self.complete_stimulus_list:
            if self.threadON == True:
                full_vial_name = stimulus[0]
                this_setpoint_sccm = stimulus[1]

                # convert it to arduino integer
                this_setpoint_int = utils_olfa_48line.convertToInt(this_setpoint_sccm,self.sccm2Ard_dict)
                
                # send the setpoint
                logger.info('%s set to %s sccm',full_vial_name,this_setpoint_sccm)
                self.w_sendThisSp.emit(full_vial_name,this_setpoint_int)
                time.sleep(waitBtSpAndOV)
                
                # open the vial
                logger.info('Opening %s (%s seconds)',full_vial_name,self.duration_on)
                self.w_send_OpenValve.emit(full_vial_name,self.duration_on)
                
                # wait until the vial closes
                time.sleep(self.duration_on)

                # wait for the time between trials
                time.sleep(self.duration_off)

        self.finished.emit()

class mainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.generate_ui()
        self.set_up_threads_sptchar()
        
        self.mainLayout = QHBoxLayout()
        self.mainLayout.addWidget(self.settings_box)
        self.mainLayout.addWidget(self.device_groupbox)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.mainLayout)
        self.setCentralWidget(self.central_widget)
        self.setWindowTitle('8-line Olfa PID Testing')
    
    def generate_ui(self):
        # SETTINGS GROUPBOX
        self.settings_box = QGroupBox('Settings')
        self.create_general_settings_box()
        self.create_add_devices_box()
        self.create_program_selection_groupbox()
        self.create_program_parameters_box()
        self.program_parameters_box.setEnabled(False)
        self.create_datafile_box()
        self.settings_layout = QGridLayout()
        self.settings_layout.addWidget(self.general_settings_box,0,0,1,1)
        self.settings_layout.addWidget(self.add_devices_groupbox,0,1,1,1)
        self.settings_layout.addWidget(self.program_selection_groupbox,1,0,1,2)
        self.settings_layout.addWidget(self.program_parameters_box,2,0,1,2)
        self.settings_layout.addWidget(self.datafile_groupbox,3,0,1,2)
        self.settings_box.setLayout(self.settings_layout)
        self.settings_box.setFixedWidth(self.settings_box.sizeHint().width() - 50)

        # DEVICES GROUPBOX
        self.device_groupbox = QGroupBox('Devices:')
        self.device_layout = QVBoxLayout()
        self.device_groupbox.setLayout(self.device_layout)

        w = self.datafile_groupbox.sizeHint().width()
        self.datafile_groupbox.setFixedWidth(w + 15)
        self.settings_box.setMinimumWidth(w+5)
    
    def create_general_settings_box(self):
        self.general_settings_box = QGroupBox('General Settings')

        # get location of log file (from logger)
        self.log_file_dir = ''
        for r in logger.handlers:
            this_handler_type = type(r).__name__
            if this_handler_type == 'FileHandler': self.log_file_dir = r.baseFilename
        if self.log_file_dir == '': logger.warning('not logging to any file')
        # shorten directory for readability
        strToFind = 'OlfactometerEngineeringGroup'          # TODO: move this to utils
        beginning_idx = self.log_file_dir.find(strToFind)
        self.log_file_dir = self.log_file_dir[beginning_idx:]
        slash_idx = self.log_file_dir.find('\\')
        self.log_file_dir = self.log_file_dir[slash_idx:]
        self.log_file_dir = '..' + self.log_file_dir
        self.log_file_dir_label = QLineEdit(text=self.log_file_dir,readOnly=True)
        self.log_file_dir_label.setToolTip('edit in header of main.py (if you need to change this)')
        
        self.log_text_edit = QTextEdit(readOnly=True)   # TODO: put log messages here
        self.log_text_edit.setToolTip('not set up yet sry')
        self.log_text_edit.setMaximumHeight(65)
        self.log_clear_btn = QPushButton(text='Clear')
        self.log_clear_btn.clicked.connect(lambda: self.log_text_edit.clear())
        '''
        log_box_layout = QGridLayout()
        log_box_layout.addWidget(QLabel('Log messages:'),0,0,1,1)
        log_box_layout.addWidget(self.log_clear_btn,0,2,1,1)
        log_box_layout.addWidget(self.log_text_edit,1,0,1,3)
        '''
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel('Log file location:'))
        layout.addWidget(self.log_file_dir_label)
        '''
        layout.addWidget(QLabel('\n'))
        layout.addLayout(log_box_layout)
        '''
        self.general_settings_box.setLayout(layout)
        max_height = self.general_settings_box.sizeHint().height()
        self.general_settings_box.setMaximumHeight(max_height)
    
    def create_datafile_box(self):
        self.datafile_groupbox = QGroupBox('Data file')

        # get today's file directory
        self.today_resultfiles_dir = main_datafile_directory + '\\' + current_date
        '''
        # TODO does this need to be here? or should these be when we start recording to a file
        # if this directory does not exist:
        if not os.path.exists(self.today_resultfiles_dir):
            os.mkdir(self.today_resultfiles_dir)
        '''
        
        # if this directory exists: get number of last datafile in it
        if os.path.exists(self.today_resultfiles_dir):
            # check what files are in this folder
            list_of_files = os.listdir(self.today_resultfiles_dir)
            list_of_files = [x for x in list_of_files if '.csv' in x]   # only get csv files
            if not list_of_files:
                self.last_datafile_number = -1  # if there are no files
            else:
                # find the number of the last data file
                last_datafile = list_of_files[len(list_of_files)-1]
                idx_fileExt = last_datafile.rfind('.')
                last_datafile = last_datafile[:idx_fileExt] # remove file extension
                idx_underscore = last_datafile.rfind('_')   # find last underscore
                last_datafile_num = last_datafile[idx_underscore+1:]
                if last_datafile_num.isnumeric():   # if what's after the underscore is a number
                    self.last_datafile_number = int(last_datafile_num)
                else:
                    self.last_datafile_number = 98  # if the last file doesn't have a number
                    logger.warning('last datafile in this folder is %s',last_datafile)
        # if this directory does not exist
        else:
            self.last_datafile_number = -1
        
        # create data file name
        self.this_datafile_number = self.last_datafile_number + 1
        self.this_datafile_number_padded = str(self.this_datafile_number).zfill(2) # zero pad
        data_file_name = current_date + '_datafile_' + self.this_datafile_number_padded
        
        # GUI FEATURES
        self.data_file_name_lineEdit = QLineEdit(text=data_file_name)
        self.data_file_textedit = QTextEdit(readOnly=True)
        self.data_file_dir_lineEdit = QLineEdit(text=self.today_resultfiles_dir,readOnly=True)
        self.begin_record_btn = QPushButton(text='Create File && Begin Recording',checkable=True,clicked=self.begin_record_btn_clicked)
        self.end_record_btn = QPushButton(text='End Recording',checkable=True,clicked=self.end_recording)
        self.end_record_btn.setEnabled(False)
        record_layout = QHBoxLayout()
        record_layout.addWidget(self.begin_record_btn)
        record_layout.addWidget(self.end_record_btn)
        
        # LAYOUT
        layout = QFormLayout()
        layout.addRow(QLabel('Directory:'),self.data_file_dir_lineEdit)
        layout.addRow(QLabel('File Name:'),self.data_file_name_lineEdit)
        layout.addRow(record_layout)
        layout.addRow(self.data_file_textedit)
        self.datafile_groupbox.setLayout(layout)
    
    def create_add_devices_box(self):
        self.add_devices_groupbox = QGroupBox("Add/Remove Devices")

        self.add_olfa_48line_btn = QPushButton(text='Add Olfactometer\n(48-line)',checkable=True,toggled=self.add_olfa_48line_toggled)
        self.add_pid_btn = QPushButton(text='Add PID',checkable=True,toggled=self.add_pid_toggled)
        self.add_olfa_orig_btn = QPushButton(text='Add Olfactometer\n(original)',checkable=True,toggled=self.add_olfa_orig_toggled)
        self.add_flow_sens_btn = QPushButton(text='Add\nHoneywell 5100V',checkable=True,toggled=self.add_flow_sens_toggled)
        
        layout = QVBoxLayout()
        layout.addWidget(self.add_pid_btn)
        layout.addWidget(self.add_flow_sens_btn)
        layout.addWidget(self.add_olfa_48line_btn)
        layout.addWidget(self.add_olfa_orig_btn)
        self.add_devices_groupbox.setLayout(layout)
    
    def create_program_widgets(self):
        if self.program_selection_btn.isChecked():
            self.program_parameters_box.setEnabled(True)
            self.program_to_run = self.program_selection_combo.currentText()
            
            if self.program_to_run == "the program":
                self.pid_record_time_widget = QSpinBox(value=5)
                self.vial_open_time_widget = QSpinBox(value=5)
                self.num_repetitions_widget = QSpinBox(value=10)

                self.program_parameters_layout.insertRow(0,QLabel('pid record time:'),self.pid_record_time_widget)
                self.program_parameters_layout.insertRow(1,QLabel('vial open time:'),self.vial_open_time_widget)
                self.program_parameters_layout.insertRow(2,QLabel('number of repetitions:'),self.num_repetitions_widget)
                self.program_parameters_layout.addWidget(self.program_start_btn)

            if self.program_to_run == "setpoint characterization":
                self.create_48line_program_widgets()
                '''
                #logger.debug('setpoint characterization selected')
                #programs_48lineolfa.create_sptchar_parameter_widgets(self.program_parameters_box)
                '''
        
        else:
            logger.warning('program selection unchecked: remove program widgets')
            self.program_parameters_box.setEnabled(False)
    
    def create_program_selection_groupbox(self):
        self.program_selection_groupbox = QGroupBox('Program Selection')
        
        self.olfa_type_label = QLabel()
        self.program_selection_combo = QComboBox()
        self.program_selection_combo.addItems(programs_48line)
        self.program_selection_btn = QPushButton(text='Select',checkable=True,toggled=self.create_program_widgets)
        
        layout = QFormLayout()
        layout.addRow(QLabel('Olfactometer type:'),self.olfa_type_label)
        layout.addRow(self.program_selection_combo,self.program_selection_btn)
        self.program_selection_groupbox.setLayout(layout)
        self.program_selection_groupbox.setEnabled(False)

    def create_program_parameters_box(self):
        self.program_parameters_box = QGroupBox('Program Parameters')

        self.program_start_btn = QPushButton(text='Start',checkable=True,toggled=self.program_start_clicked)
        #self.program_start_btn.setEnabled(False)
        
        self.program_parameters_layout = QFormLayout()
        self.program_parameters_box.setLayout(self.program_parameters_layout)
    
    def create_48line_program_widgets(self):
        if self.program_to_run == "setpoint characterization":
            logger.debug('setpoint characterization selected')

            self.p_slave_select_wid = QComboBox()
            self.p_slave_select_wid.setToolTip('Only active slaves displayed')
            if self.olfactometer.active_slaves == []:
                self.p_slave_select_wid.addItem(no_active_slaves_warning)
            else:
                self.p_slave_select_wid.addItems(self.olfactometer.active_slaves)
            self.p_slave_select_refresh = QPushButton(text="Check Slave")
            self.p_slave_select_refresh.clicked.connect(self.active_slave_refresh)
            self.p_vial_wid = QComboBox()
            self.p_vial_wid.addItems(vials) # TODO: change this
            
            self.p_vial_select_layout = QHBoxLayout()
            self.p_vial_select_layout.addWidget(self.p_slave_select_refresh)
            self.p_vial_select_layout.addWidget(QLabel('Slave:'))
            self.p_vial_select_layout.addWidget(self.p_slave_select_wid)
            self.p_vial_select_layout.addWidget(QLabel('vial:'))
            self.p_vial_select_layout.addWidget(self.p_vial_wid)
            self.active_slave_refresh()
            
            self.p_setpoints_wid = QLineEdit()
            self.p_setpoints_wid.setPlaceholderText('Setpoints to run (sccm)')
            self.p_setpoints_wid.setText(default_setpoint)
            self.p_sp_order_wid = QComboBox()
            self.p_sp_order_wid.addItems(['Sequential','Random'])
            
            self.p_spt_layout = QHBoxLayout()
            self.p_spt_layout.addWidget(QLabel('Setpoints (sccm):'))
            self.p_spt_layout.addWidget(self.p_setpoints_wid)
            self.p_spt_layout.addWidget(self.p_sp_order_wid)

            self.p_dur_on_wid = QSpinBox(value=default_dur_ON)
            self.p_dur_off_wid = QSpinBox(value=default_dur_OFF)
            self.p_numTrials_wid = QLineEdit()
            self.p_numTrials_wid.setPlaceholderText('# of Trials at each setpoint')
            self.p_numTrials_wid.setText(str(default_numTrials))
            
            self.p_dur_layout = QHBoxLayout()
            self.p_dur_layout.addWidget(QLabel('Dur. on (s):'))
            self.p_dur_layout.addWidget(self.p_dur_on_wid)
            self.p_dur_layout.addWidget(QLabel('Dur. off (s):'))
            self.p_dur_layout.addWidget(self.p_dur_off_wid)
            self.p_dur_layout.addWidget(QLabel('# trials:'))
            self.p_dur_layout.addWidget(self.p_numTrials_wid)

            self.p_pid_gain = QLineEdit(text=default_pid_gain)
            
            
            if self.program_parameters_layout.count() > 0:  # TODO
                # clear this shit
                logger.warning('gotta clear these widgets out')
                '''
                for w in range(0,self.program_parameters_layout.count()):
                    self.program_parameters_layout.removeItem(self.program_parameters_layout.itemAt(w))
                    sip.delete(self.program_parameters_layout.itemAt(w))
                '''
                
            self.program_parameters_layout.addRow(self.p_vial_select_layout)
            self.program_parameters_layout.addRow(self.p_spt_layout)
            self.program_parameters_layout.addRow(self.p_dur_layout)
            self.program_parameters_layout.addRow(QLabel('PID gain:'),self.p_pid_gain)
            self.program_parameters_layout.addRow(self.program_start_btn)

            # change datafile name
            olfa_48line_results_dir = main_datafile_directory + '\\48-line olfa' + '\\' + current_date
            if not os.path.exists(olfa_48line_results_dir): os.mkdir(olfa_48line_results_dir)

            # check what files are in this folder
            list_of_files = os.listdir(olfa_48line_results_dir)
            list_of_files = [x for x in list_of_files if '.csv' in x]   # only csv files
            if not list_of_files: self.last_datafile_number = -1
            else:
                # find the number of the last data file
                last_datafile = list_of_files[len(list_of_files)-1]
                idx_fileExt = last_datafile.rfind('.')
                last_datafile = last_datafile[:idx_fileExt] # remove file extension
                idx_underscore = last_datafile.rfind('_')   # find last underscore
                last_datafile_num = last_datafile[idx_underscore+1:]
                if last_datafile_num.isnumeric():   # if what's after the underscore is a number
                    self.last_datafile_number = int(last_datafile_num)
                else:
                    self.last_datafile_number = 99
                    logger.warning('ew')    # TODO

            # get data file number
            self.this_datafile_number = self.last_datafile_number + 1
            self.this_datafile_number_padded = str(self.this_datafile_number).zfill(2) # zero pad
            
            # create data file name
            data_file_name = current_date + '_datafile_' + self.this_datafile_number_padded
            self.data_file_name_lineEdit.setText(data_file_name)


        else:
            logger.warning('program selected is not set up')
    
    def program_start_clicked(self):
        if self.program_start_btn.isChecked():
            self.program_start_btn.setText('End Program')

            if self.program_to_run == "the program":
                self.run_odor_calibration()
            if self.program_to_run == 'setpoint characterization':
                self.run_setpoint_characterization()

        else:
            logger.info('program start button unclicked')
            self.program_start_btn.setText('Start')
            self.threadIsFinished()
    
    def run_odor_calibration(self):
        logger.info('running odor calibration procedure')
        
        # check that PID is a device & is connected
        try:
            if self.pid_nidaq.connectButton.isChecked() == False:
                logger.debug('connecting to pid')
                self.pid_nidaq.connectButton.toggle()
        except AttributeError as err:
            logger.warning('PID is not added as a device - adding now')
            self.add_pid_btn.toggle()
            logger.debug('connecting to pid')
            self.pid_nidaq.connectButton.toggle()


        # TODO: change datafile location
        # DATAFILE STUFF
        datafile_name = self.data_file_name_lineEdit.text()
        self.datafile_dir = self.data_file_dir_lineEdit.text() + '\\' + datafile_name + '.csv'
        # if file does not exist: create it
        if not os.path.exists(self.datafile_dir):
            logger.info('Creating new file: %s', datafile_name)
            File = datafile_name, ' '
            file_created_time = utils.get_current_time()
            file_created_time = file_created_time[:-4]
            with open(self.datafile_dir,'a',newline='') as f:
                writer = csv.writer(f,delimiter=',')
                writer.writerow(File)
                writer.writerow("")
        else:
            logger.warning('file already exists!!!!!!!!')


        # GET PROGRAM PARAMETERS
        vial_flows_complete_list = []
        n_rep = self.num_repetitions_widget.value()
        vial_open_duration = self.vial_open_time_widget.value()
        


        # CREATE STIMULUS LIST
        for v in self.olfactometer.vials:
            # iterate through vials to see which is checked
            vial_is_checked = v.vial_checkbox.isChecked()
            if vial_is_checked == True:
                this_vial_flow_str = v.vial_flow_list.text()
                this_vial_flow_values = this_vial_flow_str.split(",")
                
                for f in this_vial_flow_values:
                    this_vial_num = int(v.vialNum)
                    temp = np.repmat([this_vial_num,f],n_rep,1)     # make number of repetitions of this
                    vial_flows_complete_list.extend(temp.tolist())  # add to complete list
        random.shuffle(vial_flows_complete_list)        # randomize
        self.stimulus_list = vial_flows_complete_list

        # ITERATE THROUGH EACH STIMULUS
        for stimulus in self.stimulus_list:
            vial_number = stimulus[0]
            flow_value = stimulus[1]

            # tell pid to make an empty list, start adding values to it
            self.pid_nidaq.start_making_data_list()

            # open vial
            self.olfactometer.olfa_device._set_valveset(vial_number,valvestate=1,suppress_errors=False)
            
            # wait x sec
            time.sleep(vial_open_duration)

            # close vial
            self.olfactometer.olfa_device._set_valveset(vial_number,valvestate=0,suppress_errors=False)

            # get list of values from pid
            list_of_pid_values = []
            # tell pid to stop adding values to the list
            self.pid_nidaq.stop_making_data_list()
            list_of_pid_values = self.pid_nidaq.data_list
            
            # write this line to the csv file
            write_to_file = copy.copy(list_of_pid_values)
            write_to_file.insert(0,flow_value)
            write_to_file.insert(0,vial_number)
            write_to_file = tuple(write_to_file)
            with open(self.datafile_dir,'a',newline='') as f:
                writer = csv.writer(f,delimiter=',')
                writer.writerow(write_to_file)
                
            
            
            
            #string_to_write_to_file = vial_number + ',' + 
            
            # stop recording
            #self.read_thread.exit()
            # save
            # kill urself

        logger.info('all done')
        # increment file name
        # self.last_datafile_number = self.this_datafile_number
        self.this_datafile_number = self.last_datafile_number + 1
        self.this_datafile_number_padded = str(self.this_datafile_number).zfill(2)  # zero pad
        data_file_name = current_date + '_datafile_' + self.this_datafile_number_padded
        self.data_file_name_lineEdit.setText(data_file_name)
    
    
    # PROGRAMS FOR 48-LINE OLFA
    ##############################
    def run_setpoint_characterization(self):
        logger.info('run setpoint characterization')

        # CHECK THAT PID IS CONNECTED
        try:
            if self.pid_nidaq.connectButton.isChecked() == False:
                logger.debug('connecting to pid')
                self.pid_nidaq.connectButton.toggle()
        except AttributeError as err:
            logger.warning('PID is not added as a device')
            '''
            self.add_pid_btn.toggle()
            logger.debug('connecting to pid')
            self.pid_nidaq.connectButton.toggle()
            '''
        except RuntimeError as err:
            logger.debug('no pid')
        
        # CHECK THAT OLFACTOMETER IS CONNECTED
        try:
            if self.olfactometer.connect_btn.isChecked() == False:
                logger.warning('olfactometer not connected, attempting to connect')
                utils_olfa_48line.connect_to_48line_olfa(self)
        except AttributeError as err:   logger.error(err)
        
        '''
        # DATAFILE STUFF        # TODO this is a repeat
        datafile_name = self.data_file_name_lineEdit.text()
        self.datafile_dir = self.data_file_dir_lineEdit.text() + '\\' + datafile_name + '.csv'
        # if file does not exist, create it
        if not os.path.exists(self.datafile_dir):
            logger.info('Creating new file: %s', datafile_name)
            File = datafile_name, ' '
            file_created_time = utils.get_current_time()
            file_created_time = file_created_time[:-4]
            with open(self.datafile_dir,'a',newline='') as f:
                writer = csv.writer(f,delimiter=',')
                writer.writerow(File)
                writer.writerow("")
        else:
            logger.warning('file already exists!!!!!!!!')
        '''
        
        # START RECORDING
        if self.begin_record_btn.isChecked() == False:
            logger.debug('clicking begin record button')
            self.begin_record_btn.click()

        # GET PROGRAM PARAMETERS
        self.slave_to_run = self.p_slave_select_wid.currentText()
        self.vial_to_run = self.p_vial_wid.currentText()
        setpoints_to_run = self.p_setpoints_wid.text()
        setpoint_order = self.p_sp_order_wid.currentText()
        num_trials = int(self.p_numTrials_wid.text())
        dur_ON = self.p_dur_on_wid.value()
        dur_OFF = self.p_dur_off_wid.value()
        self.full_vial_name = self.slave_to_run + self.vial_to_run
        
        # CREATE STIMULUS LIST
        vial_flows_complete_list = []
        setpoints_to_run_values = setpoints_to_run.split(",")
        for f in setpoints_to_run_values:
            temp = np.repmat([self.full_vial_name,f],num_trials,1)     # make number of repetitions of this
            vial_flows_complete_list.extend(temp.tolist())  # add to complete list
        if setpoint_order == 'Random':  random.shuffle(vial_flows_complete_list)    # randomize if needed
        
        # GET DICTIONARIES FOR THIS VIAL
        vial_idx = int(self.vial_to_run) - 1
        for s in self.olfactometer.slave_objects:
            if s.name == self.slave_to_run: thisVial = s.vials[vial_idx]; break
        sccm2Ard_dict_to_use = self.olfactometer.sccm2Ard_dicts.get(thisVial.cal_table)
        ard2Sccm_dict_to_use = self.olfactometer.ard2Sccm_dicts.get(thisVial.cal_table)
        
        # SEND PARAMETERS TO WORKER
        self.obj_sptchar.complete_stimulus_list = copy.copy(vial_flows_complete_list)
        self.obj_sptchar.sccm2Ard_dict = copy.copy(sccm2Ard_dict_to_use)
        self.obj_sptchar.ard2Sccm_dict = copy.copy(ard2Sccm_dict_to_use)
        self.obj_sptchar.duration_on = copy.copy(dur_ON)
        self.obj_sptchar.duration_off = copy.copy(dur_OFF)
        
        # SET VIAL TO DEBUG MODE
        if thisVial.read_flow_vals_btn.isChecked() == False:
            thisVial.read_flow_vals_btn.toggle()
        # print a warning if any other vials are also printing
        for s in self.olfactometer.slave_objects:
            for v in s.vials:
                if v.read_flow_vals_btn.isChecked() == True:
                    if v.full_vialNum == thisVial.full_vialNum:
                        pass
                    else:
                        logger.warning('%s is set to debug mode', v.full_vialNum)
        
        # START WORKER THREAD
        self.obj_sptchar.threadON = True
        logger.debug('starting thread_olfa')
        self.thread_olfa.start()            # # start thread -> worker_sptChar iterates through stimuli
    
    def set_up_threads_sptchar(self):
        self.obj_sptchar = worker_sptChar()
        self.thread_olfa = QThread()
        self.obj_sptchar.moveToThread(self.thread_olfa)

        self.obj_sptchar.w_sendThisSp.connect(self.sendThisSetpoint)
        self.obj_sptchar.w_send_OpenValve.connect(self.send_OpenValve)
        self.obj_sptchar.finished.connect(self.threadIsFinished)
        self.thread_olfa.started.connect(self.obj_sptchar.exp)

    def threadIsFinished(self):
        self.obj_sptchar.threadON = False
        self.thread_olfa.exit()
        self.program_start_btn.setChecked(False)
        self.program_start_btn.setText('Start')
        #self.progSettingsBox.setEnabled(True)
        logger.info('Finished program')

        # end recording
        if self.begin_record_btn.isChecked():
            self.end_record_btn.click()


    def active_slave_refresh(self):        
        # if olfactometer is not connected, connect to it
        if self.olfactometer.connect_btn.isChecked() == False:
            utils_olfa_48line.connect_to_48line_olfa(self)
        
        # add the active slaves
        self.p_slave_select_wid.clear()
        self.p_slave_select_wid.addItems(self.olfactometer.active_slaves)
        if self.p_slave_select_wid.count() == 0:
            self.p_slave_select_wid.addItem(no_active_slaves_warning)
            self.program_start_btn.setEnabled(False)
        else:
            self.program_start_btn.setEnabled(True)
    
    def sendThisSetpoint(self, vial_name:str, ard_val:int):
        # TODO: change worker_sptChar so it receives the entire vial object when it starts a program. then it'll already have the dictionary, etc
        
        '''
        # find dictionary to use TODO
        #for s in self.slaves:
        #    if s.slaveName == slave:
        #        for v in s.vials:
        #            if v.vialNum == str(vial):
        #                sensDictName = v.calTable
        #dictToUse = self.sccm2Ard_dicts.get(sensDictName)
        # convert to integer and send
        #ardVal = utils.convertToInt(float(sccmVal),dictToUse)
        '''
        
        #ard_val = 700   # fix this
        strToSend = 'S_Sp_' + str(ard_val) + '_' + vial_name
        self.olfactometer.send_to_master(strToSend)
        
    def send_OpenValve(self, vial_name:str, dur:int):
        strToSend = 'S_OV_' + str(dur) + '_' + vial_name
        self.olfactometer.send_to_master(strToSend)

        # write to datafile
        self.receive_data_from_device('olfactometer ' + vial_name,'OV',str(dur))
    ##############################
    
    
    def add_olfa_48line_toggled(self,checked):
        if checked:
            # Create Olfactometer Objectgit st
            self.olfactometer = olfa_driver_48line.olfactometer_window()
            self.device_layout.addWidget(self.olfactometer)
            self.add_olfa_orig_btn.setEnabled(False)
            self.add_olfa_48line_btn.setText('Remove olfactometer\n(48-line)')
            self.olfa_type_label.setText('48-line olfa')

            # Program Selection/Parameters
            self.program_selection_groupbox.setEnabled(True)
            self.program_selection_combo.clear()
            self.program_selection_combo.addItems(programs_48line)
            
            if self.program_parameters_box.isEnabled():
                logger.info('refresh')
                if self.program_to_run == 'setpoint characterization':
                    self.active_slave_refresh()
            
            # Results file name/directory
            self.olfa_48line_resultfiles_dir = main_datafile_directory + '\\48-line olfa'
            if not os.path.exists(self.olfa_48line_resultfiles_dir):
                os.mkdir(self.olfa_48line_resultfiles_dir)
                logger.debug('created 48-line olfa results files at %s',self.olfa_48line_resultfiles_dir)
            self.today_olfa_48line_resultfiles_dir = main_datafile_directory + '\\48-line olfa' + '\\' + current_date
            if not os.path.exists(self.today_olfa_48line_resultfiles_dir):
                os.mkdir(self.today_olfa_48line_resultfiles_dir)
                logger.debug('created today folder at %s',self.today_olfa_48line_resultfiles_dir)
            self.data_file_dir_lineEdit.setText(self.today_olfa_48line_resultfiles_dir)
            
            # debugging: just for today (7/25/2022)
            for s in self.olfactometer.slave_objects:
                s.vials[0].setEnabled(False)
                s.vials[2].setEnabled(False)
                s.vials[7].setEnabled(False)
        
        else:
            self.mainLayout.removeWidget(self.olfactometer)
            sip.delete(self.olfactometer)
            logger.debug('removed olfactometer object')
            self.add_olfa_orig_btn.setEnabled(True)
            self.add_olfa_48line_btn.setText('Add Olfactometer\n(48-line)')
            self.olfa_type_label.setText(' ')
            self.program_selection_groupbox.setEnabled(False)
            self.program_parameters_box.setEnabled(False)

    def add_olfa_orig_toggled(self, checked):
        if checked:
            self.olfactometer = olfa_driver_original.olfactometer_window()
            self.device_layout.addWidget(self.olfactometer)
            logger.debug('created olfactometer object')
            self.add_olfa_48line_btn.setEnabled(False)
            self.add_olfa_orig_btn.setText('Remove olfactometer\n(original)')
            self.olfa_type_label.setText('original olfa')
            self.program_selection_groupbox.setEnabled(True)
            self.program_selection_combo.clear()
            self.program_selection_combo.addItems(programs_orig)

        else:
            self.mainLayout.removeWidget(self.olfactometer)
            sip.delete(self.olfactometer)
            logger.debug('removed olfactometer object')
            self.add_olfa_48line_btn.setEnabled(True)
            self.add_olfa_orig_btn.setText('Add Olfactometer\n(original)')
            self.olfa_type_label.setText(' ')
            self.program_selection_groupbox.setEnabled(False)
            self.program_parameters_box.setEnabled(False)

    def add_pid_toggled(self, checked):
        if checked:
            self.pid_nidaq = NiDAQ_driver.NiDaq(self)
            self.device_layout.insertWidget(0,self.pid_nidaq)
            logger.debug('created pid object')

            self.add_pid_btn.setText('Remove PID')
            self.add_pid_btn.setToolTip('u sure?')
            
        else:
            self.mainLayout.removeWidget(self.pid_nidaq)
            sip.delete(self.pid_nidaq)
            logger.debug('removed nidaq object')
            
            self.add_pid_btn.setText('Add PID')
    
    def add_flow_sens_toggled(self, checked):
        if checked:
            self.flow_sensor = flow_sensor_driver.flowSensor(port=' ')
            self.device_layout.insertWidget(0,self.flow_sensor)
            logger.debug('created flow sensor object')
            self.add_flow_sens_btn.setText('Remove\nHoneywell 5100V')

        else:
            self.mainLayout.removeWidget(self.flow_sensor)
            sip.delete(self.flow_sensor)
            logger.debug('removed flow sensor object')
            self.add_flow_sens_btn.setText('Add\nHoneywell 5100V')
    
    def begin_record_btn_clicked(self):
        if self.begin_record_btn.isChecked() == True:
            logger.debug('begin record button clicked')
            self.begin_record_btn.setText('Pause Recording')
            self.end_record_btn.setEnabled(True)

            # get file name & full directory
            datafile_name = self.data_file_name_lineEdit.text()
            self.datafile_dir = self.data_file_dir_lineEdit.text() + '\\' + datafile_name + '.csv'
            # if directory does not exist, make it
            if not os.path.exists(self.data_file_dir_lineEdit.text()):
                os.mkdir(self.data_file_dir_lineEdit.text())
            # if file does not exist: create it & write header
            if not os.path.exists(self.datafile_dir):
                logger.info('Creating new file: %s (%s)', datafile_name, self.datafile_dir)
                File = datafile_name, ' '
                file_created_time = utils.get_current_time()
                file_created_time = file_created_time[:-4]
                Time = 'File Created: ', str(current_date + ' ' + file_created_time)
                DataHead = 'Time','Instrument','Unit','Value'
                #pid_line = str(self.p_pid_gain.text()) # TODO
                #pid_line_header = 'PIDgain',pid_line
                with open(self.datafile_dir,'a',newline='') as f:
                    writer = csv.writer(f,delimiter=',')
                    writer.writerow(File)
                    writer.writerow(Time)
                    #if self.program_to_run == 'setpoint characterization':
                    #    writer.writerow(pid_line_header)
                    #else:
                    #    writer.writerow("")
                    writer.writerow("")
                    writer.writerow(DataHead)
                self.data_file_textedit.append(datafile_name)
                self.data_file_textedit.append('File Created: ' + str(current_date + ' ' + file_created_time))
                # if setpoint char: write pid gain
                #if self.program_to_run == 'setpoint characterization':
                #    self.data_file_textedit.append('PID gain,' + pid_line)
                #self.data_file_textedit.append('Time, Instrument, Unit, Value')
            else:   # TODO: throw an error if the file already exists
                logger.info('Recording resumed')            

        else:
            logger.info('Recording paused')
            self.begin_record_btn.setText('Resume Recording')
    
    def end_recording(self):
        logger.info('Ended recording to file: %s', self.data_file_name_lineEdit.text())
        # TODO: add a bunch of newlines

        
        # update file number in box
        self.this_datafile_number = self.this_datafile_number + 1
        self.this_datafile_number_padded = str(self.this_datafile_number).zfill(2) # zero pad
        data_file_name = current_date + '_datafile_' + self.this_datafile_number_padded
        self.data_file_name_lineEdit.setText(data_file_name)

        self.begin_record_btn.setText('Create File && Begin Recording')
        self.begin_record_btn.setChecked(False)
        self.end_record_btn.setChecked(False)
        self.end_record_btn.setEnabled(False)
        self.data_file_textedit.clear()
    
    def receive_data_from_device(self, device, unit, value):
        # if recording is ON: write to datafile
        if self.begin_record_btn.isChecked():
            current_time = utils.get_current_time()
            write_to_file = current_time,device,unit,str(value)
            with open(self.datafile_dir,'a',newline='') as f:
                writer = csv.writer(f,delimiter=',')
                writer.writerow(write_to_file)
            display_to_box = str(write_to_file)
            self.data_file_textedit.append(display_to_box[1:-1])

    def closeEvent(self, event):
        # if olfactometer is still connected: set all vials to not debug
        pass
        '''
        active_slaves = self.olfactometer.active_slaves
        # for each currently active slave
        for slave in active_slaves:
            # for each vial
            for vial in range(0,olfactometer_driver.vialsPerSlave):
                # set all vials to not debug
                strToSend = 'MS_' + slave + str(vial+1)
                self.olfactometer.send_to_master(strToSend)
        '''
    

if __name__ == "__main__":
    app1 = QApplication(sys.argv)
    theWindow = mainWindow()
    theWindow.show()
    sys.exit(app1.exec_())