import sys, logging
from datetime import datetime

from PyQt5.QtWidgets import *
from serial.tools import list_ports



currentDate = str(datetime.date(datetime.now()))
number_of_vials = 8

noPort_msg = "no ports detected :/"

        

class Vial(QGroupBox):

    def __init__(self, parent, vialNum):
        super().__init__()
        self.parent = parent
        self.vialNum = vialNum

        self.generate_stuff()

        self.setLayout(self.layout)
        self.vial_button.setMaximumWidth(60)
        
    
    def generate_stuff(self):
        # checkbox
        self.vial_checkbox = QCheckBox()
        self.vial_checkbox.setToolTip('Include this vial in trial')

        # open vial
        self.vial_button = QPushButton(text=self.vialNum,checkable=True,toggled=self.vial_button_toggled)
        self.vial_button.setToolTip('Open vial')
        
        # odor
        self.vial_odor = QLineEdit()
        self.vial_odor.setToolTip('Enter odor')

        # concentration
        self.vial_concentration = QLineEdit()
        self.vial_concentration.setToolTip('Enter concentration')

        # list of flows
        self.vial_flow_list = QLineEdit()
        self.vial_flow_list.setToolTip('Enter list of flows for this trial')
        
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.vial_checkbox)
        self.layout.addWidget(self.vial_button)
        self.layout.addWidget(self.vial_odor)
        self.layout.addWidget(self.vial_concentration)
        self.layout.addWidget(self.vial_flow_list)

    # ACTIONS
    def vial_button_toggled(self, checked):
        if checked:
            logger.debug('opening vial %s', self.vialNum)
            # TODO: open vial

        else:
            logger.debug('closing vial %s', self.vialNum)
            # TODO: close vial


class MFC(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.generate_stuff()
        self.setLayout(self.mainLayout)

    def generate_stuff(self):
        self.mfc_flow_set = QSpinBox(maximum=1000,value=100)
        self.mfc_flow_set.setToolTip('Set MFC flow')

        self.mfc_flow_update_btn = QPushButton(text='Update')
        self.mfc_flow_update_btn.setToolTip('Send flow value to MFC')
        self.mfc_flow_update_btn.clicked.connect(self.send_mfc_flow_update)

        self.mainLayout = QHBoxLayout()
        self.mainLayout.addWidget(QLabel('MFC'))
        self.mainLayout.addWidget(self.mfc_flow_set)
        self.mainLayout.addWidget(QLabel('SCCM'))
        self.mainLayout.addWidget(self.mfc_flow_update_btn)

    def send_mfc_flow_update(self):
        new_flow_value = self.mfc_flow_set.text()
        logger.debug('updated MFC flow to %s sccm',new_flow_value)

        # TODO: send this to the MFC



class olfactometer_window(QGroupBox):
    
    def __init__(self):
        super().__init__()

        self.generate_ui()
        self.setTitle('Olfactometer')

    
    def generate_ui(self):
        self.create_connect_box()
        self.create_mfcs_box()
        self.create_vials_box()
        self.connect_box.setMaximumHeight(self.connect_box.sizeHint().height())

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        mainLayout.addWidget(self.connect_box)
        mainLayout.addWidget(self.mfcs_groupbox)
        mainLayout.addWidget(self.vials_groupbox)
        
    def create_connect_box(self):
        self.connect_box = QGroupBox("Connect to Teensy")
        self.port_widget = QComboBox(currentIndexChanged=self.port_changed)
        self.connect_btn = QPushButton(checkable=True,toggled=self.toggled_connect)
        self.refresh_btn = QPushButton(text="Refresh",clicked=self.get_ports)
        self.get_ports()
        connect_box_layout = QFormLayout()
        connect_box_layout.addRow(QLabel(text="Select Port:"),self.port_widget)
        connect_box_layout.addRow(self.refresh_btn,self.connect_btn)
        self.connect_box.setLayout(connect_box_layout)

    def create_mfcs_box(self):
        self.mfcs_groupbox = QGroupBox('MFCs')

        self.mfc1 = MFC(self)
        self.mfc2 = MFC(self)

        layout = QVBoxLayout()
        layout.addWidget(self.mfc1)
        layout.addWidget(self.mfc2)
        self.mfcs_groupbox.setLayout(layout)

    
    def create_vials_box(self):
        self.vials_groupbox = QGroupBox('Vials')
        self.vials = []
        for v in range(number_of_vials):
            v_vialNum = str(v+1)
            v_vial = Vial(parent=self, vialNum=v_vialNum)
            self.vials.append(v_vial)

        self.vials_layout = QVBoxLayout()
        for v in range(number_of_vials):
            self.vials_layout.addWidget(self.vials[v])

        self.vials_groupbox.setLayout(self.vials_layout)

    # CONNECT FUNCTIONS
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
            self.port_widget.addItem(noPort_msg)
    
    def port_changed(self):
        if self.port_widget.count() != 0:
            self.port = self.port_widget.currentText()
            if self.port == noPort_msg:
                self.connect_btn.setEnabled(False)
                self.connect_btn.setText(noPort_msg)
            else:
                self.portStr = self.port[:self.port.index(':')]
                self.connect_btn.setEnabled(True)
                self.connect_btn.setText("Connect to  " + self.portStr)
    
    def toggled_connect(self, checked):
        if checked:
            logger.error('connecting to olfactometer')
            # TODO: connect to olfactometer

        '''
            i = self.port.index(':')
            self.comPort = self.port[:i]
            self.serial = QtSerialPort.QSerialPort(self.comPort,readyRead=self.receive)
            if not self.serial.isOpen():
                if self.serial.open(QtCore.QIODevice.ReadWrite):
                    self.set_connected(True)
                else:
                    self.set_connected(False)
            else:
                self.set_connected(True)
        else:
            try:
                self.set_connected(False)
                self.serial.close()
            except AttributeError:
                pass
        '''

        
    def set_connected(self, connected):
        if connected == True:
            self.connect_btn.setText('Stop communication w/ ' + self.portStr)
            self.refresh_btn.setEnabled(False)
            self.port_widget.setEnabled(False)
        else:
            self.connect_btn.setText('Connect to ' + self.portStr)
            self.connect_btn.setChecked(False)
            self.refresh_btn.setEnabled(True)
            self.port_widget.setEnabled(True)

    '''
    def receive(self):
        if self.serial.canReadLine() == True:
            text = self.serial.readLine(1024)
            try:
                text = text.decode("utf-8")
                text = text.rstrip('\r\n')
                self.raw_read_display.append(text)

                strToFind = 'name: '
                
                # IF NAME/ADDRESS WERE SENT
                if strToFind in text:
                    text=text[3:]       # remove logging info
                    
                    # find name
                    strToFind = 'name: '
                    beginning_idx = text.find(strToFind)
                    charsToRemove = len(strToFind)
                    c = text[charsToRemove:]
                    slash_idx = c.find('\t')
                    slave_name_received = c[:slash_idx]
                    self.active_slaves.append(slave_name_received)

                    # find address
                    strToFind = 'address: '
                    beginning_idx = text.find(strToFind)
                    charsToRemove = len(strToFind) + beginning_idx
                    slave_address = text[charsToRemove:]
                    
                    
                    # enable groupbox for this slave
                    for s in self.slave_objects:
                        if s.name == slave_name_received:
                            s.setEnabled(True)
                            # & add the address
                            address_label = 'Slave Address: {}'.format(slave_address)
                            s.slave_address_label.setText(address_label)

                        
                # IF FLOW UPDATE WAS SENT
                if len(text) == 17:
                    text = text[3:]     # remove arduino logging info

                    # split up for writing to datafile
                    slave_vial = text[0:2]
                    flowVal = text[2:6]
                    ctrlVal = text[6:10]

                    # send to main GUI
                    device = 'olfactometer ' + slave_vial
                    unit = 'FL'
                    value = flowVal
                    self.window().receive_data_from_device(device,unit,value)
            
            except UnicodeDecodeError as err:
                print("Serial read error")
    '''



if __name__ == "__main__":

    # LOGGING
    logger = logging.getLogger(name='olfactometer')
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
    theWindow = olfactometer_window()
    theWindow.show()
    sys.exit(app1.exec_())