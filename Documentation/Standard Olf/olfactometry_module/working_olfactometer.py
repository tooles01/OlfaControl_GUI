'''
working_olfactometer.py


GUI for using both the olfactometer and final valve at the same time

ST 5/21/2026
'''

import sys, logging
from PyQt5 import sip
from PyQt5.QtWidgets import *
from serial import SerialException
import olfactometry
import final_valve

config_file = 'olfa_config.json'

# TODO: error checking for if no olfactometer connected

def create_console_handler():
    console_handler_formatter = logging.Formatter('%(asctime)s : %(name)-14s :%(levelname)-8s: %(message)s',datefmt='%H:%M:%S')
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(console_handler_formatter)
    return console_handler

# CREATE LOGGER
logger = logging.getLogger(name='working olfactometer')
logger.setLevel(logging.DEBUG)
if logger.hasHandlers():    logger.handlers.clear()     # removes duplicate log messages
console_handler = create_console_handler()
logger.addHandler(console_handler)

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
        self.setWindowTitle('Working Olfactometer')


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

        layout = QVBoxLayout()
        layout.addWidget(self.config_file_name_wid)
        self.olfa_settings_groupbox.setLayout(layout)

    def create_program_box(self):
        self.program_box = QGroupBox('Program')

        layout = QVBoxLayout()
        layout.addWidget(QLabel("it's coming"))
        self.program_box.setLayout(layout)


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

if __name__ == "__main__":
    app1 = QApplication(sys.argv)
    theWindow = mainWindow()
    theWindow.show()
    sys.exit(app1.exec_())