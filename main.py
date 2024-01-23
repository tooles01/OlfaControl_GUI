import sys, os, logging, csv, copy, time, random
import numpy.matlib as np
from PyQt5 import sip
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtCore import QTimer
from datetime import datetime

import NiDAQ_driver, flow_sensor_driver, olfa_driver_original, olfa_driver_48line
import utils, utils_olfa_48line, program_additive_popup
import config_main


programs_48line = ['setpoint characterization','additive']
programs_orig = ['the program']

current_date = utils.currentDate


##############################
# CREATE LOGGER
main_datafile_directory = utils.find_log_directory()
if not os.path.exists(main_datafile_directory): os.mkdir(main_datafile_directory)   # if folder doesn't exist, make it
logger = logging.getLogger(name='main')
logger.setLevel(logging.DEBUG)
if logger.hasHandlers():    logger.handlers.clear()     # removes duplicate log messages
console_handler = utils.create_console_handler()
file_handler = utils.create_file_handler(main_datafile_directory)
logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.debug('log file located at: %s', main_datafile_directory)
##############################
# test


class worker_sptChar(QObject):
    finished = pyqtSignal()
    w_sendThisSp = pyqtSignal(str,int)
    w_send_OpenValve = pyqtSignal(str,float)
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
        time.sleep(config_main.waitBtSpAndOV)
        time.sleep(config_main.waitBtSpAndOV)

        # do an off duration so we have a better baseline
        time.sleep(self.duration_off)

        # calculate full duration of entire shenanigan (for progress bar)
        self.full_trial_duration_sec = (self.duration_on+self.duration_off) * len(self.complete_stimulus_list)
        self.trial_start_time = datetime.now()
        
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
                time.sleep(config_main.waitBtSpAndOV)

                # update progress bar
                current_time = datetime.now()
                time_elapsed = (current_time - self.trial_start_time).total_seconds()
                ratio_of_entire_duration = time_elapsed / self.full_trial_duration_sec
                self.w_incProgBar.emit(int(ratio_of_entire_duration*100))
                
                # open the vial
                logger.info('Opening %s (%s seconds)',full_vial_name,self.duration_on)
                self.w_send_OpenValve.emit(full_vial_name,self.duration_on)
                
                # wait until the vial closes
                time.sleep(self.duration_on)

                # update progress bar
                current_time = datetime.now()
                time_elapsed = (current_time - self.trial_start_time).total_seconds()
                ratio_of_entire_duration = time_elapsed / self.full_trial_duration_sec
                self.w_incProgBar.emit(int(ratio_of_entire_duration*100))

                # wait for the time between trials
                time.sleep(self.duration_off-config_main.waitBtSpAndOV)
                
                # update progress bar
                current_time = datetime.now()
                time_elapsed = (current_time - self.trial_start_time).total_seconds()
                ratio_of_entire_duration = time_elapsed / self.full_trial_duration_sec
                self.w_incProgBar.emit(int(ratio_of_entire_duration*100))
        
        # update progress bar
        current_time = datetime.now()
        time_elapsed = (current_time - self.trial_start_time).total_seconds()
        ratio_of_entire_duration = time_elapsed / self.full_trial_duration_sec
        self.w_incProgBar.emit(int(ratio_of_entire_duration*100))
        
        self.finished.emit()

class worker_additive(QObject):
    finished = pyqtSignal()
    w_sendThisSp = pyqtSignal(str,int)
    w_send_OpenValve = pyqtSignal(str,float)
    w_send_Command = pyqtSignal(str)
    w_incProgBar = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.threadON = False
        
        # worker will receive these values from mainWindow during additive program setup (once "start" is clicked)
        self.vials_to_run = []
        self.complete_stimulus_list = []
        self.duration_on = 5
        self.duration_off = 5
        self.sccm2Ard_dict = []
        self.ard2Sccm_dict = []
    
    @pyqtSlot()
    def exp(self):
        # set vials to debug mode
        for v in self.vials_to_run:
            time.sleep(config_main.waitBtSpAndOV)
            strToSend = 'MS_debug_' + str(v)
            self.w_send_Command.emit(strToSend)        
        
        # wait so olfa has time to set vial to debug mode
        time.sleep(config_main.waitBtSpAndOV)
        time.sleep(config_main.waitBtSpAndOV)

        # do an off duration so we have a better baseline
        time.sleep(self.duration_off)

        # calculate full duration of entire shenanigan (for progress bar)
        self.full_trial_duration_sec = (self.duration_on+self.duration_off) * len(self.complete_stimulus_list)
        self.trial_start_time = datetime.now()
        
        # iterate through stimulus list
        for stimulus in self.complete_stimulus_list:
            if self.threadON == True:
                
                # update progress bar
                current_time = datetime.now()
                time_elapsed = (current_time - self.trial_start_time).total_seconds()
                ratio_of_entire_duration = time_elapsed / self.full_trial_duration_sec
                self.w_incProgBar.emit(int(ratio_of_entire_duration*100))
                
                # for each vial: send setpoint
                for v in range(len(self.vials_to_run)):
                    vial = self.vials_to_run[v]
                    this_setpoint_sccm = stimulus[v]
                    
                    # convert it to arduino integer
                    this_setpoint_int = utils_olfa_48line.convertToInt(this_setpoint_sccm,self.sccm2Ard_dict[v])
                    
                    # send the setpoint
                    logger.info('Setting %s to %s sccm',vial,this_setpoint_sccm)
                    self.w_sendThisSp.emit(vial,this_setpoint_int)
                    time.sleep(config_main.waitBtSpAndOV)
                
                # create the string to send : vial will be E12345
                vial_string = ''
                slave_name = self.vials_to_run[0]
                slave_name = slave_name[:-1]
                vial_string = vial_string + slave_name
                for v in self.vials_to_run:
                    vial_string = vial_string + v[1:]
                
                # open the vials
                logger.debug('Opening %s for %s seconds',vial_string,self.duration_on)
                self.w_send_OpenValve.emit(vial_string,self.duration_on)
                
                # update progress bar
                current_time = datetime.now()
                time_elapsed = (current_time - self.trial_start_time).total_seconds()
                ratio_of_entire_duration = time_elapsed / self.full_trial_duration_sec
                self.w_incProgBar.emit(int(ratio_of_entire_duration*100))
                
                # wait until the vials have closed
                time.sleep(self.duration_on)

                # update progress bar
                current_time = datetime.now()
                time_elapsed = (current_time - self.trial_start_time).total_seconds()
                ratio_of_entire_duration = time_elapsed / self.full_trial_duration_sec
                self.w_incProgBar.emit(int(ratio_of_entire_duration*100))
                
                # wait for the rest duration
                # TODO calculate what this actually should be
                time.sleep(self.duration_off - config_main.waitBtSpAndOV)
                
                # update progress bar
                current_time = datetime.now()
                time_elapsed = (current_time - self.trial_start_time).total_seconds()
                ratio_of_entire_duration = time_elapsed / self.full_trial_duration_sec
                self.w_incProgBar.emit(int(ratio_of_entire_duration*100))
            
            if self.threadON == False:
                break
        
        # update progress bar
        current_time = datetime.now()
        time_elapsed = (current_time - self.trial_start_time).total_seconds()
        ratio_of_entire_duration = time_elapsed / self.full_trial_duration_sec
        self.w_incProgBar.emit(int(ratio_of_entire_duration*100))
        
        self.finished.emit()
        self.threadON = False


class mainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.generate_ui()
        self.set_up_threads_sptchar()
        self.set_up_threads_additive()
        
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
        self.create_program_start_box()
        self.program_parameters_box.setEnabled(False)
        self.create_datafile_box()
        self.settings_layout = QGridLayout()
        self.settings_layout.addWidget(self.general_settings_box,0,0,1,1)
        self.settings_layout.addWidget(self.add_devices_groupbox,0,1,1,1)
        self.settings_layout.addWidget(self.program_selection_groupbox,1,0,1,2)
        self.settings_layout.addWidget(self.program_parameters_box,2,0,1,2)
        self.settings_layout.addWidget(self.program_start_box,3,0,1,2)
        self.settings_layout.addWidget(self.datafile_groupbox,4,0,1,2)
        self.settings_box.setLayout(self.settings_layout)
        #self.settings_box.setFixedWidth(self.settings_box.sizeHint().width() - 50)
        self.settings_box.setFixedWidth(self.settings_box.sizeHint().width())
        
        # DEVICES GROUPBOX
        self.device_groupbox = QGroupBox('Devices:')
        self.device_layout = QVBoxLayout()
        self.device_groupbox.setLayout(self.device_layout)

        # so that datafile stuff is all on one row
        w = self.datafile_groupbox.sizeHint().width()
        self.datafile_groupbox.setFixedWidth(w)
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
        self.log_file_dir_label = QLineEdit(text=self.log_file_dir,readOnly=True)
        self.log_file_dir_label.setToolTip('edit in config_main.py (if you need to change this)')
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel('Log file location:'))
        layout.addWidget(self.log_file_dir_label)
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

        # things for header
        self.data_file_pid_gain_lbl = QLabel('PID gain: ')
        self.data_file_pid_gain = QLineEdit(text=config_main.default_pid_gain)
        self.data_file_notes_lbl = QLabel('Notes:')
        self.data_file_notes_wid = QLineEdit()
        
        # BUTTONS
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
        layout.addRow(QLabel('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'))
        layout.addRow(QLabel('Things for file header:'))
        layout.addRow(self.data_file_pid_gain_lbl,self.data_file_pid_gain)
        layout.addRow(self.data_file_notes_lbl,self.data_file_notes_wid)
        layout.addRow(QLabel('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'))
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
    
    
    ##############################
    # PROGRAM WIDGETS
    def program_select_toggled(self):
        if self.program_selection_btn.isChecked():
            self.program_selection_btn.setText("Deselect")
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
            
            if self.program_to_run == "additive":
                self.create_additive_widgets()
        
        else:
            self.program_selection_btn.setText("Select")
            logger.debug('program selection unchecked')
            
            self.program_parameters_box.setEnabled(False)
            
            # remove the program parameters groupbox ** this is the only way I've been able to delete these stupid widgets
            sip.delete(self.program_parameters_box)
            # add the program parameters groupbox back in
            self.create_program_parameters_box()
            self.settings_layout.addWidget(self.program_parameters_box,2,0,1,2)            
    
    def create_program_selection_groupbox(self):
        self.program_selection_groupbox = QGroupBox('Program Selection')
        
        self.olfa_type_label = QLabel()
        self.program_selection_combo = QComboBox()
        self.program_selection_combo.addItems(programs_48line)
        self.program_selection_combo.setToolTip('Programs available:\n\n'
            'Setpoint characterization:\n'
            ' - Single odor line\n'
            ' - Multiple setpoints\n'
            '\nAdditive:\n'
            ' - Multiple odor lines\n'
            ' - Setpoint = total flow from all lines (setpoints for individual lines vary from trial to trial)')
        self.program_selection_btn = QPushButton(text='Select',checkable=True,toggled=self.program_select_toggled)
        
        layout = QFormLayout()
        layout.addRow(QLabel('Olfactometer type:'),self.olfa_type_label)
        layout.addRow(self.program_selection_combo,self.program_selection_btn)
        self.program_selection_groupbox.setLayout(layout)
        self.program_selection_groupbox.setEnabled(False)

    def create_program_parameters_box(self):
        self.program_parameters_box = QGroupBox('Program Parameters')
        
        self.program_parameters_layout = QFormLayout()
        self.program_parameters_box.setLayout(self.program_parameters_layout)
    
    def create_program_start_box(self):
        self.program_start_box = QGroupBox()
        self.program_start_btn = QPushButton(text='Start Program',checkable=True,toggled=self.program_start_clicked)
        self.program_progress_bar = QProgressBar()
        self.program_timer_label = QLabel()
        self.program_timer = QTimer()
        self.program_timer.timeout.connect(self.update_program_timer)
        layout_second_row = QHBoxLayout()
        layout_second_row.addWidget(self.program_start_btn)
        layout_second_row.addWidget(self.program_timer_label)
        layout_second_row.addWidget(QLabel('remaining'))
        
        self.program_start_box_layout = QVBoxLayout()
        self.program_start_box_layout.addWidget(self.program_progress_bar)
        self.program_start_box_layout.addLayout(layout_second_row)
        self.program_start_box.setLayout(self.program_start_box_layout)
    
    def increment_progress_bar(self, val):
        self.program_progress_bar.setValue(val)
    
    def update_program_timer(self):
        # TODO finish this
        pass
    
    def change_parameters_btn_toggled(self,checked):
        if checked:
            # DISABLE CHANGE PARAMETERS/START PROGRAM BUTTONS
            self.change_parameters_btn.setEnabled(False)
            self.program_start_btn.setEnabled(False)

            # SHOW ADDITIVE POPUP WINDOW
            self.additive_program_window.show()
            self.additive_program_window.parameter_set_button.setChecked(False)     # necessary or whole window is grayed out
    
    def program_start_clicked(self, checked):
        if checked:
            self.program_start_btn.setText('End Program')

            try:
                if self.program_to_run == "the program":
                    self.run_odor_calibration()
                if self.program_to_run == 'setpoint characterization':
                    self.run_setpoint_characterization()
                if self.program_to_run == 'additive':
                    self.run_additive_program()
            except AttributeError as err:
                logger.error('No program selected')
                self.program_start_btn.setChecked(False)

        else:
            #logger.debug('program start button unclicked')
            self.program_start_btn.setText('Start Program')
            # TODO additive takes an extra second to stop
            # stops trying to send parameters, but prints "finished program" a bit later
            # probably bc of sleeps?
            self.threadIsFinished() # TODO this double-prints when program finishes naturally
    ##############################
    
    
    ##############################
    # PROGRAMS FOR ORIGINAL OLFA
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
    ##############################
    
    
    ##############################
    # PROGRAM WIDGETS FOR 48-LINE OLFA
    def create_48line_program_widgets(self):
        if self.program_to_run == "setpoint characterization":
            
            ##############################
            ## CREATE WIDGETS            
            self.p_slave_lbl = QLabel('Slave:')
            self.p_slave_lbl.setToolTip('Slave to run program on')
            self.p_slave_select_wid = QComboBox()
            self.p_slave_select_wid.setToolTip('Only active slaves displayed')
            if self.olfactometer.active_slaves == []:
                self.p_slave_select_wid.addItem(config_main.no_active_slaves_warning)
            else:
                self.p_slave_select_wid.addItems(self.olfactometer.active_slaves)
            self.p_slave_select_refresh = QPushButton(text="Check Slave")
            self.p_slave_select_refresh.setToolTip('Request current slave addresses')
            self.p_slave_select_refresh.clicked.connect(self.active_slave_refresh)
            self.p_vial_lbl = QLabel('vial:')
            self.p_vial_lbl.setToolTip('Vial to run program on')
            self.p_vial_wid = QComboBox()
            vial_nums_int = list(range(1,self.olfactometer.vialsPerSlave+1))   # list of vial numbers
            vial_nums_str = []
            for item in vial_nums_int: vial_nums_str.append(str(item))
            self.p_vial_wid.addItems(vial_nums_str)
            self.p_vial_wid.setToolTip('Vial to run program on')
            
            self.p_vial_select_layout = QHBoxLayout()
            self.p_vial_select_layout.addWidget(self.p_slave_select_refresh)
            self.p_vial_select_layout.addWidget(self.p_slave_lbl)
            self.p_vial_select_layout.addWidget(self.p_slave_select_wid)
            self.p_vial_select_layout.addWidget(self.p_vial_lbl)
            self.p_vial_select_layout.addWidget(self.p_vial_wid)            
            
            self.p_setpoints_wid = QLineEdit(toolTip='Enter setpoints separated by commas')
            self.p_setpoints_wid.setPlaceholderText('Setpoints to run (sccm)')
            self.p_setpoints_wid.setText(config_main.default_setpoint)
            self.p_sp_order_wid = QComboBox()
            self.p_sp_order_wid.addItems(['Random','Sequential'])
            
            self.p_spt_layout = QHBoxLayout()
            self.p_spt_layout.addWidget(QLabel('Setpoints (sccm):'))
            self.p_spt_layout.addWidget(self.p_setpoints_wid)
            self.p_spt_layout.addWidget(self.p_sp_order_wid)
            
            self.p_dur_on_lbl = QLabel('Dur. on (s):',toolTip='Duration of valve opening (in seconds)')
            self.p_dur_off_lbl = QLabel('Dur. off (s):',toolTip="Rest duration between valve openings (in seconds)")
            self.p_dur_on_wid = QSpinBox(value=config_main.default_dur_ON,toolTip="Duration of valve opening (in seconds)")
            self.p_dur_off_wid = QSpinBox(value=config_main.default_dur_OFF,toolTip="Rest duration between valve openings (in seconds)")
            self.p_numTrials_wid = QLineEdit(text=str(config_main.default_numTrials))
            self.p_numTrials_wid.setPlaceholderText('# of Trials at each setpoint')
            self.p_numTrials_wid.setToolTip('# of Trials at each setpoint')
            # setpoints will be run in the order entered
            
            self.p_dur_layout = QHBoxLayout()
            self.p_dur_layout.addWidget(self.p_dur_on_lbl)
            self.p_dur_layout.addWidget(self.p_dur_on_wid)
            self.p_dur_layout.addWidget(self.p_dur_off_lbl)
            self.p_dur_layout.addWidget(self.p_dur_off_wid)
            self.p_dur_layout.addWidget(QLabel('# trials:'))
            self.p_dur_layout.addWidget(self.p_numTrials_wid)
            '''
            self.p_fake_open_lbl = QLabel('Fake open:')
            self.p_fake_open_wid = QComboBox()
            self.p_fake_open_wid.addItems(['On','Off'])
            
            p_btm_row_layout = QHBoxLayout()
            p_btm_row_layout.addWidget(self.p_fake_open_lbl)
            p_btm_row_layout.addWidget(self.p_fake_open_wid)
            '''
            
            self.program_parameters_layout.addRow(self.p_vial_select_layout)
            self.program_parameters_layout.addRow(self.p_spt_layout)
            self.program_parameters_layout.addRow(self.p_dur_layout)
            
            
            ##############################
            ## UPDATE DATAFILE STUFF            
            
            # change datafile name
            olfa_48line_results_dir = main_datafile_directory + '\\48-line olfa' + '\\' + current_date
            if not os.path.exists(olfa_48line_results_dir): os.mkdir(olfa_48line_results_dir); self.logger.debug('created folder at %s', olfa_48line_results_dir)

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
                    logger.debug('last datafile in this folder does not have a number (%s), setting default datafile number to 00', last_datafile)

            # get data file number
            self.this_datafile_number = self.last_datafile_number + 1
            self.this_datafile_number_padded = str(self.this_datafile_number).zfill(2) # zero pad
            
            # create data file name
            data_file_name = current_date + '_datafile_' + self.this_datafile_number_padded
            self.data_file_name_lineEdit.setText(data_file_name)

        else:
            logger.warning('program selected is not set up')
    
    def create_additive_widgets(self):
        # SHOW ADDITIVE POPUP WINDOW
        self.additive_program_window = program_additive_popup.additiveProgramSettingsPopup(self)
        self.additive_program_window.show()
        
        # ADD WIDGETS TO PROGRAM PARAMETERS LAYOUT
        self.additive_parameters_box = QGroupBox('Selected parameters:')
        #self.additive_parameters_layout = QFormLayout()
        #self.additive_parameters_box.setLayout(self.additive_parameters_layout)
        self.change_parameters_btn = QPushButton(text="Change Parameters",checkable=True,toggled=self.change_parameters_btn_toggled)
        
        self.program_parameters_layout.addWidget(self.additive_parameters_box)
        self.program_parameters_layout.addWidget(self.change_parameters_btn)

        # DISABLE CHANGE PARAMETERS/START PROGRAM BUTTONS
        self.change_parameters_btn.setEnabled(False)
        self.program_start_btn.setEnabled(False)
    
    def additive_parameters_display(self):
        ## function is called from the popup window
        
        ##############################
        # REMOVE PREVIOUS VALUES
        
        # delete & recreate additive parameters box
        sip.delete(self.additive_parameters_box)
        self.additive_parameters_box = QGroupBox('selected additive parameters')
        self.additive_parameters_layout = QFormLayout()
        self.additive_parameters_box.setLayout(self.additive_parameters_layout)
        self.program_parameters_layout.insertRow(0,self.additive_parameters_box)

        # create widgets
        self.a_vial_wid = QLineEdit()
        self.a_flow_wid = QLineEdit()
        self.a_flow_vals_wid = QLineEdit()
        #self.a_min_flow_wid = QLineEdit()
        #self.a_inc_flow_wid = QLineEdit()
        self.a_open_dur_wid = QLineEdit()
        self.a_rest_dur_wid = QLineEdit()
        self.a_num_trials_wid = QLineEdit()
        self.a_vial_wid.setEnabled(False)
        self.a_flow_wid.setEnabled(False)
        self.a_flow_vals_wid.setEnabled(False)
        #self.a_min_flow_wid.setEnabled(False)
        #self.a_inc_flow_wid.setEnabled(False)
        self.a_open_dur_wid.setEnabled(False)
        self.a_rest_dur_wid.setEnabled(False)
        self.a_num_trials_wid.setEnabled(False)
        '''
        self.a_vials_wid.setReadOnly(True)
        self.a_flow_wid.setReadOnly(True)
        self.a_min_flow_wid.setReadOnly(True)
        self.a_inc_flow_wid.setReadOnly(True)
        self.a_open_dur_wid.setReadOnly(True)
        self.a_rest_dur_wid.setReadOnly(True)
        self.a_num_trials_wid.setReadOnly(True)
        '''
        self.a_vial_lbl = QLabel('Vials:')
        self.a_flow_per_trial_lbl = QLabel('Total flow per trial (sccm):')
        self.a_flow_values_lbl = QLabel('Flow values to run (sccm):')
        #self.a_min_flow_lbl = QLabel('Min flow (per vial):')
        #self.a_inc_flow_lbl = QLabel('Increment flow by:')
        self.a_open_dur_lbl = QLabel('Vial open duration (s):')
        self.a_rest_dur_lbl = QLabel('Rest between trials (s):')
        self.a_num_trials_lbl = QLabel('Number of trials:')
        
        self.additive_parameters_layout.addRow(self.a_vial_lbl,self.a_vial_wid)
        self.additive_parameters_layout.addRow(self.a_flow_per_trial_lbl,self.a_flow_wid)
        self.additive_parameters_layout.addRow(self.a_flow_values_lbl,self.a_flow_vals_wid)
        #self.additive_parameters_layout.addRow(self.a_min_flow_lbl,self.a_min_flow_wid)
        #self.additive_parameters_layout.addRow(self.a_inc_flow_lbl,self.a_inc_flow_wid)
        self.additive_parameters_layout.addRow(self.a_open_dur_lbl,self.a_open_dur_wid)
        self.additive_parameters_layout.addRow(self.a_rest_dur_lbl,self.a_rest_dur_wid)
        self.additive_parameters_layout.addRow(self.a_num_trials_lbl,self.a_num_trials_wid)
        
        ##############################
        # GET SELECTED PARAMETERS FROM POPUP WINDOW
        # get list of vials
        vials_to_run_lbl = ', '.join(self.additive_program_window.vials_to_run)
        self.a_vial_wid.setText(vials_to_run_lbl)
        #self.a_vials_wid.setText(self.additive_program_window.flow_per_trial) #TODO
        self.a_flow_wid.setText(self.additive_program_window.flow_per_trial)
        self.a_flow_vals_wid.setText(self.additive_program_window.flow_values_to_run)
        #self.a_min_flow_wid.setText(self.additive_program_window.min_flow)
        #self.a_inc_flow_wid.setText(self.additive_program_window.inc_flow)
        self.a_open_dur_wid.setText(self.additive_program_window.open_dur)
        self.a_rest_dur_wid.setText(self.additive_program_window.rest_dur)
        self.a_num_trials_wid.setText(self.additive_program_window.num_trials)
        
        ##############################
        # ENABLE CHANGE PARAMETERS/START PROGRAM BUTTONS
        self.change_parameters_btn.setChecked(False)
        self.change_parameters_btn.setEnabled(True)
        self.program_start_btn.setEnabled(True)
        
        ##############################
        # HIDE POPUP WINDOW
        self.additive_program_window.hide()
    
    # PROGRAMS FOR 48-LINE OLFA
    def run_setpoint_characterization(self):
        
        # CHECK THAT PID IS CONNECTED
        try:
            if self.pid_nidaq.connectButton.isChecked() == False:
                logger.debug('connecting to PID')
                self.pid_nidaq.connectButton.toggle()
        except AttributeError as err:
            logger.warning('PID is not added as a device')
        except RuntimeError as err:
            logger.debug('no pid')
        
        # CHECK THAT OLFACTOMETER IS CONNECTED
        try:
            if self.olfactometer.connect_btn.isChecked() == False:
                logger.warning('Olfactometer not connected, attempting to connect')
                utils_olfa_48line.connect_to_48line_olfa(self.olfactometer)
        except AttributeError as err:   logger.error(err)
        
        # CHECK THAT OLFACTOMETER HAS ACTIVE SLAVES
        if self.olfactometer.active_slaves != []:
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
            
            # START RECORDING # TODO don't do this until it's READY to go
            if self.begin_record_btn.isChecked() == False:
                self.begin_record_btn.click()
            
            # START WORKER THREAD
            self.obj_sptchar.threadON = True
            self.thread_olfa.start()            # # start thread -> worker_sptChar iterates through stimuli
        else:
            logger.error('olfactometer has no active slaves - cannot run program')
            self.program_start_btn.setChecked(False)
    
    def run_additive_program(self):
        logger.info('run additive experiment')

        # CHECK THAT OLFACTOMETER IS CONNECTED
        try:
            if self.olfactometer.connect_btn.isChecked() == False:
                logger.warning('olfactometer not connected, attempting to connect')
                utils_olfa_48line.connect_to_48line_olfa(self.olfactometer)
        except AttributeError as err:   logger.error(err)
        
        # GET PROGRAM PARAMETERS
        additive_vials_to_run = copy.copy(self.additive_program_window.vials_to_run)
        if additive_vials_to_run != []:
            # GET SLAVE NAME
            self.slave_to_run = additive_vials_to_run[0]
            self.slave_to_run = self.slave_to_run[:-1]

            dur_ON = int(self.additive_program_window.open_dur_wid.text())
            dur_OFF = int(self.additive_program_window.rest_dur_wid.text())
            
            # GET STIMULUS LIST
            additive_stimulus_list = copy.copy(self.additive_program_window.vial_flows_complete_list)
            
            # GET DICTIONARIES FOR THESE VIALS
            these_sccm2Ard_dicts = []
            these_ard2Sccm_dicts = []
            for v in additive_vials_to_run:
                this_vial_num = v[1:]   # remove slave name
                vial_idx = int(this_vial_num) - 1
                for s in self.olfactometer.slave_objects:
                    if s.name == self.slave_to_run:
                        thisVial = s.vials[vial_idx]
                        sccm2Ard_dict_to_use = self.olfactometer.sccm2Ard_dicts.get(thisVial.cal_table)
                        ard2Sccm_dict_to_use = self.olfactometer.ard2Sccm_dicts.get(thisVial.cal_table)
                        these_sccm2Ard_dicts.append(sccm2Ard_dict_to_use)
                        these_ard2Sccm_dicts.append(ard2Sccm_dict_to_use)

            # SEND PARAMETERS TO ADDITIVE WORKER OBJECT
            self.obj_additive.vials_to_run = copy.copy(additive_vials_to_run)
            self.obj_additive.complete_stimulus_list = copy.copy(additive_stimulus_list)
            self.obj_additive.sccm2Ard_dict = copy.copy(these_sccm2Ard_dicts)
            self.obj_additive.ard2Sccm_dict = copy.copy(these_ard2Sccm_dicts)
            self.obj_additive.duration_on = copy.copy(dur_ON)
            self.obj_additive.duration_off = copy.copy(dur_OFF)
            
            # START RECORDING
            if self.begin_record_btn.isChecked() == False:
                self.begin_record_btn.click()
            
            # START WORKER THREAD
            self.obj_additive.threadON = True
            logger.debug('starting thread_additive')
            self.thread_additive.start()
        else:
            logger.info('No vials selected - cannot run program')
    
    def set_up_threads_sptchar(self):
        self.obj_sptchar = worker_sptChar()
        self.thread_olfa = QThread()
        self.obj_sptchar.moveToThread(self.thread_olfa)

        self.obj_sptchar.w_sendThisSp.connect(self.sendThisSetpoint)
        self.obj_sptchar.w_send_OpenValve.connect(self.send_OpenValve)
        self.obj_sptchar.w_incProgBar.connect(self.increment_progress_bar)
        self.obj_sptchar.finished.connect(self.threadIsFinished)
        self.thread_olfa.started.connect(self.obj_sptchar.exp)
    
    def set_up_threads_additive(self):
        self.obj_additive = worker_additive()
        self.thread_additive = QThread()
        self.obj_additive.moveToThread(self.thread_additive)

        self.obj_additive.w_sendThisSp.connect(self.sendThisSetpoint)
        self.obj_additive.w_send_OpenValve.connect(self.send_OpenValve)
        self.obj_additive.w_send_Command.connect(self.send_Command)
        self.obj_additive.w_incProgBar.connect(self.increment_progress_bar)
        self.obj_additive.finished.connect(self.threadIsFinished)
        self.thread_additive.started.connect(self.obj_additive.exp)
    
    def threadIsFinished(self):
        if self.obj_sptchar.threadON == True:
            self.obj_sptchar.threadON = False
            self.thread_olfa.exit()
            logger.debug('spt char program finished')
        if self.obj_additive.threadON == True:
            self.obj_additive.threadON = False
            self.thread_additive.exit()
            logger.debug('additive program finished')
        
        self.program_start_btn.setChecked(False)
        self.program_start_btn.setText('Start Program')
        self.program_progress_bar.setValue(0)
        logger.info('Finished program')

        # end recording
        if self.begin_record_btn.isChecked():
            self.end_record_btn.click()
    
    def active_slave_refresh(self):        
        # CHECK THAT OLFACTOMETER IS CONNECTED
        if self.olfactometer.connect_btn.isChecked() == False:
            utils_olfa_48line.connect_to_48line_olfa(self.olfactometer)
        
        # add the active slaves
        self.p_slave_select_wid.clear()
        self.p_slave_select_wid.addItems(self.olfactometer.active_slaves)
        if self.p_slave_select_wid.count() == 0:
            self.p_slave_select_wid.addItem(config_main.no_active_slaves_warning)
            self.program_start_btn.setEnabled(False)
        else:
            self.program_start_btn.setEnabled(True)
    ##############################
    

    ##############################
    ## FUNCTIONS USED BY WORKERS
    def sendThisSetpoint(self, vial_name:str, ard_val:int):
        strToSend = 'S_Sp_' + str(ard_val) + '_' + vial_name
        self.olfactometer.send_to_master(strToSend)
        
    def send_OpenValve(self, vial_name:str, dur:float):
        strToSend = 'S_OV_' + str(dur) + '_' + vial_name
        self.olfactometer.send_to_master(strToSend)

        # write to datafile
        self.receive_data_from_device('olfactometer ' + vial_name,'OV',str(dur))

    def send_Command(self, stringToSend:str):
        strToSend = stringToSend
        self.olfactometer.send_to_master(strToSend)
    ##############################
    
    
    ##############################
    ## ADD DEVICE/INSTRUMENT
    def add_olfa_48line_toggled(self,checked):  # TODO make sure this can't be untoggled while a program is running
        if checked:
            # Create Olfactometer Object
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
            
            # Directory for 48-line olfa
            self.olfa_48line_resultfiles_dir = main_datafile_directory + '\\48-line olfa'
            if not os.path.exists(self.olfa_48line_resultfiles_dir):
                os.mkdir(self.olfa_48line_resultfiles_dir)
                logger.debug('created 48-line olfa results files at %s',self.olfa_48line_resultfiles_dir)
            # Directory for 48-line olfa for today, get datafile number
            self.today_olfa_48line_resultfiles_dir = main_datafile_directory + '\\48-line olfa' + '\\' + current_date
            if os.path.exists(self.today_olfa_48line_resultfiles_dir):
                # check what files are in this folder
                list_of_files = os.listdir(self.today_olfa_48line_resultfiles_dir)
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
            if not os.path.exists(self.today_olfa_48line_resultfiles_dir):
                os.mkdir(self.today_olfa_48line_resultfiles_dir)
                logger.debug('created today folder at %s',self.today_olfa_48line_resultfiles_dir)   # TODO don't make this folder until it's time to start recording
                self.last_datafile_number = -1
            self.data_file_dir_lineEdit.setText(self.today_olfa_48line_resultfiles_dir)
            # update datafile number
            self.this_datafile_number = self.last_datafile_number + 1
            self.this_datafile_number_padded = str(self.this_datafile_number).zfill(2) # zero pad
            data_file_name = current_date + '_datafile_' + self.this_datafile_number_padded
            self.data_file_name_lineEdit.setText(data_file_name)
            
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
    ##############################
    

    def begin_record_btn_clicked(self):
        # Record button was checked- Begin Recording
        if self.begin_record_btn.isChecked() == True:
            logger.debug('begin record button clicked')
            self.begin_record_btn.setText('Pause Recording')
            self.end_record_btn.setEnabled(True)
            
            # Get file name & directory from GUI
            datafile_name = self.data_file_name_lineEdit.text()
            self.datafile_dir = self.data_file_dir_lineEdit.text() + '\\' + datafile_name + '.csv'
            
            # If directory does not already exist: Create it
            if not os.path.exists(self.data_file_dir_lineEdit.text()):
                os.mkdir(self.data_file_dir_lineEdit.text())
                logger.debug('created folder at %s', self.data_file_dir_lineEdit.text())
            
            # If file does not already exist: Create it & write header
            if not os.path.exists(self.datafile_dir):
                logger.info('Creating new file: %s (%s)', datafile_name, self.datafile_dir)
                File = datafile_name, ' '
                file_created_time = utils.get_current_time()
                file_created_time = file_created_time[:-4]
                Time = 'File Created: ', str(current_date + ' ' + file_created_time)
                # Write file header
                with open(self.datafile_dir,'a',newline='') as f:
                    writer = csv.writer(f,delimiter=',')
                    writer.writerow(File)
                    writer.writerow(Time)
                # Display (for the user)
                self.data_file_textedit.append(datafile_name)
                self.data_file_textedit.append('File Created: ' + str(current_date + ' ' + file_created_time))
                
                # If PID exists: write gain to file
                if self.add_pid_btn.isChecked() == True:
                    # if we are connected to it
                    if self.pid_nidaq.connectButton.isChecked() == True:
                        self.pid_gain = self.data_file_pid_gain.text()  # get value from widget
                        pid_line_header = 'PID gain: ', self.pid_gain
                        # write gain to file
                        with open(self.datafile_dir,'a',newline='') as f:
                            writer = csv.writer(f,delimiter=',')
                            writer.writerow(pid_line_header)
                        self.data_file_textedit.append('PID Gain: ' + self.pid_gain)

                # Write notes to file
                self.this_file_notes = self.data_file_notes_wid.text()
                notes_line_header = 'Notes: ', self.this_file_notes
                with open(self.datafile_dir,'a',newline='') as f:
                    writer = csv.writer(f,delimiter=',')
                    writer.writerow(notes_line_header)
                self.data_file_textedit.append('Notes: ' + self.this_file_notes)
                
                # If olfactometer exists: Write calibration tables to file
                try:
                    # if it's the 48-line one
                    if self.add_olfa_48line_btn.isChecked() == True:
                        # if she is connected
                        if self.olfactometer.connect_btn.isChecked() == True:
                            # open file so we can write to it
                            with open(self.datafile_dir,'a',newline='') as f:
                                writer = csv.writer(f,delimiter=',')
                                writer.writerow("")
                                write_this_row = 'Calibration Tables:',' '
                                writer.writerow(write_this_row)
                                
                                if (self.olfactometer.active_slaves != []):
                                    # list of all vials in active slaves
                                    self.vials_to_record_cal_table = []
                                    for s in self.olfactometer.active_slaves:
                                        for v in range(1,self.olfactometer.vialsPerSlave+1):
                                            this_string = s + str(v)
                                            self.vials_to_record_cal_table.append(this_string)
                                            # TODO figure out if we should just write all of them (this can probably be figured out once u write multi line programs)
                                    
                                    # Get calibration tables & write to file
                                    for full_vial_name in self.vials_to_record_cal_table:
                                        slave_name = full_vial_name[0]
                                        for s in self.olfactometer.slave_objects:
                                            # find the slave we want
                                            if s.name == slave_name:
                                                # find the vial we want
                                                vial_num = full_vial_name[1]
                                                vial_idx = int(vial_num) - 1
                                                this_vial = s.vials[vial_idx]
                                                this_vial_name = this_vial.full_vialNum
                                                this_vial_dict_name = this_vial.cal_table
                                                # write it to the file
                                                write_to_file = this_vial_name,this_vial_dict_name
                                                writer.writerow(write_to_file)
                                else:
                                    logger.warning('no calibration tables recorded to datafile (olfactometer does not have any active slaves)')
                
                # If olfactometer does not exist: Skip all this
                except AttributeError:
                    pass
                
                # Write variable headers to file
                DataHead = 'Time','Instrument','Unit','Value'
                with open(self.datafile_dir,'a',newline='') as f:
                    writer = csv.writer(f,delimiter=',')
                    writer.writerow("")
                    writer.writerow("")
                    writer.writerow(DataHead)
            
            # If file already exists
            else:
                logger.warning('File already exists: resuming recording to %s',self.datafile_dir)
        # Record button was unchecked - Pause Recording
        else:
            logger.info('Recording paused')
            self.begin_record_btn.setText('Resume Recording')
    
    def end_recording(self):
        logger.info('Ended recording to file: %s', self.data_file_name_lineEdit.text())        
        
        if self.add_olfa_48line_btn.isChecked() == True:
            # Check directory for last datafile number
            list_of_files = os.listdir(self.today_olfa_48line_resultfiles_dir)
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
        else:
            self.last_datafile_number = self.this_datafile_number + 1
        
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