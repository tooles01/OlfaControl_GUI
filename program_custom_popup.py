import sys
import os, logging, utils
from PyQt5.QtWidgets import *
from PyQt5 import sip
import pandas as pd

##############################
# CREATE LOGGER
main_datafile_directory = utils.find_log_directory()
if not os.path.exists(main_datafile_directory): os.mkdir(main_datafile_directory)   # if folder doesn't exist, make it
logger = logging.getLogger(name='Custom Program')
logger.setLevel(logging.DEBUG)
if logger.hasHandlers():    logger.handlers.clear()     # removes duplicate log messages
console_handler = utils.create_console_handler()
file_handler = utils.create_file_handler(main_datafile_directory)
logger.addHandler(console_handler)
logger.addHandler(file_handler)
##############################

default_num_trials = 3
default_flow_value = 10


class custom_program_popup(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.olfactometer_object = self.parent.olfactometer
        
        # 11/7/2025: might remove, putting here bc we know these get used later
        self.vial_names_list = []
        self.all_trials_widgets_list = []

        # 11/13/2025
        self.trial_data_from_file = []
        self.vials_to_use = []

        self.num_trials = default_num_trials

        self.create_ui_features()
        #self.setSizePolicy(QSizePolicy.Minimum)    # this don't work
        self.setMaximumWidth(self.sizeHint().width())
        self.setWindowTitle('Custom Program Details')
        self.hide()

    
    def create_ui_features(self):
        # Create Manual Entry Widgets

        # Number of trials
        label = QLabel('Enter # of trials:')
        self.num_trials_wid = QLineEdit(str(default_num_trials))
        self.update_template_btn = QPushButton('Update Template')
        self.update_template_btn.setToolTip('Update the number of trials\n'
                                            'WARNING: This will remove data from an uploaded file and autopopulate the boxes')
        self.num_trials_wid.returnPressed.connect(self.update_template)
        self.update_template_btn.clicked.connect(self.update_template)
        layout1 = QHBoxLayout()
        layout1.addWidget(label)
        layout1.addWidget(self.num_trials_wid)
        layout1.addWidget(self.update_template_btn)

        # Buttons for auto populate or upload file or done
        self.upload_file_btn = QPushButton('Upload file')
        self.upload_file_btn.setToolTip('This does nothing right now lol')
        self.upload_file_btn.clicked.connect(self.upload_file_btn_clicked)  # Temp 11/13/2025
        self.auto_pop_btn = QPushButton('Auto populate flow rates')
        self.auto_pop_btn.clicked.connect(self.auto_populate_clicked)
        self.done_btn = QPushButton('Done')
        self.done_btn.setToolTip('Close window and create stimulus list')
        self.done_btn.clicked.connect(self.done_btn_clicked)
        layout2 = QHBoxLayout()
        layout2.addWidget(self.upload_file_btn)
        layout2.addWidget(self.auto_pop_btn)
        layout2.addWidget(self.done_btn)

        # Trial Template
        logger.debug('Generating template')
        self.regenerate_template()  # this requires vials_to_use and num_trials
        #self.generate_template()

        # Main Layout
        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(layout1)
        self.main_layout.addLayout(layout2)
        self.main_layout.addWidget(self.template_groupbox)
        self.setLayout(self.main_layout)

        self.upload_file_btn.setMaximumWidth(130)
        self.auto_pop_btn.setMaximumWidth(130)
        self.done_btn.setMaximumWidth(130)

    def generate_template(self):
        '''
        Creates template_groupbox:

            Creates vial number labels
                Gets currently active slaves from olfactometer
                Gets vial numbers for that slave, adds labels for them
            For number of trials (from num_trials widget)
                Adds Trial # label
                For each vial: Adds flow widget, adds to list of flow widgets for this trial
                Add list of this trial widgets to self.all_trials_widgets_list
                    (List of all trials)
                    (For each trial, contains a list of the flow widgets)
        '''

        logger.debug('Generating template')
        self.template_groupbox = QGroupBox("Template")
        
        # Get available vials
        #currently_active_slaves = self.olfactometer_object.active_slaves
        currently_active_slaves = 'A'   # TEMP 10/23/2025
        try:
            currently_active_slave_name = currently_active_slaves[0]    # Hopefully there is only one lol
            self.num_trials = int(self.num_trials_wid.text())   # Get number of trials
            self.grid_layout = QGridLayout()
            
            ##############################
            # VIAL NUMBER LABELS
            self.vial_names_list = []   # For creating stimulus list later
            slave_object = []   # Get the slave object
            for s_obj in self.olfactometer_object.slave_objects:
                if s_obj.name == currently_active_slave_name:
                    slave_object = s_obj    # this is the object we want
                    break
            # Get the vial numbers from that slave, add these labels
            for vial in slave_object.vials:
                vial_name = vial.full_vialNum
                this_label = QLabel(vial_name)
                self.grid_layout.addWidget(this_label,0,int(vial.vialNum))
                self.vial_names_list.append(vial_name)
            
            ##############################
            # ROWS FOR EACH TRIAL
            num_vials = len(slave_object.vials)
            self.all_trials_widgets_list = []    # list of lists --> all_trials_list[0] = row 1 --> row 1 is a list of the widgets
            for row in range(self.num_trials):
                # Trial # label
                this_row_label = QLabel(str(row+1))
                self.grid_layout.addWidget(this_row_label,row+1,0)   # +1 because row 0 is the header
                
                # Flow value boxes
                this_trial_flow_widgets = []    # List of flow widgets for this trial
                for col in range(num_vials):
                    flow_widget = QLineEdit(str(default_flow_value))
                    flow_widget.setToolTip('Enter flow rate')
                    self.grid_layout.addWidget(flow_widget, row+1, col+1)
                    flow_widget.setFixedWidth(40)    # TEMP 10/23/2025
                    this_trial_flow_widgets.append(flow_widget)
                self.all_trials_widgets_list.append(this_trial_flow_widgets)
            
            self.template_groupbox.setLayout(self.grid_layout)
        
        except IndexError as err:
            logger.warning('Cannot generate template, no currently active slaves')
            self.parent.program_selection_btn.setChecked(False)
            self.hide()
    
    def update_template(self):
        # Deletes current template & regenerates with the new # of trials we need
        logger.debug('Updating template')
        
        sip.delete(self.template_groupbox)
        self.generate_template()
        self.main_layout.addWidget(self.template_groupbox)
    
    
    def auto_populate_clicked(self):
        logger.debug('Populating template')
        
        # Create the whole list of values
        
        # Add them into the groupbox
        
        logger.error('This does nothing right now lol')


    
    def create_stimulus_list(self):
        ''' self.complete_stimulus_list:    List of dicts, each dict has keys (vial names) and values (flow rate) '''
        
        logger.debug('Creating stimulus list!!!!')
        self.complete_stimulus_list = [] # List of dicts

        # For each trial (row of widgets):
        for this_trial_widgets in self.all_trials_widgets_list:    
            # Get the flow rate from each vial's widget & add to this_trial_dict
            this_trial_dict = {}    # Blank dict for this trial
            for idx, flow_rate_widget in enumerate(this_trial_widgets):
                this_vial_name = self.vial_names_list[idx]          # Get the vial name
                this_flow_rate = float(flow_rate_widget.text())     # Get the flow rate
                this_trial_dict[this_vial_name] = this_flow_rate    # Add vial number & flow rate to dict for this trial

            # Add to complete_stimulus_list
            self.complete_stimulus_list.append(this_trial_dict) # list of dicts
    
    def done_btn_clicked(self):
        ''' Creates stimulus list and hides window '''

        logger.debug('Done setting parameters')
        self.create_stimulus_list()     # Create stimulus list
        logger.debug('Closing custom program window')
        self.hide()     # Close window
        self.parent.program_selection_btn.setChecked(False)
        
    def upload_file_btn_clicked(self):
        # Temporary 11/13/2025
        file_path = 'C:\\Users\\Admin\\NYU Langone Health Dropbox\\Shannon Toole\\OlfactometerEngineeringGroup (2)\\Control\\a_software\\OlfaControl_GUI\\'
        #file_name = 'Designment_Olfactometer.xlsx'
        file_name = 'Designment_Olfactometer - Copy.xlsx'
        #file_name = 'Designment_Olfactometer_2.xlsx'
        #file_name = 'Designment_Olfactometer_3.xlsx'
        file_selected = file_path + file_name
        logger.info('Loading file: \t%s', file_name)

        self.get_data_from_excel_file(file_selected)    # Get the data, put into self.trial_data_from_file
        sip.delete(self.template_groupbox)              # Delete current template
        self.regenerate_template()          # Regenerate template
        self.put_file_data_into_widgets()   # Put data into widgets

        # Update layout
        self.num_trials_wid.setText(str(self.num_trials))   # Update the lil num trials widget
        self.main_layout.addWidget(self.template_groupbox)  # Re-add to main layout
        
        '''
        # Open file select dialog
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.ExistingFile)   # The name of a single existing file
        dlg.setNameFilter("Excel Files (*.xlsx)")   # Set file filter to .xlsx
        
        # When file has been selected, go get the data
        if dlg.exec():
            file_selected = dlg.selectedFiles()
            file_selected = file_selected[0]
            logger.debug('User has selected file: %s', file_selected)
            
            self.get_data_from_excel_file(file_selected)    # Get the data, put into self.trial_data_from_file
            self.regenerate_template()          # Regenerate template            
            self.put_file_data_into_widgets()   # Put data into widgets

            # Update layout
            self.num_trials_wid.setText(str(self.num_trials))   # Update the lil num trials widget
            self.main_layout.addWidget(self.template_groupbox)  # Re-add to main layout
        '''
        
    def get_data_from_excel_file(self, excel_file):
        
        # Read file into a pandas DataFrame
        df = pd.read_excel(excel_file,header=0)
        
        # Put each trial (row) into the list of dicts
        self.trial_data_from_file = []
        for row in df.itertuples(index=False):  # For each row (iterate over DataFrame rows as namedtuples)
            this_row = row._asdict()    # Convert this row to a dict
            # Append (valid rows) to self.trial_data_from_file (list of dicts)
            try:
                has_non_numeric = any(not isinstance(value, (int, float)) for value in this_row.values())   # Get if any values are NOT int or float
                if (has_non_numeric is True) or (this_row['Trial'] != this_row['Trial']):
                    pass    # If there are any values that are (not int or float) OR (are NaN), skip this row
                else:
                    self.trial_data_from_file.append(this_row)
            except KeyError as err:
                logger.error("Please make sure column A header is 'Trial', %s", err)

        header_row = list(df.columns)       # Here's all the column headers
        self.vials_to_use = header_row[1:]       # we want the vial numbers to be these
        self.num_trials = len(self.trial_data_from_file)  # Get number of trials
        
    def regenerate_template(self):
        # GENERATE TEMPLATE (using vials_to_use and # of trials)
        
        # Create groupbox
        self.template_groupbox = QGroupBox("Template")
        self.grid_layout = QGridLayout()

        # Create vial number labels
        self.vial_names_list = []   # For creating stimulus list later
        for idx, vial_name in enumerate(self.vials_to_use):
            this_label = QLabel(vial_name)
            self.grid_layout.addWidget(this_label,0,int(idx+1))  # unclear if i need +1 here
            self.vial_names_list.append(vial_name)

        # Create rows for each trial
        num_vials = len(self.vials_to_use)
        self.all_trials_widgets_list = []
        for row in range(self.num_trials):
            # Trial # label
            this_row_label = QLabel(str(row+1))
            self.grid_layout.addWidget(this_row_label,row+1,0)   # +1 because row 0 is the header

            # Flow value boxes
            this_trial_flow_widgets = []
            for col in range(num_vials):
                flow_widget = QLineEdit('0')    # 11/13/2025 NOTE: does not use vials_to_use
                self.grid_layout.addWidget(flow_widget,row+1,col+1)
                flow_widget.setFixedWidth(40)
                this_trial_flow_widgets.append(flow_widget)

            self.all_trials_widgets_list.append(this_trial_flow_widgets)


    def put_file_data_into_widgets(self):
        # PUT FILE DATA INTO THE WIDGETS
        
        # For each trial (dict) in self.trial_data_from_file (list)
        for trial in self.trial_data_from_file:
            try:
                trial_number = trial['Trial']   # Get the trial number
                list_idx = trial_number - 1     # Row to put the data into
                widgets_for_this_trial = self.all_trials_widgets_list[list_idx]     # List of widgets in this row

                try:
                    # For each vial listed in the file, put flow value into its widget
                    for idx, vial in enumerate(self.vials_to_use):
                        this_vial_flow_rate = trial[vial]
                        widgets_for_this_trial[idx].setText(str(this_vial_flow_rate))
                except KeyError:
                    logger.error('Please make sure vial names are listed correctly in header')
            
            except KeyError as err:
                logger.error("Please make sure column A header is 'Trial', %s", err)

        # Put it all back into the layout
        self.template_groupbox.setLayout(self.grid_layout)




if __name__ == "__main__":
    app1 = QApplication(sys.argv)
    theWindow = custom_program_popup()
    theWindow.show()
    sys.exit(app1.exec_())



