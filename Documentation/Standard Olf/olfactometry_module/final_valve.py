'''
Final valve widget

This will connect to an Arduino and send something when the button is pushed


ST 5/21/2026
'''

import sys, logging
from PyQt5 import QtCore, QtSerialPort
from PyQt5.QtWidgets import *
from serial.tools import list_ports


noPortMsg = ' ~ No COM ports detected ~'
arduino_baud = 9600

def create_console_handler():
    console_handler_formatter = logging.Formatter('%(asctime)s : %(name)-14s :%(levelname)-8s: %(message)s',datefmt='%H:%M:%S')
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(console_handler_formatter)
    return console_handler

# CREATE LOGGER
logger = logging.getLogger(name='final valve')
logger.setLevel(logging.DEBUG)
if logger.hasHandlers():    logger.handlers.clear()     # removes duplicate log messages
console_handler = create_console_handler()
logger.addHandler(console_handler)

class Final_Valve(QGroupBox):

    def __init__(self):
        super().__init__()
        self.setTitle('Final Valve')

        self.generate_ui()
        layout = QHBoxLayout()
        layout.addWidget(self.connect_box)
        layout.addWidget(self.final_valve_button)
        self.setLayout(layout)
    
    # GUI ELEMENTS
    def generate_ui(self):
        # CONNECT BOX
        self.connect_box = QGroupBox("Connect")

        self.portLbl = QLabel(text="Port/Device:")
        self.port_widget = QComboBox(currentIndexChanged=self.port_changed)
        self.connect_btn = QPushButton(checkable=True,toggled=self.toggled_connect)
        self.refresh_btn = QPushButton(text="Refresh",clicked=self.get_ports)
        self.get_ports()

        connect_box_layout = QFormLayout()
        connect_box_layout.addRow(self.portLbl,self.port_widget)
        connect_box_layout.addRow(self.refresh_btn,self.connect_btn)
        self.connect_box.setLayout(connect_box_layout)

        # FINAL VALVE BUTTON
        self.final_valve_button = QPushButton(text='Final Valve',checkable=True)
        self.final_valve_button.toggled.connect(self.fv_btn_toggled)

    
    # SERIAL CONNECTION
    def get_ports(self):
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

    def toggled_connect(self, checked):
        if checked:
            i = self.port.index(':')
            self.comPort = self.port[:i]
            self.serial = QtSerialPort.QSerialPort(self.comPort,baudRate=arduino_baud)#,readyRead=self.receive)
            if not self.serial.isOpen():
                if self.serial.open(QtCore.QIODevice.ReadWrite):
                    self.set_connected(True)
                else:
                    self.set_connected(False)
            else:
                self.set_connected(True)
        else:
            try:
                self.serial.close()
                self.set_connected(False)
            except AttributeError as err:
                logger.error("error :( --> %s", err)

    def port_changed(self):
        if self.port_widget.count() != 0:
            self.port = self.port_widget.currentText()
            if self.port == noPortMsg:
                self.portStr = noPortMsg
                self.connect_btn.setEnabled(False)
                self.connect_btn.setText(noPortMsg)
            else:
                self.portStr = self.port[:self.port.index(':')]
                self.connect_btn.setEnabled(True)
                self.connect_btn.setText("Connect to  " + self.portStr)

    def set_connected(self, connected):
        if connected == True:
            logger.info('Connected to ' + self.port_widget.currentText())
            self.connect_btn.setText("Disconnect")
            self.connect_btn.setToolTip("Disconnect from " + self.portStr)
            self.refresh_btn.setEnabled(False)
            self.port_widget.setEnabled(False)
        
        else:
            logger.info('Disconnected from ' + self.port_widget.currentText())
            self.connect_btn.setText("Connect")
            self.connect_btn.setToolTip("Connect to " + self.portStr)
            self.connect_btn.setChecked(False)
            self.refresh_btn.setEnabled(True)
            self.port_widget.setEnabled(True)
    
    # ACTIVATE FINAL VALVE
    def fv_btn_toggled(self,checked):
        if checked:
            self.send_to_Arduino("on")
            self.final_valve_button.setText("Turn FV off")
            #logger.debug("Turning final valve on")

        else:
            self.send_to_Arduino("off")
            self.final_valve_button.setText("Turn FV on")
            #logger.debug("Turning final valve off")
    
    # SEND MESSAGE
    def send_to_Arduino(self, strToSend):
        bArr_send = strToSend.encode()
        try:
            if self.serial.isOpen():
                self.serial.write(bArr_send)                # Send to Arduino
                logger.info("Sending string to Arduino: %s", strToSend)
            else:
                logger.warning('Serial port not open, cannot send string')
        except AttributeError as err:
            if (err.args[0] == "'Final_Valve' object has no attribute 'serial'"):
                logger.warning('(Attribute Error) Serial port not open, cannot send parameter: %s', strToSend)

if __name__ == "__main__":
    app1 = QApplication(sys.argv)
    theWindow = Final_Valve()
    theWindow.show()
    sys.exit(app1.exec_())