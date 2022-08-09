# flowSensor_driver.py
# for Honeywell 5100V

#import os, time, serial
import sys
import logging
from PyQt5 import QtCore, QtSerialPort
from PyQt5.QtWidgets import *
from serial.tools import list_ports
import utils

currentDate = utils.currentDate
noPortMsg = ' ~ No COM ports detected ~'

flowSens_baud = 9600
sensorType = "Honeywell 5101V"


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
        self.create_raw_data_box()
        self.createDataReceiveBoxes()

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.connectBox,0,0,1,1)
        mainLayout.addWidget(self.settings_box,1,0,1,1)
        mainLayout.addWidget(self.raw_data_box,2,0,1,1)
        mainLayout.addWidget(self.dataReceiveBox,0,1,3,1)
        self.setLayout(mainLayout)
    
    
    # CONNECT TO DEVICE
    def createConnectBox(self):
        self.connectBox = QGroupBox("Connect")

        self.portLbl = QLabel(text="Port/Device:")
        self.port_widget = QComboBox(currentIndexChanged=self.portChanged)
        self.connectButton = QPushButton(checkable=True,toggled=self.toggled_connect)
        self.refreshButton = QPushButton(text="Refresh",clicked=self.getPorts)
        self.getPorts()

        #readLbl = QLabel(text="raw data from serial port:")
        #self.rawReadDisplay = QTextEdit(readOnly=True)
        #self.rawReadSpace = QWidget()
        #readLayout = QVBoxLayout()
        #readLayout.addWidget(readLbl)
        #readLayout.addWidget(self.rawReadDisplay)
        #self.rawReadSpace.setLayout(readLayout)

        self.connectBoxLayout = QFormLayout()
        self.connectBoxLayout.addRow(self.portLbl,self.port_widget)
        self.connectBoxLayout.addRow(self.refreshButton,self.connectButton)
        #self.connectBoxLayout.addRow(self.rawReadSpace)
        self.connectBox.setLayout(self.connectBoxLayout)

    def create_settings_box(self):
        self.settings_box = QGroupBox('Settings')

        self.timebtreqs_wid = QLineEdit(text='100',returnPressed=lambda:self.send_to_arduino('MM_timebt_' + self.timebtreqs_wid.text()))
        self.timebtreqs_btn = QPushButton(text="Send", clicked=lambda:self.send_to_arduino('MM_timebt_' + self.timebtreqs_wid.text()))
        
        layout = QHBoxLayout()
        layout.addWidget(QLabel(text="Time b/t requests for slave data (ms):"))
        layout.addWidget(self.timebtreqs_wid)
        layout.addWidget(self.timebtreqs_btn)
        self.settings_box.setLayout(layout)


    def create_raw_data_box(self):
        self.raw_data_box = QGroupBox('Raw Data')

        readLbl = QLabel(text="raw data from serial port:")
        self.rawReadDisplay = QTextEdit(readOnly=True)
        self.rawReadSpace = QWidget()
        
        layout = QVBoxLayout()
        layout.addWidget(readLbl)
        layout.addWidget(self.rawReadDisplay)
        self.raw_data_box.setLayout(layout)
    
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
            logger.debug('setting olfa port widget to arduino port')
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
    
    def send_to_arduino(self, strToSend):
        bArr_send = strToSend.encode()
        try:
            if self.serial.isOpen():
                self.serial.write(bArr_send)                # send to Arduino
                #self.raw_write_display.append(strToSend)    # display string that was sent
            else:
                logger.warning('Serial port not open, cannot send parameter: %s', strToSend)
        except AttributeError as err:
            logger.warning('(Attribute Error) Serial port not open, cannot send parameter: %s', strToSend)

    
    # RECEIVE DATA
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
    
    def receive(self):
        if self.serial.canReadLine() == True:
            text = self.serial.readLine(1024)
            try:
                text = text.decode("utf-8")
                text = text.rstrip('\r\n')
                self.rawReadDisplay.append(text)
                if text.isnumeric():
                    str_value = text
                    flowVal = int(text)
                    #val_SCCM = utils.convertToSCCM(flowVal,sensorType)
                    #dataStr = str_value + '\t' + str(val_SCCM)
                    dataStr = str_value + '\t' + str(flowVal)
                    self.receiveBox.append(dataStr)
                    try:
                        self.window().receive_data_from_device('flow sensor','FL',str_value)
                    except AttributeError as err:
                        pass
            except UnicodeDecodeError as err:
                logger.error('Serial read error: %s',err)


if __name__ == "__main__":
    logger.debug('opening window')
    app1 = QApplication(sys.argv)
    theWindow = flowSensor()
    theWindow.show()
    theWindow.setWindowTitle('flow sensor')
    sys.exit(app1.exec_())