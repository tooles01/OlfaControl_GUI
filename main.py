#!/usr/bin/env python
import sys, os, logging, csv
import numpy.matlib as np
import random, time
import copy

from PyQt5 import sip
from PyQt5.QtWidgets import *

import utils
import olfa_driver_48line
import NiDAQ_driver
import olfa_driver_original
#from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
#import matplotlib.pyplot  as plt
import olfa_original_procedures
#import olfa_48line_procedures

#main_datafile_directory = 'C:\\Users\\Admin\\Dropbox (NYU Langone Health)\\OlfactometerEngineeringGroup (2)\\Control\\a_software\\logfiles\\8-line_v1'
#main_datafile_directory = 'C:\\Users\\SB13FLLT004\\Dropbox (NYU Langone Health)\\OlfactometerEngineeringGroup (2)\\Control\\a_software\\logfiles\\8-line_v1'

main_datafile_directory = 'C:\\GIT\\OlfaControl_GUI\\result_files'
programs_48line = ['setpoint characterization','additive']
programs_orig = ['the program']
        

class mainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()

        self.generate_ui()        
        
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
        self.device_groupbox = QGroupBox('Devices')
        self.device_layout = QVBoxLayout()
        self.device_groupbox.setLayout(self.device_layout)


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
        log_box_layout = QGridLayout()
        log_box_layout.addWidget(QLabel('Log messages:'),0,0,1,1)
        log_box_layout.addWidget(self.log_clear_btn,0,2,1,1)
        log_box_layout.addWidget(self.log_text_edit,1,0,1,3)
        '''
        custom_handler = logging.StreamHandler()
        custom_handler.setLevel(logging.DEBUG)
        custom_handler_formatter = logging.Formatter('%(name)-14s: %(levelname)-8s: %(message)s')
        custom_handler.setFormatter(custom_handler_formatter)
        custom_handler.setStream(self.log_text_edit)
        logger.addHandler(custom_handler)
        '''
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel('Log file located at:'))
        layout.addWidget(self.log_file_dir_label)
        layout.addWidget(QLabel('\n'))
        layout.addLayout(log_box_layout)
        self.general_settings_box.setLayout(layout)
        max_height = self.general_settings_box.sizeHint().height()
        self.general_settings_box.setMaximumHeight(max_height)
        
    def create_program_selection_groupbox(self):
        self.program_selection_groupbox = QGroupBox('Program Selection')

        self.olfa_type_label = QLabel()

        self.program_selection_combo = QComboBox()
        self.program_selection_combo.addItems(programs_48line)
        
        self.program_selection_picked = QPushButton('Select')
        self.program_selection_picked.clicked.connect(self.create_program_widgets)

        layout = QFormLayout()
        layout.addRow(QLabel('Olfactometer type:'),self.olfa_type_label)
        layout.addRow(self.program_selection_combo,self.program_selection_picked)
        #layout.addRow(self.program_start_btn)
        self.program_selection_groupbox.setLayout(layout)
        self.program_selection_groupbox.setEnabled(False)
    

    def create_program_parameters_box(self):
        self.program_parameters_box = QGroupBox('Program Parameters')

        self.program_start_btn = QPushButton(text='Start')
        self.program_start_btn.clicked.connect(self.program_start_clicked)
        self.program_start_btn.setEnabled(False)
        
        
        self.program_parameters_layout = QFormLayout()
        self.program_parameters_layout.addWidget(self.program_start_btn)
        self.program_parameters_box.setLayout(self.program_parameters_layout)

    def create_program_widgets(self):
        self.program_to_run = self.program_selection_combo.currentText()
        self.program_start_btn.setEnabled(True)

        if self.program_to_run == "the program":
            self.iti_time_widget = QSpinBox(value=5)
            self.vial_open_time_widget = QSpinBox(value=5)
            self.num_repetitions_widget = QSpinBox(value=10)

            self.program_parameters_layout.insertRow(0,QLabel('Inter trial interval [s]:'),self.iti_time_widget)
            self.program_parameters_layout.insertRow(1,QLabel('Vial open time [s]:'),self.vial_open_time_widget)
            self.program_parameters_layout.insertRow(2,QLabel('Number of repetitions:'),self.num_repetitions_widget)
            


        if self.program_to_run == "setpoint characterization":
            # add the widgets for this
            pass

    
    def create_datafile_box(self):
        self.datafile_groupbox = QGroupBox('Data file')

        # find / make directory for today's files
        today_datafile_dir = main_datafile_directory + '\\' + current_date        # TODO: update this to search any computer
        if not os.path.exists(today_datafile_dir): os.mkdir(today_datafile_dir)

        data_file_dir = today_datafile_dir
        self.data_file_dir_lineEdit = QLineEdit(text=data_file_dir,readOnly=True)

        # check what files are in this folder
        list_of_files = os.listdir(data_file_dir)
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
                logger.warning('ew')    # TODO: finish this

        self.this_datafile_number = self.last_datafile_number + 1
        self.this_datafile_number_padded = str(self.this_datafile_number).zfill(2) # zero pad
        
        # create data file name
        data_file_name = current_date + '_datafile_' + self.this_datafile_number_padded
        self.data_file_name_lineEdit = QLineEdit(text=data_file_name)
        self.data_file_textedit = QTextEdit(readOnly=True)

        self.begin_record_btn = QPushButton(text='Create File && Begin Recording',checkable=True)
        self.end_record_btn = QPushButton(text='End Recording')
        self.begin_record_btn.clicked.connect(self.begin_record_btn_toggled)
        self.end_record_btn.clicked.connect(self.end_recording)
        self.end_record_btn.setEnabled(False)
        record_layout = QHBoxLayout()
        record_layout.addWidget(self.begin_record_btn)
        record_layout.addWidget(self.end_record_btn)


        layout = QFormLayout()
        layout.addRow(QLabel('Directory:'),self.data_file_dir_lineEdit)
        layout.addRow(QLabel('File Name:'),self.data_file_name_lineEdit)
        layout.addRow(record_layout)
        layout.addRow(self.data_file_textedit)
        self.datafile_groupbox.setLayout(layout)

    def create_add_devices_box(self):
        self.add_devices_groupbox = QGroupBox("Devices")

        self.add_olfa_48line_btn = QPushButton(text='Add Olfactometer\n(48-line)',checkable=True,toggled=self.add_olfa_48line_toggled)
        self.add_pid_btn = QPushButton(text='Add PID',checkable=True,toggled=self.add_pid_toggled)
        self.add_olfa_orig_btn = QPushButton(text='Add Olfactometer\n(original)',checkable=True,toggled=self.add_olfa_orig_toggled)
        
        layout = QVBoxLayout()
        layout.addWidget(self.add_pid_btn)
        layout.addWidget(self.add_olfa_48line_btn)
        layout.addWidget(self.add_olfa_orig_btn)
        self.add_devices_groupbox.setLayout(layout)

    
    def add_olfa_48line_toggled(self,checked):
        if checked:
            self.olfactometer = olfa_driver_48line.olfactometer_window()
            self.device_layout.addWidget(self.olfactometer)
            logger.debug('created olfactometer object')
            self.add_olfa_orig_btn.setEnabled(False)
            self.add_olfa_48line_btn.setText('Remove olfactometer\n(48-line)')
            self.olfa_type_label.setText('48-line olfa')
            self.program_selection_groupbox.setEnabled(True)
            self.program_selection_combo.clear()
            self.program_selection_combo.addItems(programs_48line)
            
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
            print( self.olfactometer.mfc1.mfc_capacity_set)
            self.olfactometer.mfc1.mfc_capacity_set.setValue(100)
       

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
        
    def program_start_clicked(self):

        if self.program_to_run == "the program":
            self.run_odor_calibration()
        


    def run_odor_calibration(self):
        # TODO: check that PID is connected

        # TODO: change datafile location

        # .3 seconds is not enough
        # .4 seconds is enough
        # .4 seconds is no longer enough
        # .5 seconds is no longer enough
        time_to_pause_seconds = 1

        # Connect olfactometer
        self.olfactometer.setDefaultParams()
        self.olfactometer.COM_settings_mfc['com_port'] = int(self.olfactometer.portStr[3:])
        self.olfactometer.olfa_device.connect_olfa(self.olfactometer.MFC_settings, self.olfactometer.COM_settings_mfc, flow_units='SCCM', setflow=-1)   

       

        # DATAFILE STUFF
        datafile_name = self.data_file_name_lineEdit.text()
        self.datafile_dir = self.data_file_dir_lineEdit.text() + '\\' + datafile_name + '.csv'
        # if file does not exist: create it
        if not os.path.exists(self.datafile_dir):
            logger.info('Creating new file: %s', datafile_name)
            File = datafile_name, ' '
            file_created_time = utils.get_current_time()
            file_created_time = file_created_time[:-4]
            write_this_row = file_created_time,str(time_to_pause_seconds)
            with open(self.datafile_dir,'a',newline='') as f:
                writer = csv.writer(f,delimiter=',')
                writer.writerow(File)
                writer.writerow(write_this_row)
                writer.writerow("")
        else:
            logger.warning('file already exists!!!!!!!!')


        # GET PROGRAM PARAMETERS
        vial_flows_complete_list = []
        n_rep = self.num_repetitions_widget.value()
        vial_open_duration = self.vial_open_time_widget.value()
        
        iti_time = self.iti_time_widget.value()
        # make sure you retrieve the last capacity value
        self.olfactometer.olfa_device.mfc1_capacity = self.olfactometer.mfc1.mfc_capacity_set.value()
        # check PID box to connect
        self.pid_nidaq.connectButton.setChecked(True)
        # check olfa box to add


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
            #print(type(flow_value))
            # set MFC 

            self.olfactometer.olfa_device.set_flowrate(int(flow_value))
            print("set mfc")
            time.sleep(3)
            # tell pid to make an empty list, start adding values to it
            self.pid_nidaq.start_making_data_list()

            # open vial
            self.olfactometer.olfa_device._set_valveset(vial_number,valvestate=1,suppress_errors=False)
            print("Opening vial")
            # wait x sec
            time.sleep(vial_open_duration)

            # close vial
            self.olfactometer.olfa_device._set_valveset(vial_number,valvestate=0,suppress_errors=False)
            print("Closing vial")
           
            time.sleep(iti_time)
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
        # Close connection to olfactometer
        self.olfactometer.olfa_device.disconnect_olfa()
        self.last_datafile_number = self.this_datafile_number
        self.this_datafile_number = self.last_datafile_number + 1
        self.this_datafile_number_padded = str(self.this_datafile_number).zfill(2)  # zero pad
        data_file_name = current_date + '_datafile_' + self.this_datafile_number_padded
        self.data_file_name_lineEdit.setText(data_file_name)

        # increment file name


    
    def begin_record_btn_toggled(self):
        if self.begin_record_btn.isChecked() == True:
            # get file name & full directory
            datafile_name = self.data_file_name_lineEdit.text()
            self.datafile_dir = self.data_file_dir_lineEdit.text() + '\\' + datafile_name + '.csv'

            # if file does not exist: create it & write header
            if not os.path.exists(self.datafile_dir):
                logger.info('Creating new file: %s', datafile_name)
                File = datafile_name, ' '
                file_created_time = utils.get_current_time()
                file_created_time = file_created_time[:-4]
                Time = 'File Created: ', str(current_date + ' ' + file_created_time)
                DataHead = 'Time','Instrument','Unit','Value'
                with open(self.datafile_dir,'a',newline='') as f:
                    writer = csv.writer(f,delimiter=',')
                    writer.writerow(File)
                    writer.writerow(Time)
                    writer.writerow("")
                    writer.writerow(DataHead)
                self.data_file_textedit.append(datafile_name)
                self.data_file_textedit.append('File Created: ' + str(current_date + ' ' + file_created_time))
                self.data_file_textedit.append('Time, Instrument, Unit, Value')
            else:   # TODO: throw an error if the file already exists
                logger.info('Recording resumed')
            
            self.begin_record_btn.setText('Pause Recording')
            self.end_record_btn.setEnabled(True)

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
    current_date = utils.currentDate

    # LOGGING

    # if today folder doesn't exist, make it
    today_logDir = main_datafile_directory + '\\' + current_date
    if not os.path.exists(today_logDir): os.mkdir(today_logDir)


    logger = logging.getLogger(name='main')
    logger.setLevel(logging.DEBUG)
    if logger.hasHandlers():    logger.handlers.clear()     # removes duplicate log messages
    console_handler = utils.create_console_handler()
    file_handler = utils.create_file_handler(main_datafile_directory)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)




    # MAIN APP
    logger.debug('opening window')
    app1 = QApplication(sys.argv)
    theWindow = mainWindow()
    theWindow.show()
    sys.exit(app1.exec_())