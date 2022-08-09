# flowSensor_driver.py
# for Honeywell 5100V

import os, sys, logging, csv
from PyQt5 import QtCore, QtSerialPort
from PyQt5.QtWidgets import *
from serial.tools import list_ports
import utils, utils_olfa_48line

currentDate = utils.currentDate
noPortMsg = ' ~ No COM ports detected ~'

flowSens_baud = 9600
sensorType = "Honeywell 5101V"  # TODO
calibration_table_item_number = 4


# CREATE LOGGER
logger = logging.getLogger(name='flow sensor')
logger.setLevel(logging.DEBUG)
if logger.hasHandlers():    logger.handlers.clear()     # removes duplicate log messages
console_handler = utils.create_console_handler()
logger.addHandler(console_handler)

class flowSensor(QGroupBox):

    def __init__(self, port=""):
        super().__init__()
        self.port = port
        self.connected = False
        
        self.createConnectBox()
        self.create_settings_box()
        self.create_cal_table_box()
        self.createDataReceiveBoxes()

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.connectBox,0,0,)
        mainLayout.addWidget(self.settings_box,1,0)
        mainLayout.addWidget(self.cal_table_box,2,0)
        mainLayout.addWidget(self.dataReceiveBox,0,1,3,1)
        self.setLayout(mainLayout)

        self.settings_box.setMaximumHeight(self.settings_box.sizeHint().height())
        self.cal_table_widget.setFixedHeight(100)
        self.cal_table_box.setFixedHeight(self.cal_table_box.sizeHint().height())
        self.dataReceiveBox.setFixedWidth(self.dataReceiveBox.sizeHint().width())
    
    # CREATE GUI ELEMENTS
    def createConnectBox(self):
        self.connectBox = QGroupBox("Connect")

        self.portLbl = QLabel(text="Port/Device:")
        self.port_widget = QComboBox(currentIndexChanged=self.portChanged)
        self.connectButton = QPushButton(checkable=True,toggled=self.toggled_connect)
        self.refreshButton = QPushButton(text="Refresh",clicked=self.getPorts)
        self.getPorts()

        self.connectBoxLayout = QFormLayout()
        self.connectBoxLayout.addRow(self.portLbl,self.port_widget)
        self.connectBoxLayout.addRow(self.refreshButton,self.connectButton)
        self.connectBox.setLayout(self.connectBoxLayout)

    def create_settings_box(self):
        self.settings_box = QGroupBox('Settings')
        
        self.timebtreqs_wid = QLineEdit(text='100',returnPressed=lambda:self.send_to_arduino('MM_timebt_' + self.timebtreqs_wid.text()))
        self.timebtreqs_btn = QPushButton(text="Send", clicked=lambda:self.send_to_arduino('MM_timebt_' + self.timebtreqs_wid.text()))
        
        layout = QHBoxLayout()
        layout.addWidget(QLabel(text="Time b/t acquisitions (ms):"))
        layout.addWidget(self.timebtreqs_wid)
        layout.addWidget(self.timebtreqs_btn)
        self.settings_box.setLayout(layout)
    
    def create_cal_table_box(self):
        self.cal_table_box = QGroupBox('Calibration table')
        
        self.get_calibration_tables()
        self.cal_table_widget = QListWidget()
        self.cal_table_widget.addItems(self.sccm2Ard_dicts)
        default_cal_table_item = self.cal_table_widget.item(calibration_table_item_number)
        self.cal_table_widget.setCurrentItem(default_cal_table_item)
        
        self.cal_table_btn = QPushButton('Set calibration table',checkable=True,toggled=self.cal_tbl_btn_toggled)
        if self.cal_table_btn.isChecked() == False:
            self.cal_table_btn.toggle()
        
        layout = QVBoxLayout()
        layout.addWidget(self.cal_table_widget)
        layout.addWidget(self.cal_table_btn)
        self.cal_table_box.setLayout(layout)
    
    def createDataReceiveBoxes(self):
        self.dataReceiveBox = QGroupBox("data received")

        self.receiveBox = QTextEdit(readOnly=True)
        receiveBoxLbl = QLabel(text="Flow val (int), Flow val (SCCM)")
        receiveBoxLayout = QVBoxLayout()
        receiveBoxLayout.addWidget(receiveBoxLbl)
        receiveBoxLayout.addWidget(self.receiveBox)

        layout = QHBoxLayout()
        layout.addLayout(receiveBoxLayout)
        self.dataReceiveBox.setLayout(layout)
    
    
    # FUNCTIONS
    def get_calibration_tables(self):
        self.flow_cal_dir = utils.find_olfaControl_directory() + '\\calibration_tables' # NOTE: this takes a super long time
        
        if os.path.exists(self.flow_cal_dir):
            logger.debug('loading flow sensor calibration tables (%s)', self.flow_cal_dir)

            file_type = '.txt'
            cal_file_names = os.listdir(self.flow_cal_dir)
            cal_file_names = [fn for fn in cal_file_names if fn.endswith(file_type)]    # only txt files # TODO: change to csv
            if cal_file_names == []:
                logger.warning('no cal files found')
            else:
                # create dictionaries
                new_sccm2Ard_dicts = {}
                new_ard2Sccm_dicts = {}
                for cal_file in cal_file_names:
                    x = 0       # what is this
                    idx_ext = cal_file.find('.')
                    file_name = cal_file[:idx_ext]
                    sccm2Ard = {}
                    ard2Sccm = {}
                    cal_file_full_dir = self.flow_cal_dir + '\\' + cal_file
                    with open(cal_file_full_dir, newline='') as f:
                        csv_reader = csv.reader(f)
                        firstLine = next(csv_reader)    # skip over header line
                        # get the shit
                        reader = csv.DictReader(f, delimiter=',')
                        for row in reader:
                            if x == 0:
                                try:
                                    sccm2Ard[int(row['SCCM'])] = int(row['int'])
                                    ard2Sccm[int(row['int'])] = int(row['SCCM'])
                                except KeyError as err:
                                    logger.warning('error: %s',err)
                                    logger.warning('%s does not have correct headings for calibration files', cal_file)
                                    x = 1   # don't keep trying to read this file
                    if bool(sccm2Ard) == True:
                        new_sccm2Ard_dicts[file_name] = sccm2Ard
                        new_ard2Sccm_dicts[file_name] = ard2Sccm
                
                # if new dicts are not empty, replace the old ones
                if len(new_sccm2Ard_dicts) != 0:
                    self.sccm2Ard_dicts = new_sccm2Ard_dicts
                    self.ard2Sccm_dicts = new_ard2Sccm_dicts
                else:
                    logger.info('no calibration files found in this directory')
            
        else:
            logger.warning('Cannot find flow cal directory (searched in %s)', self.flow_cal_dir)   # TODO this is big issue if none found
    
    def cal_tbl_btn_toggled(self, checked):
        if checked:
            self.cal_table_btn.setText('Change calibration table')
            self.cal_table_widget.setEnabled(False)
            self.calibration_table_changed()
        else:
            self.cal_table_btn.setText('Set calibration table')
            self.cal_table_widget.setEnabled(True)
    
    def calibration_table_changed(self):
        new_calibration_table_name = self.cal_table_widget.currentItem().text()
        self.intToSccm_dict = self.ard2Sccm_dicts.get(new_calibration_table_name)
        self.sccmToInt_dict = self.sccm2Ard_dicts.get(new_calibration_table_name)
    
    
    # CONNECT TO DEVICE
    def getPorts(self):
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
            self.port_widget.addItem(noPortMsg)

        # if any are 'Arduino', set the first one to the current index
        for item_idx in range(0,self.port_widget.count()):
            this_item = self.port_widget.itemText(item_idx)
            if 'Arduino' in this_item:
                break
        if item_idx != []:
            self.port_widget.setCurrentIndex(item_idx)
        else:
            logger.debug('no Arduinos detected :(')
    
    def portChanged(self):
        if self.port_widget.count() != 0:
            self.port = self.port_widget.currentText()
            if self.port == noPortMsg:
                self.connectButton.setEnabled(False)
                self.connectButton.setText(noPortMsg)
            else:
                self.portStr = self.port[:self.port.index(':')]
                self.connectButton.setEnabled(True)
                self.connectButton.setText("Connect to  " + self.portStr)
        
    def toggled_connect(self, checked):
        if checked:
            i = self.port.index(':')
            comPort = self.port[:i]
            baudrate = int(flowSens_baud)
            self.serial = QtSerialPort.QSerialPort(comPort,baudRate=baudrate,readyRead=self.receive)
            logger.info('Created serial object at %s', comPort)
            if not self.serial.isOpen():
                if self.serial.open(QtCore.QIODevice.ReadWrite):
                    logger.info('successfully opened port (& set mode to ReadWrite)')
                    self.setConnected(True)
                else:
                    logger.warning('could not successfully open port')
                    self.setConnected(False)
            else:
                self.setConnected(True)
        else:
            try:
                if self.serial.isOpen():
                    self.serial.close()
                    logger.info('Closed serial port')
                    self.setConnected(False)
            except AttributeError:
                logger.debug('Cannot close port, serial object does not exist')
    
    def setConnected(self, connected):
        if connected == True:
            self.connectButton.setText('Stop communication w/ ' + self.portStr)
            self.refreshButton.setEnabled(False)
        else:
            self.connectButton.setText('Connect to ' + self.portStr)
            self.connectButton.setChecked(False)
            self.refreshButton.setEnabled(True)
    
    
    # SEND/RECEIVE DATA
    def receive(self):
        if self.serial.canReadLine() == True:
            text = self.serial.readLine(1024)
            try:
                text = text.decode("utf-8")
                text = text.rstrip('\r\n')
                self.rawReadDisplay.append(text)
                if text.isnumeric():
                    str_value = text
                    flowVal_int = int(text)
                    val_SCCM = utils_olfa_48line.convertToSCCM(flowVal_int,self.intToSccm_dict)
                    dataStr = str_value + '\t' + str(val_SCCM)
                    #dataStr = str_value + '\t' + str(flowVal_int)
                    self.receiveBox.append(dataStr)
                    try: self.window().receive_data_from_device('flow sensor','FL',str_value)
                    except AttributeError as err: pass
            except UnicodeDecodeError as err:
                logger.error('Serial read error: %s',err)
    
    def send_to_arduino(self, strToSend):
        bArr_send = strToSend.encode()
        try:
            if self.serial.isOpen():
                self.serial.write(bArr_send)                # send to Arduino
            else:
                logger.warning('Serial port not open, cannot send parameter: %s', strToSend)
        except AttributeError as err:
            logger.warning('(Attribute Error) Serial port not open, cannot send parameter: %s', strToSend)


if __name__ == "__main__":
    app1 = QApplication(sys.argv)
    theWindow = flowSensor()
    theWindow.show()
    theWindow.setWindowTitle('flow sensor')
    sys.exit(app1.exec_())