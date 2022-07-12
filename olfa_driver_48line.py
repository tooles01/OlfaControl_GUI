import sys, logging, time
from datetime import datetime

from PyQt5 import QtCore, QtSerialPort
from PyQt5.QtWidgets import *
from serial.tools import list_ports



currentDate = str(datetime.date(datetime.now()))


baudrate = 9600     # for communicating w/ master
vialsPerSlave = 8
noPort_msg = "no ports detected :/"

master_modes = ["6: verbose",
                "5: trace",
                "4: notice",
                "3: warning",
                "2: error",
                "1: fatal"]
slave_names = ['A',
                'B',
                'C',
                'D',
                'E',
                'F']
        

class Vial(QGroupBox):

    def __init__(self, parent, vialNum):
        super().__init__()
        self.parent = parent
        self.slaveName = parent.name
        self.vialNum = vialNum

        self.generate_stuff()

        #self.vial_groupbox = QGroupBox()
        #self.vial_groupbox.setLayout(self.layout)
        self.setLayout(self.layout)
        self.vial_button.setMaximumWidth(60)
        self.setpoint_send_btn.setMaximumWidth(60)
        #self.readFromThisVial.setMaximumWidth(self.readFromThisVial.sizeHint().width())
        max_width = self.sizeHint().width()
        self.setMaximumWidth(max_width - 15)
        
    
    def generate_stuff(self):
        self.vial_duration_spinbox = QSpinBox(value=5)
        self.vial_button = QPushButton(text=str("Open " + self.slaveName + self.vialNum),
            #checkable=True,
            toolTip="open vial")
        self.vial_button.clicked.connect(lambda: self.vial_button_clicked())
        self.vial_layout = QHBoxLayout()
        self.vial_layout.addWidget(QLabel("dur(s):"))
        self.vial_layout.addWidget(self.vial_duration_spinbox)
        self.vial_layout.addWidget(self.vial_button)
        
        self.setpoint_value_box = QSpinBox(maximum=1024,value=800)
        self.setpoint_send_btn = QPushButton(text="Update\nSpt")
        self.setpoint_send_btn.clicked.connect(lambda: self.setpoint_btn_clicked(self.setpoint_value_box.value()))
        self.setpoint_layout = QHBoxLayout()
        self.setpoint_layout.addWidget(QLabel("sccm:"))
        self.setpoint_layout.addWidget(self.setpoint_value_box)
        self.setpoint_layout.addWidget(self.setpoint_send_btn)
        
        self.readFromThisVial = QPushButton(text="read flow vals", checkable=True, toggled=self.readFlow_btn_toggled)

        self.calibrate_vial_edit = QLineEdit(text='100')
        self.calibrate_vial_btn = QPushButton(text="calibrate")
        self.calibrate_vial_btn.clicked.connect(self.calibrate_flow_sensor)
        self.calibration_layout = QHBoxLayout()
        self.calibration_layout.addWidget(self.calibrate_vial_edit)
        self.calibration_layout.addWidget(self.calibrate_vial_btn)
        
        # - calibration table selection
        # - debug window
        # - current flow value (?)

        self.layout = QFormLayout()
        self.layout.addRow(self.vial_layout)
        self.layout.addRow(self.setpoint_layout)
        self.layout.addRow(self.readFromThisVial)
        #self.layout.addRow(self.calibration_layout)

    # ACTIONS
    def setpoint_btn_clicked(self, value):
        # - convert from sccm to integer
        setpoint_integer = value

        strToSend = 'S_Sp_' + str(setpoint_integer) + '_' + self.slaveName + self.vialNum
        self.parent.parent.send_to_master(strToSend)    # send to olfactometer_window
        
    def vial_button_clicked(self):
        # toggle it until the duration has passed

        strToSend = 'S_OV_' + str(self.vial_duration_spinbox.value()) + '_' + self.parent.name + self.vialNum
        self.parent.parent.send_to_master(strToSend)
        
    def readFlow_btn_toggled(self, checked):
        if checked:
            self.readFromThisVial.setText("stop getting flow vals")
            strToSend = 'MS_debug_' + self.parent.name + self.vialNum
            self.parent.parent.send_to_master(strToSend)
        else:
            self.readFromThisVial.setText("read flow vals")
            strToSend = 'MS_' + self.parent.name + self.vialNum
            self.parent.parent.send_to_master(strToSend)
        
    def calibrate_flow_sensor(self):
        value_to_calibrate = int(self.calibrate_vial_edit.text())
        # set MFC to this value

        # open proportional valve
        open_pv_command = 'S_OC_' + self.parent.name + self.vialNum
        self.parent.parent.send_to_master(open_pv_command)

        # open isolation valve
        open_iv_command = 'S_OV_5_' + self.parent.name + self.vialNum
        self.parent.parent.send_to_master(open_iv_command)

        # read flow values
        # TODO

class slave_8vials(QGroupBox):

    def __init__(self, parent, name):
        super().__init__()
        self.parent = parent
        self.name = name

        self.create_slaveInfo_box()
        self.create_vials_box()

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.slaveInfo_layout)
        self.mainLayout.addLayout(self.vials_layout)
        self.setLayout(self.mainLayout)

        self.setTitle(name)

    def create_slaveInfo_box(self):
        self.slave_info_box = QGroupBox()

        self.slave_address_label = QLabel(text='Slave address:')
        self.temp_label = QLabel("slave active, whatever")
        # add a way to apply commands to multiple vials at once
        # ex: check the ones you want to apply this setpoint to

        self.slaveInfo_layout = QVBoxLayout()
        self.slaveInfo_layout.addWidget(self.slave_address_label)
        self.slaveInfo_layout.addWidget(self.temp_label)
        
    def create_vials_box(self):
        self.vials = []
        for v in range(vialsPerSlave):
            v_vialNum = str(v+1)
            v_vial = Vial(parent=self, vialNum=v_vialNum)
            self.vials.append(v_vial)

        self.vials_layout = QHBoxLayout()
        for v in range(vialsPerSlave):
            self.vials_layout.addWidget(self.vials[v])

            

class olfactometer_window(QGroupBox):
    
    def __init__(self):
        super().__init__()

        self.generate_ui()
        self.master_groupbox.setEnabled(False)

        self.active_slaves = []

        # TODO: upon first connect: set all vials to not debug

        
        self.setTitle('Olfactometer')

    
    def generate_ui(self):
        self.create_connect_box()
        self.create_master_groupbox()
        self.create_raw_comm_groupbox()
        self.create_slave_groupbox()

        col1_max_width = self.master_groupbox.sizeHint().width()
        self.connect_box.setFixedWidth(col1_max_width)
        self.master_groupbox.setFixedWidth(col1_max_width)

        self.connect_box.setMaximumHeight(self.connect_box.sizeHint().height())
        self.master_groupbox.setMaximumHeight(114)
        self.raw_comm_box.setMaximumHeight(202)

        mainLayout = QGridLayout()
        self.setLayout(mainLayout)

        mainLayout.addWidget(self.connect_box,0,0,1,1)
        mainLayout.addWidget(self.master_groupbox,1,0,1,1)
        mainLayout.addWidget(self.raw_comm_box,0,1,2,1)
        mainLayout.addWidget(self.slave_groupbox,2,0,1,2)
        
    def create_connect_box(self):
        self.connect_box = QGroupBox("Connect to master Arduino")
        self.port_widget = QComboBox(currentIndexChanged=self.port_changed)
        self.connect_btn = QPushButton(checkable=True,toggled=self.toggled_connect)
        self.refresh_btn = QPushButton(text="Refresh",clicked=self.get_ports)
        self.get_ports()
        connect_box_layout = QFormLayout()
        connect_box_layout.addRow(QLabel(text="Select Port:"),self.port_widget)
        connect_box_layout.addRow(self.refresh_btn,self.connect_btn)
        self.connect_box.setLayout(connect_box_layout)

    def create_master_groupbox(self):
        self.master_groupbox = QGroupBox('Master Settings')

        self.m_check_addr_btn = QPushButton(text="Get Slave Addresses",clicked=lambda: self.get_slave_addresses())

        self.m_mode_dropdown = QComboBox()
        self.m_mode_dropdown.addItems(master_modes)
        self.m_mode_btn = QPushButton(text="Send", clicked=lambda: self.send_master_mode(self.m_mode_dropdown.currentText()))
        m_mode_layout = QHBoxLayout()
        m_mode_layout.addWidget(self.m_check_addr_btn)
        m_mode_layout.addWidget(QLabel(text='Change master logging mode:'))
        m_mode_layout.addWidget(self.m_mode_dropdown)
        m_mode_layout.addWidget(self.m_mode_btn)

        self.m_timebtreqs = QLineEdit(text='100',#self.defTimebt,
            returnPressed=lambda:self.send_to_master('MM_timebt_' + self.m_timebtreqs.text()))
        self.m_timebtreqs_btn = QPushButton(text="Send", clicked=lambda:self.send_to_master('MM_timebt_' + self.m_timebtreqs.text()))
        timebt_layout = QHBoxLayout()
        timebt_layout.addWidget(QLabel(text="Time b/t requests for slave data (ms):"))
        timebt_layout.addWidget(self.m_timebtreqs)
        timebt_layout.addWidget(self.m_timebtreqs_btn)

        self.m_manualcmd = QLineEdit(text='xx',#defManualCmd,
            returnPressed=lambda: self.send_to_master(self.m_manualcmd.text()))
        self.m_manualcmd_btn = QPushButton(text="Send",
            clicked=lambda: self.send_to_master(self.m_manualcmd.text()))
        manualcmd_layout = QHBoxLayout()
        manualcmd_layout.addWidget(QLabel(text="Send manual command:"))
        manualcmd_layout.addWidget(self.m_manualcmd)
        manualcmd_layout.addWidget(self.m_manualcmd_btn)
        

        layout = QVBoxLayout()
        layout.addLayout(m_mode_layout)
        layout.addLayout(timebt_layout)
        layout.addLayout(manualcmd_layout)
        self.master_groupbox.setLayout(layout)
        
    def create_raw_comm_groupbox(self):
        self.raw_comm_box = QGroupBox("Raw Communication Data")

        self.raw_write_display = QTextEdit(readOnly=True)
        raw_write_layout = QVBoxLayout()
        raw_write_layout.addWidget(QLabel('wrote to serial port:'))
        raw_write_layout.addWidget(self.raw_write_display)

        self.raw_read_display = QTextEdit(readOnly=True)
        raw_read_layout = QVBoxLayout()
        raw_read_layout.addWidget(QLabel('read from serial port:'))
        raw_read_layout.addWidget(self.raw_read_display)

        raw_comm_layout = QHBoxLayout()
        raw_comm_layout.addLayout(raw_read_layout)
        raw_comm_layout.addLayout(raw_write_layout)
        self.raw_comm_box.setLayout(raw_comm_layout)

        self.raw_write_display.setMinimumWidth(230)
        self.raw_read_display.setMinimumWidth(230)
        
    def create_slave_groupbox(self):
        self.slave_groupbox = QGroupBox('Slaves')

        self.slave_objects = []
        for s in slave_names:
            create_slave = slave_8vials(parent=self,name=s)
            self.slave_objects.append(create_slave)

        self.slave_layout = QVBoxLayout()
        for s in self.slave_objects:
            self.slave_layout.addWidget(s)
            s.setEnabled(False)
        
        self.slave_widget = QWidget()
        self.slave_widget.setLayout(self.slave_layout)

        self.slave_scrollArea = QScrollArea()
        self.slave_scrollArea.setWidget(self.slave_widget)

        self.nothing_layout = QHBoxLayout()
        self.nothing_layout.addWidget(self.slave_scrollArea)
        self.slave_groupbox.setLayout(self.nothing_layout)
        #self.slave_groupbox.setMinimumWidth(self.slave_scrollArea.sizeHint().width())
        self.slave_groupbox.setMinimumWidth(self.slave_widget.sizeHint().width() + 40)


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
            i = self.port.index(':')
            self.comPort = self.port[:i]
            self.serial = QtSerialPort.QSerialPort(self.comPort,baudRate=baudrate,readyRead=self.receive)
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
    
    def set_connected(self, connected):
        if connected == True:
            self.get_slave_addresses()
            self.master_groupbox.setEnabled(True)
            self.connect_btn.setText('Stop communication w/ ' + self.portStr)
            self.refresh_btn.setEnabled(False)
            self.port_widget.setEnabled(False)
        else:
            self.master_groupbox.setEnabled(False)
            self.connect_btn.setText('Connect to ' + self.portStr)
            self.connect_btn.setChecked(False)
            self.refresh_btn.setEnabled(True)
            self.port_widget.setEnabled(True)

            # set vials of all currently active slaves to not debug
            for slave in self.active_slaves:
                for vial in range(0,vialsPerSlave):
                    strToSend = 'MS_' + slave + str(vial+1)
                    self.send_to_master(strToSend)
                    time.sleep(.3)

    def get_slave_addresses(self):
        self.active_slaves = []
        self.send_to_master('C')

        '''
        # once received, remove inactive slaves
        for s_name in slave_names:
            # if name is not in active slaves list: remove its groupbox
            if s_name in self.active_slaves:
                # you can keep it
                x=2
            else:
                # get rid of it
                x=2
        '''
        

        
    def send_master_mode(self, newMode):
        if newMode == master_modes[0]:  mode_value = 6
        if newMode == master_modes[1]:  mode_value = 5
        if newMode == master_modes[2]:  mode_value = 4
        if newMode == master_modes[3]:  mode_value = 3
        if newMode == master_modes[4]:  mode_value = 2
        if newMode == master_modes[5]:  mode_value = 1
        
        m_mode_string = 'MM_mode_' + str(mode_value)
        self.send_to_master(m_mode_string)


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
                    '''
                    # add groupbox to layout
                    for s in self.slave_objects:
                        if s.name == slave_name_received:
                            self.slave_layout.addWidget(s)
                            address_label = 'Slave Address: {}'.format(slave_address)
                            s.slave_address_label.setText(address_label)
                            self.slave_groupbox.setLayout(self.nothing_layout)
                            
                            #x=1
                    '''
                        
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

    def send_to_master(self, strToSend):
        bArr_send = strToSend.encode()
        try:
            if self.serial.isOpen():
                self.serial.write(bArr_send)
                print("sent to", self.port, ":  ", strToSend)
                self.raw_write_display.append(strToSend)
            else:
                print('Serial port not open, cannot send parameter: %s', strToSend)

        except AttributeError as err:
            print('(Attribute Error) Serial port not open, cannot send parameter: %s', strToSend)



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