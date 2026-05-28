'''
working_olfactometer.py


GUI for using both the olfactometer and final valve at the same time

ST 5/21/2026
'''

import sys, logging, time, random
from PyQt5 import sip
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from serial import SerialException

import olfactometry
import final_valve

config_file = 'olfa_config.json'

# Default values
dur_FV_open = 3
dur_vial_prep = 1
num_reps = 2
flow_rate = 100
dur_bt_trials = 5


def create_console_handler():
    console_handler_formatter = logging.Formatter('%(asctime)s : %(name)-14s :%(levelname)-8s: %(message)s',datefmt='%H:%M:%S')
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(console_handler_formatter)
    return console_handler

# CREATE LOGGER
logger = logging.getLogger(name='working olfa')
logger.setLevel(logging.DEBUG)
logger.propagate = False    # removes duplicate log messages
console_handler = create_console_handler()
logger.addHandler(console_handler)


class worker_program(QObject):
    finished = pyqtSignal()
    w_set_mfc = pyqtSignal()
    w_open_vial = pyqtSignal(int)
    w_close_vial = pyqtSignal(int)
    w_close_FV = pyqtSignal()
    w_open_FV = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.threadON = False
        self.complete_stimulus_list = []

        # All durations in seconds
        self.dur_FV_open = 0            # Duration of odor presentation
        self.dur_bt_trials = 0          # Duration between trials
        self.flow_rate = 0              # MFC flow rate
        self.vial_prep_time = 0
        
    @pyqtSlot()
    def exp(self):
        # Set MFC flow rate
        logger.info('worker: Setting MFC to %s SCCM', self.flow_rate)
        self.w_set_mfc.emit()

        # Wait for a sec
        time.sleep(1)

        # Iterate through stimulus list
        for stimulus in self.complete_stimulus_list:
            if self.threadON == True:
                full_vial_name = stimulus[0]
                
                # Open vial
                self.w_open_vial.emit(full_vial_name)

                # Wait to open FV
                time.sleep(self.vial_prep_time)

                # Open FV
                self.w_open_FV.emit()

                # Wait for duration of FV open
                time.sleep(self.dur_FV_open)
                
                # Close FV
                self.w_close_FV.emit()

                # Close vial
                self.w_close_vial.emit(full_vial_name)

                # Wait between trials
                time.sleep(self.dur_bt_trials - self.vial_prep_time)
        
        self.finished.emit()

class mainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.generate_ui()
        self.set_up_threads()

        self.mainLayout = QHBoxLayout()
        self.mainLayout.addWidget(self.settings_box)
        self.mainLayout.addWidget(self.device_groupbox)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.mainLayout)
        self.setCentralWidget(self.central_widget)
        self.setWindowTitle('Working Olfactometer')

    ##################################
    # UI
    def generate_ui(self):
        # SETTINGS GROUPBOX
        self.settings_box = QGroupBox('Settings')
        self.create_add_devices_box()
        self.create_olfa_settings_box()
        self.create_program_box()
        self.settings_layout = QVBoxLayout()
        self.settings_layout.addWidget(self.add_devices_groupbox)
        self.settings_layout.addWidget(self.olfa_settings_groupbox)
        self.settings_layout.addWidget(self.program_box)
        self.settings_box.setLayout(self.settings_layout)

        # DEVICES GROUPBOX
        self.device_groupbox = QGroupBox('Devices:')
        self.device_layout = QVBoxLayout()
        self.device_groupbox.setLayout(self.device_layout)
        x=1

    def create_add_devices_box(self):
        self.add_devices_groupbox = QGroupBox("Add/Remove Devices")

        self.add_olfa_btn = QPushButton(text='Add Olfactometer',checkable=True,toggled=self.add_olfa_btn_toggled)
        self.add_fv_btn = QPushButton(text='Add Final Valve',checkable=True,toggled=self.add_fv_toggled)

        layout = QVBoxLayout()
        layout.addWidget(self.add_olfa_btn)
        layout.addWidget(self.add_fv_btn)
        self.add_devices_groupbox.setLayout(layout)

    def create_olfa_settings_box(self):
        self.olfa_settings_groupbox = QGroupBox('Olfactometer Settings')
        
        self.config_file_name_wid = QLineEdit()
        self.config_file_name_wid.setText(config_file)
        self.config_file_name_wid.setToolTip("this is a placeholder, doesn't do anything right now")
        self.config_file_name_wid.setEnabled(False)

        layout = QVBoxLayout()
        layout.addWidget(self.config_file_name_wid)
        self.olfa_settings_groupbox.setLayout(layout)

    def create_program_box(self):
        self.program_box = QGroupBox('Program')
        # TODO gray it out until the devices are added

        layout = QFormLayout()
        layout.addRow(QLabel("Select vials:"))

        # Vials to do
        vial_button_layout = QHBoxLayout()
        self.vial_buttons = []
        # it would be nice to get this from the olfa but we will bare bones it for now
        self.vials = [5,6,7,8,9,10,11,12]
        for v in self.vials:
            vial_button = QPushButton(str(v),checkable=True)
            vial_button.setChecked(True)
            vial_button.setMaximumWidth(20)
            self.vial_buttons.append(vial_button)
            vial_button_layout.addWidget(vial_button)

        self.p_dur_FV_open_wid = QLineEdit(str(dur_FV_open))            # Duration of odor presentation (FV open)
        self.p_dur_vial_prep_time_wid = QLineEdit(str(dur_vial_prep))   # Time for vial to be open before final valve is open
        self.p_dur_vial_prep_time_wid.setToolTip("Duration vial is open before final valve opens\n(Time for odor to stabilize before presentation)")
        self.p_num_reps_wid = QLineEdit(str(num_reps))                  # Number of times to run each vial
        self.p_dur_bt_trials_wid = QLineEdit(str(dur_bt_trials))        # Duration between presentations
        self.p_dur_bt_trials_wid.setToolTip("Duration between last time final valve closed/next time to open it\nITI")
        self.p_flow_rate_wid = QLineEdit(str(flow_rate))                # MFC flow rate
        self.p_flow_rate_wid.setEnabled(False)

        self.program_start_btn = QPushButton(text='Start Program',checkable=True,toggled=self.program_start_clicked)

        layout.addRow(vial_button_layout)
        layout.addRow(QLabel("Duration FV open (s):"),self.p_dur_FV_open_wid)
        layout.addRow(QLabel("Duration vial prep (s):"),self.p_dur_vial_prep_time_wid)
        layout.addRow(QLabel("Duration bt trials (s):"),self.p_dur_bt_trials_wid)
        layout.addRow(QLabel("Num repetitions:"),self.p_num_reps_wid)
        layout.addRow(QLabel("MFC flow rate (SCCM):"),self.p_flow_rate_wid)
        layout.addRow(self.program_start_btn)
        self.program_box.setLayout(layout)
    ##################################

    
    ##################################
    # ADD DEVICES
    def add_olfa_btn_toggled(self, checked):
        if checked:
            logger.debug('adding olfactometer')
            self.add_olfa_btn.setText('Remove Olfactometer')
            # Create olfactometer
            try:
                self.olfas = olfactometry.Olfactometers(parent=self)
                #for olfa in self.olfas:
                # fuck it assume one for now
                self.olfactometer = self.olfas[0]
                # add it to the layout
                self.device_layout.addWidget(self.olfactometer)
            except SerialException:
                print('com port bad')
                self.add_olfa_btn.setChecked(False)

        else:
            logger.debug('removing olfactometer')
            self.add_olfa_btn.setText('Add Olfactometer')
            try:
                # make sure you disconnect the com port
                self.olfactometer.serial.close()
                self.mainLayout.removeWidget(self.olfactometer)
                sip.delete(self.olfactometer)
            except AttributeError:
                logger.debug('no olfactometer')
            #except RuntimeError:
            #    print('cant remove bc it already gone')
            #    print('this shouldnt happen')
    
    def add_fv_toggled(self, checked):
        if checked:
            logger.debug('adding final valve')
            self.add_fv_btn.setText('Remove Final Valve')
            self.final_valve = final_valve.Final_Valve()
            self.device_layout.addWidget(self.final_valve)

        else:
            logger.debug('removing final valve')
            self.add_fv_btn.setText('Add Final Valve')
            self.mainLayout.removeWidget(self.final_valve)
            sip.delete(self.final_valve)
    ##################################

    
    ##################################
    # THREADS
    def set_up_threads(self):
        # Create worker and thread
        self.obj_worker = worker_program()
        self.thread_program = QThread()
        self.obj_worker.moveToThread(self.thread_program)

        # Connect worker functions to stuff here
        self.obj_worker.w_set_mfc.connect(self.set_mfc)
        self.obj_worker.w_open_vial.connect(self.open_vial)
        self.obj_worker.w_close_vial.connect(self.close_vial)
        self.obj_worker.w_open_FV.connect(self.open_FV)
        self.obj_worker.w_close_FV.connect(self.close_FV)
        
        self.obj_worker.finished.connect(self.thread_is_finished)
        self.thread_program.started.connect(self.obj_worker.exp)

    def program_start_clicked(self,checked):
        if checked:
            self.program_start_btn.setText('End Program')
            self.program_start_btn.setToolTip("this won't work yet sorry you gotta wait it out")    # TODO
            
            self.run_program()

        else:
            self.program_start_btn.setText("Start program")
            self.thread_is_finished()
    
    def run_program(self):
        logger.info('starting program')
        
        # CHECK THAT DEVICES ARE CONNECTED
        # TODO make this a try/except
        if self.add_olfa_btn.isChecked() == False:
            logger.warning('No olfa connected, this is about to fail')
            #self.add_olfa_btn.toggle()
        if self.add_fv_btn.isChecked() == False:
            logger.warning('No final valve connected, this is about to fail')
            # TODO check if connected to arduino
        
        
        # GET PROGRAM PARAMETERS
        flow_rate = int(self.p_flow_rate_wid.text())
        dur_vial_prep = int(self.p_dur_vial_prep_time_wid.text())
        dur_fv_open = int(self.p_dur_FV_open_wid.text())
        n_rep = int(self.p_num_reps_wid.text())
        dur_bt_trials = int(self.p_dur_bt_trials_wid.text())
        

        # CREATE STIMULUS LIST
        vials_complete_list = []
        #for v in self.olfactometer.vials:
        for v in self.vial_buttons:
            # see which is checked
            vial_is_checked = v.isChecked()
            if vial_is_checked == True:
                this_vial_num = int(v.text())
                temp = [this_vial_num]*n_rep
                vials_complete_list.append(temp)
        random.shuffle(vials_complete_list)
        self.stimulus_list = vials_complete_list
        
        # SEND PARAMETERS TO WORKER
        self.obj_worker.complete_stimulus_list = self.stimulus_list
        self.obj_worker.dur_FV_open = dur_fv_open
        self.obj_worker.vial_prep_time = dur_vial_prep
        self.obj_worker.dur_bt_trials = dur_bt_trials
        self.obj_worker.flow_rate = flow_rate

        # START WORKER THREAD
        self.obj_worker.threadON = True
        self.thread_program.start()

    def thread_is_finished(self):
        # End the thread
        if self.obj_worker.threadON == True:
            self.obj_worker.threadON == False
            self.thread_program.exit()
            self.thread_program.wait()
            if self.thread_program.isRunning() == False:
                logger.debug('Program is finished')
        
        # Reset the GUI
        if self.program_start_btn.isChecked() == True:
            self.program_start_btn.setChecked(False)
        self.program_start_btn.setText('Start Program')
        #self.program_progress_bar.setValue(0)  # TODO
        logger.info('Finished program')
        
    ##################################



    ##################################
    ## FUNCTIONS USED BY WORKERS
    def set_mfc(self):
        # TODO
        logger.warning("this doesn't do anything")

    def open_vial(self, vial_name:int):
        logger.info('Opening vial %s', str(vial_name))
        self.olfactometer.set_vial(vial_name)
        
    def close_vial(self,vial_name:int):
        logger.info('Closing vial %s', str(vial_name))
        self.olfactometer.set_vial(vial_name)

    def open_FV(self):
        logger.info('Opening final valve')
        self.final_valve.final_valve_button.setChecked(True)

    def close_FV(self):
        logger.info('Closing final valve')
        self.final_valve.final_valve_button.setChecked(False)

    ##################################

if __name__ == "__main__":
    app1 = QApplication(sys.argv)
    theWindow = mainWindow()
    theWindow.show()
    sys.exit(app1.exec_())