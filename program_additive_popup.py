
import logging, random
from PyQt5.QtWidgets import *

import utils, config_main


# CREATE LOGGER
logger = logging.getLogger(name='vial popup')
logger.setLevel(logging.DEBUG)
if logger.hasHandlers():    logger.handlers.clear()     # removes duplicate log messages
console_handler = utils.create_console_handler()
logger.addHandler(console_handler)

# DEFAULT VALUES
def_flow_per_trial = 100
def_min_flow = 10
def_max_flow = 100
def_inc_flow = 10


class additiveProgramSettingsPopup(QWidget):
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.olfactometer_object = self.parent.olfactometer
        self.vials_to_run = []
        self.vial_flows_complete_list = []

        self.create_ui_features()
        self.setWindowTitle('Additive Program Details')
        self.hide()


    def create_ui_features(self):
        self.parameter_set_button = QPushButton(text="Set Parameters",checkable=True,toggled=self.parameter_set_toggled)
        self.create_vial_selection_box()
        self.create_trial_settings_box()
        
        layout = QHBoxLayout()
        layout.addWidget(self.vial_selection_box)
        layout.addWidget(self.trial_settings_box)
        self.setLayout(layout)

    def create_vial_selection_box(self):
        self.vial_selection_box = QGroupBox('Vial Selection')

        # each row has a button with the vial name
        self.layout_vial_selection = QVBoxLayout()

        # check how many slaves are active
        currently_active_slaves = self.olfactometer_object.active_slaves
        
        self.slave_layouts = []
        self.slave_vial_btn_objects_array = []
        # for each column (slave):
        for s in currently_active_slaves:
            this_layout = QVBoxLayout()
            self.vial_btn_objects = []
            for v in range(0,self.olfactometer_object.vialsPerSlave):
                vial_name = s + str(v+1)
                this_btn = QPushButton(text=vial_name,checkable=True)
                self.vial_btn_objects.append(this_btn)
                this_layout.addWidget(this_btn)
            self.slave_layouts.append(this_layout)
            self.slave_vial_btn_objects_array.append(self.vial_btn_objects)

        for l in self.slave_layouts:
            self.layout_vial_selection.addLayout(l)

        self.vial_selection_box.setLayout(self.layout_vial_selection)

    def create_trial_settings_box(self):
        self.trial_settings_box = QGroupBox('Trial Settings')

        self.flow_per_trial_lbl = QLabel('Total flow per trial (sccm):')
        self.flow_per_trial_wid = QLineEdit(text=str(def_flow_per_trial))
        self.min_flow_lbl = QLabel('Min flow (per vial):')
        self.min_flow_wid = QLineEdit(text=str(def_min_flow))
        #self.max_flow_lbl = QLabel('Max flow (per vial):')
        #self.max_flow_wid = QLineEdit(text=str(def_max_flow))
        self.inc_flow_lbl = QLabel('Increment flow by:')
        self.inc_flow_wid = QLineEdit(text=str(def_inc_flow))
        self.open_dur_lbl = QLabel('Vial open duration (s):')
        self.open_dur_wid = QLineEdit(text=str(config_main.default_dur_ON))
        self.rest_dur_lbl = QLabel('Rest between trials (s):')
        self.rest_dur_wid = QLineEdit(text=str(config_main.default_dur_OFF))
        self.num_trials_lbl = QLabel('Number of trials:')
        self.num_trials_wid = QLineEdit(text=str(config_main.default_numTrials))
        
        
        layout = QFormLayout()
        layout.addRow(self.flow_per_trial_lbl,self.flow_per_trial_wid)
        layout.addRow(self.min_flow_lbl,self.min_flow_wid)
        #layout.addRow(self.max_flow_lbl,self.max_flow_wid)
        layout.addRow(self.inc_flow_lbl,self.inc_flow_wid)
        layout.addRow(self.open_dur_lbl,self.open_dur_wid)
        layout.addRow(self.rest_dur_lbl,self.rest_dur_wid)
        layout.addRow(self.num_trials_lbl,self.num_trials_wid)

        layout.addRow(self.parameter_set_button)

        self.trial_settings_box.setLayout(layout)
        
    def parameter_set_toggled(self,checked):
        if checked:
            logger.debug('parameters have been set')
            
            # get which vials are selected
            self.vials_to_run = []
            # for number of slaves:
            for s in range(len(self.slave_layouts)):
                # for each vial:
                for v in range(0,self.olfactometer_object.vialsPerSlave):
                    # check if button is selected or not
                    if self.slave_vial_btn_objects_array[s][v].isChecked() == True:
                        # if button is checked, it needs to be used in this trial
                        self.vials_to_run.append(self.slave_vial_btn_objects_array[s][v].text())

            # get all parameters
            self.flow_per_trial = self.flow_per_trial_wid.text()
            self.min_flow = self.min_flow_wid.text()
            #self.max_flow = self.max_flow_wid.text()
            self.inc_flow = self.inc_flow_wid.text()
            self.open_dur = self.open_dur_wid.text()
            self.rest_dur = self.rest_dur_wid.text()
            self.num_trials = self.num_trials_wid.text()

            # create stimulus list
            self.create_stimulus_list()
            
            # tell the main window parameters have been set
            self.parent.additive_parameters_display()

            # gray everything out so user cannot select
            self.vial_selection_box.setEnabled(False)
            self.trial_settings_box.setEnabled(False)
            
            # TODO close this window????

        else:
            logger.debug('parameters are available to be changed')
            #self.parameter_set_button.setText("Set Parameters")

            self.vial_selection_box.setEnabled(True)
            self.trial_settings_box.setEnabled(True)
            

    def create_stimulus_list(self):
        self.vial_flows_complete_list = []

        # check number of vials selected
        num_vials_to_run = len(self.vials_to_run)

        # convert everything to ints or whatever
        total_flow_per_trial = int(self.flow_per_trial)
        min_flow = int(self.min_flow)
        inc_flow = int(self.inc_flow)
        num_trials = int(self.num_trials)

        # create list of setpoints (2 or 3 vials)
        random_max_gen_value = round(total_flow_per_trial/inc_flow)
        min_for_random = round(min_flow / inc_flow)

        # for each trial
        for i in range(num_trials):
            # get setpoints
            this_trial_setpoints = []

            # generate first setpoint
            sccmVal1 = random.randint(min_for_random,random_max_gen_value)
            sccmVal1 = sccmVal1 * inc_flow
            sccmVal2 = total_flow_per_trial - sccmVal1
            
            this_trial_setpoints.append(sccmVal1)
            this_trial_setpoints.append(sccmVal2)
            
            '''
            if num_vials_to_run == 3 or 2:
                max_for_first_setpoint = total_flow_per_trial - ((num_vials_to_run-1)*min_flow)
                if max_for_first_setpoint != 0:
                    sccmVal1 = random.randint(min_flow,max_for_first_setpoint)
                else:
                    sccmVal1 = 0
                this_trial_setpoints.append(sccmVal1)
                remaining_flow = total_flow_per_trial-sccmVal1
                if num_vials_to_run == 2:
                    sccmVal2 = random.randint(min_flow,remaining_flow)
                    this_trial_setpoints.append(sccmVal2)
                if num_vials_to_run == 3:
                    max_for_second_setpoint = remaining_flow - min_flow
                    sccmVal2 = random.randint(min_flow,max_for_second_setpoint)
                    this_trial_setpoints.append(sccmVal2)
                    remaining_flow = total_flow_per_trial - (sccmVal1+sccmVal2)
                    sccmVal3 = random.randint(min_flow,remaining_flow)
                    this_trial_setpoints.append(sccmVal3)
                
            else:
                logger.warning('%s vials selected, must be 2 or 3 vials', num_vials_to_run)
            '''
            
            self.vial_flows_complete_list.append(this_trial_setpoints)
            
        '''
        # create list of setpoints
        for i in range(num_trials):
            this_trial_setpoints = []
            max_for_first_setpoint = total_flow_per_trial-((num_vials_to_run-1)*min_flow)

            sccmVal1 = random.randint(min_flow,max_for_first_setpoint)
            this_trial_setpoints.append(sccmVal1)
            remaining = total_flow_per_trial-sccmVal1
            for num_vials in range(num_vials_to_run-1):
                this_vial_num = num_vials+2
                # if it's not the last one
                if this_vial_num == num_vials_to_run:
                    max_for_this_setpoint = remaining
                else:
                    max_for_this_setpoint = remaining-((num_vials+1)*min_flow)
                try:
                    next_sccm_val = random.randint(min_flow,max_for_this_setpoint)
                    remaining = remaining - next_sccm_val
                    this_trial_setpoints.append(next_sccm_val)
                except ValueError as err:
                    logger.debug('max for first setpoint: %s',max_for_first_setpoint)
                    logger.debug('sccmVal1:\t%s',sccmVal1)
                    logger.debug('total number of vials: %s',num_vials_to_run)
                    logger.debug('this vial num: %s',this_vial_num)
                    logger.debug('this_trial_setpoints: %s',this_trial_setpoints)
                    logger.debug('max for this setpoint: %s',max_for_this_setpoint)
                    logger.debug('num_vials:\t%s',num_vials)
            
            self.vial_flows_complete_list.append(this_trial_setpoints)
        '''
