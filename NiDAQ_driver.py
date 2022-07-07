# NiDAQ_driver.py

'''
    - download nidaqmx package from NI website (before using pip install)

    - install NI-DAQmx driver from NI website (or it won't recognize the device)
        https://www.ni.com/en-us/support/downloads/drivers/download/packaged.ni-daqmx.445931.html
        requires reboot
'''


import sys, time, logging
#from tkinter import mainloop
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
import nidaqmx
    
noPortMsg = '~ No NI devices detected ~'
analogChannel = 'ai0'   # TODO: fix this

timeBt_Hz = 1000
timeBt_s = 1/timeBt_Hz


class worker(QObject):
    sendData_from_worker = pyqtSignal(float)

    def __init__(self, devName):
        super().__init__()
        self.readTheStuff = False
        self.timeToSleep = timeBt_s
        self.devName = devName
        self.analogChan = analogChannel
    
    @pyqtSlot()
    def read_from_ni_device(self):
        channelIWant = self.devName + '/' + self.analogChan
        t = nidaqmx.Task()      # create a task
        t.ai_channels.add_ai_voltage_chan(channelIWant) # add analog input channel to this task
        while self.readTheStuff == True:
            value = t.read(1)
            value = value[0]
            self.sendData_from_worker.emit(value)
            time.sleep(self.timeToSleep)


class NiDaq(QGroupBox):

    def __init__(self):
        super().__init__()

        self.generate_ui()

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.connectBox,0,0,1,1)
        mainLayout.addWidget(self.settingsBox,1,0,1,1)
        mainLayout.addWidget(self.dataReceiveBox,0,1,2,1)
        self.setLayout(mainLayout)
        self.setMaximumHeight(225)
        self.setTitle('PID')
    
    def generate_ui(self):
        self.createConnectBox()
        self.createSettingsBox()
        self.createDataReceiveBoxes()

        max_width = self.connectBox.sizeHint().width()
        self.connectBox.setFixedWidth(max_width)
        self.settingsBox.setFixedWidth(max_width)

        


    # CONNECT TO DEVICE
    def createConnectBox(self):
        self.connectBox = QGroupBox("Connect to NI device")

        self.portLbl = QLabel(text="Select Device:")
        self.portWidget = QComboBox(currentIndexChanged=self.port_changed)
        self.connectButton = QPushButton(checkable=True,toggled=self.toggled_connect)
        self.refreshButton = QPushButton(text="Refresh",clicked=self.getPorts)
        self.getPorts()

        channelLbl = QLabel(text="Channel:")
        
        self.channelToRead = QLineEdit(readOnly=True)
        self.channelToRead.setToolTip("Device channel to read from")
        self.channel_widget = QComboBox()
        
        if self.port != noPortMsg:
            self.channelToRead.setText(self.port + '/' + analogChannel)
        
        self.connectBoxLayout = QFormLayout()
        self.connectBoxLayout.addRow(self.portLbl,self.portWidget)
        self.connectBoxLayout.addRow(channelLbl,self.channelToRead)
        self.connectBoxLayout.addRow(self.refreshButton,self.connectButton)
        self.connectBox.setLayout(self.connectBoxLayout)
    
    def getPorts(self):
        self.portWidget.clear()
        try:
            ports = nidaqmx.system.system.System().devices.device_names
            if ports:
                for ser in ports:
                    ser_str = str(ser)
                    self.portWidget.addItem(ser_str)
            else:
                self.portWidget.addItem(noPortMsg)
        except FileNotFoundError:
            #logger.warning('no NI devices detected')
            self.portWidget.addItem(noPortMsg)
        self.port = self.portWidget.currentText()
    
    def port_changed(self):
        if self.portWidget.count() != 0:
            self.port = self.portWidget.currentText()
            if self.port == noPortMsg:
                self.connectButton.setEnabled(False)
                self.connectButton.setText("Connect")
            else:
                self.connectButton.setEnabled(True)
                self.connectButton.setText("Connect to " + self.port)

    def toggled_connect(self, checked):
        if checked:
            #logger.debug('clicked connect button')
            self.portWidget.setEnabled(False)
            self.refreshButton.setEnabled(False)
            self.connectButton.setText('Stop reading from ' + str(self.port))

            self.setUpThreads()
            self.thread1.start()
            self.worker_obj.readTheStuff = True
        
        else:
            #logger.debug('disconnect')
            self.portWidget.setEnabled(True)
            self.connectButton.setText('Connect to ' + str(self.port))
            self.refreshButton.setEnabled(True)

            self.worker_obj.readTheStuff = False
            self.thread1.quit()
    
    def setUpThreads(self):
        self.worker_obj = worker(self.port)
        self.thread1 = QThread()
        self.worker_obj.moveToThread(self.thread1)
        self.worker_obj.sendData_from_worker.connect(self.receive_data_from_worker)
        self.thread1.started.connect(self.worker_obj.read_from_ni_device)

    def createSettingsBox(self):
        self.settingsBox = QGroupBox("Settings")

        lbl = QLabel("Time b/t readings (ms):")
        self.timeWid = QLineEdit()
        self.updateBut = QPushButton(text="Update",clicked=self.updateTimeBt)

        layout = QFormLayout()
        layout.addRow(lbl)
        layout.addRow(self.timeWid,self.updateBut)
        self.settingsBox.setLayout(layout)

    def updateTimeBt(self):
        # TODO: finish this
        #self.timeBt = self.timeWid.
        #logger.error('not set up yet')
        pass

    # RECEIVE DATA
    def createDataReceiveBoxes(self):
        self.dataReceiveBox = QGroupBox("data received")

        self.raw_receive_box = QTextEdit(readOnly=True)
        receiveBoxLbl = QLabel(text="raw values")
        receiveBoxLayout = QVBoxLayout()
        receiveBoxLayout.addWidget(receiveBoxLbl)
        receiveBoxLayout.addWidget(self.raw_receive_box)

        self.mV_receive_box = QTextEdit(readOnly=True)
        mV_receive_box_lbl = QLabel(text="Reading (mV)")
        mV_receive_box_layout = QVBoxLayout()
        mV_receive_box_layout.addWidget(mV_receive_box_lbl)
        mV_receive_box_layout.addWidget(self.mV_receive_box)

        layout = QHBoxLayout()
        layout.addLayout(receiveBoxLayout)
        layout.addLayout(mV_receive_box_layout)
        self.dataReceiveBox.setLayout(layout)

        self.raw_receive_box.setMinimumWidth(165)
        self.mV_receive_box.setMinimumWidth(165)
    
    
    def receive_data_from_worker(self, incomingFlt):
        value = incomingFlt
        value_mV = value*1000

        self.raw_receive_box.append(str(value))
        self.mV_receive_box.append(str(round(value_mV,3)))
        self.window().receive_data_from_device('pid','mV',str(value_mV))
    




if __name__ == "__main__":

    # LOGGING
    logger = logging.getLogger(name='NiDAQ')
    logger.setLevel(logging.DEBUG)
    # console handler
    console_handler_level = logging.DEBUG
    console_handler_formatter = logging.Formatter('%(name)-14s: %(levelname)-8s: %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_handler_level)
    console_handler.setFormatter(console_handler_formatter)
    logger.addHandler(console_handler)

    
    # MAIN APP
    logger.debug('opening window')
    app1 = QApplication(sys.argv)
    theWindow = NiDaq()
    theWindow.show()
    sys.exit(app1.exec_())