import sys, logging
from datetime import datetime

from PyQt5.QtWidgets import *
#from PyQt5.QtCore import QObject
from serial.tools import list_ports

import time
import serial

currentDate = str(datetime.date(datetime.now()))
number_of_vials = 8

noPort_msg = "no ports detected :/"

vial_default_flow_values = '10,14,27,52'

        

class Vial(QGroupBox):

    def __init__(self, parent, vialNum):
        super().__init__()
        self.parent = parent
        self.vialNum = vialNum
        self.teensy = self.parent.olfa_device

        self.generate_stuff()

        self.setLayout(self.layout)
        self.vial_button.setMaximumWidth(60)
        
    
    def generate_stuff(self):
        # checkbox
        self.vial_checkbox = QCheckBox()
        self.vial_checkbox.setToolTip('Include this vial in trial')
        self.vial_checkbox.setChecked(True)

        # open vial
        self.vial_button = QPushButton(text=self.vialNum,checkable=True,toggled=self.vial_button_toggled)
        self.vial_button.setToolTip('Open vial')
        
        # odor
        self.vial_odor = QLineEdit()
        self.vial_odor.setPlaceholderText('Chemical')
        self.vial_odor.setToolTip('Enter odor')

        # concentration
        self.vial_concentration = QLineEdit()
        self.vial_concentration.setPlaceholderText('Concentration (0-1)')
        self.vial_concentration.setToolTip('Enter concentration')

        # list of flows
        self.vial_flow_list = QLineEdit()
        self.vial_flow_list.setPlaceholderText("Flows list")
        self.vial_flow_list.setToolTip('Enter list of flows for this trial')
        self.vial_flow_list.setText(vial_default_flow_values)
        
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.vial_checkbox)
        self.layout.addWidget(self.vial_button)
        self.layout.addWidget(self.vial_odor)
        self.layout.addWidget(self.vial_concentration)
        self.layout.addWidget(self.vial_flow_list)

    # ACTIONS
    def vial_button_toggled(self, checked):
        if checked:
            print(type(self.vialNum))
            logger.debug('opening vial %s', self.vialNum)
            self.teensy._set_valveset(self.vialNum, valvestate=1, suppress_errors=False)

        else:
            logger.debug('closing vial %s', self.vialNum)
            self.teensy._set_valveset(self.vialNum, 0, suppress_errors=False)


class MFC(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.teensy = self.parent.olfa_device
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
        print("I am sure I am here")
        new_flow_value = self.mfc_flow_set.text()
        logger.debug('updated MFC flow to %s sccm',new_flow_value)
        print(type(new_flow_value))
        self.teensy.set_flowrate( int(new_flow_value))




class TeensyOlfa():
    
    def __init__(self):
        #super().__init__()
        self.dummyvial = 4
        
    def connect_olfa(self, mfc_config, com_settings, flow_units='SCCM', setflow=-1):   
        print(flow_units)
        self.slaveindex = mfc_config['slave_index']
        self.mfc_type = mfc_config['MFC_type']
        self.capacity = int(mfc_config['capacity'])
        self.units = flow_units
        self.gas = mfc_config['gas']
        if self.mfc_type.startswith('alicat_digital'):
            self.address = mfc_config['address']
        if 'arduino_port_num' in list(mfc_config.keys()):  # this is only needed for Teensy olfactometers. This is the device ID
            self.arduino_port = int(mfc_config['arduino_port_num'])

        self.serial = self.connect_serial(com_settings['com_port'], baudrate=com_settings['baudrate'], timeout=1, writeTimeout=1)
     
    def connect_serial(self, port, baudrate, timeout=1, writeTimeout=1):
        """
        Return Serial object after making sure that the port is accessible and that the port is expressed as a string.

        :param port: str or int (ie "COM4" or 4 for Windows).
        :param baudrate: baudrate.
        :param timeout: read timeout in seconds, default 1 sec.
        :param writeTimeout: write timeout in seconds, default 1 sec.
        :return: serial port object.
        :rtype: serial.Serial
        """
        print(baudrate)
        if isinstance(port, int):
            port = "COM{0}".format(port)
        names_list = list()
        for i in list_ports.comports():
            names_list.append(i[0])
        if port not in names_list:
            print(("Serial not found on {0}.".format(port)))
            print('Listing current serial ports with devices:')
            for ser in list_ports.comports():
                ser_str = '\t{0}: {1}'.format(ser[0], ser[1])
                print(ser_str)
            time.sleep(.01)  # just to let the above lines print before the exemption is raised. cleans console output.
            raise serial.SerialException('Requested COM port: {0} is not listed as connected.'.format(port))
        else:
            
            print(baudrate, timeout, writeTimeout)
            return serial.Serial(port, baudrate=baudrate, timeout=timeout, writeTimeout=writeTimeout)

    def set_flowrate(self, flowrate):
        """

        :param flowrate: flowrate in units of self.capacity (usually ml/min)
        :param args:
        :param kwargs:
        :return:
        """
        success = False
        start_time = time.time()
        # print "Setting rate of: ", flowrate
        print( self.capacity)
        if flowrate > self.capacity or flowrate < 0:
            return success
        flownum = (flowrate * 1. / self.capacity)*64000
        flownum = int(flownum)
        command = "DMFC {0:d} {1:d} A{2:d}".format(self.slaveindex, self.arduino_port, flownum)
        print(command)
        confirmation = self.send_command(command)
        #print(confirmation)
        if(confirmation != 'MFC set\r\n'):
            print("Error setting MFC: ", confirmation)
        else:
            # Attempt to read back
            success = True
            command = "DMFC {0:d} {1:d}".format(self.slaveindex, self.arduino_port)
            returnstring = self.send_command(command)
            print(returnstring)
            while (returnstring is None or returnstring.startswith(b'Error -2')) and time.time() - start_time < .2:
                returnstring = self.send_command(command)
            
        return success

    def get_flowrate(self):
        """

        :param args:
        :param kwargs:
        :return: float flowrate normalized to max flowrate.
        """
        start_time = time.time()

        command = "DMFC {0:d} {1:d} A".format(self.slaveindex, self.arduino_port)
        command_get = "DMFC {0:d} {1:d}".format(self.slaveindex, self.arduino_port)

        # first, flush the buffer on the Teensy:
        _ = self.send_command(command_get)
        # stick around querying the olfactometer until it gets the command.
        confirmation = self.send_command(command)
        while (confirmation is None or not confirmation.startswith(b"MFC set")) and time.time() - start_time < .2:
            confirmation = self.send_command(command)
        # stick around querying the olfactometer until it gets the flow data from the alicat.
        returnstring = self.send_command(command_get)
        while (returnstring is None or returnstring.startswith(b"Error -2")) and time.time() - start_time < .2:
            returnstring = self.send_command(command_get)
        # once it returns a good string, parse the string and return the flow.
        li = returnstring.split(b' ')
        if len(li) > 4:
            r_str = li[4]  # 5th column is mass flow, so index 4.
            try:
                flow = float(r_str)
                if self.capacity > 1000:
                    flow *= 1000.
                flow = flow / self.capacity  # normalize as per analog api.
                self.lcd.setStyleSheet("background-color: None")
            except ValueError:
                self.lcd.setStyleSheet("background-color: Grey")
                flow = None
            if (flow < 0):
                self.lcd.setStyleSheet("background-color: Red")
                logging.error('MFC reporting negative flow.')
                logging.error(returnstring)
        else:
            self.lcd.setStyleSheet("background-color: Grey")
            flow = None
            # Failure

        return flow
    def set_dummy_vial(self, valvestate=1):
        """
        Sets the dummy vial.

        Valvestate means the state of the valve. This is inversed from a normal valve!!

        * A valvestate of 0 means to *close* the dummy by powering the solenoid.
        * A valvestate of 1 means to *open* the dummy by closing other open valves (if any) and depower the dummy valves.

        Usually, you want to pass valvestate with a 1 to close open valves and set the dummy open.

        :param valvestate: Desired state of the dummy (0 closed, 1 open). Default is 1.
        :return: True if successful setting.
        :rtype : bool
        """
        success = False
        if self.checked_id == self.dummyvial and not valvestate:  # dummy is "off" (this means open as it is normally open),
            command = "vial {0} {1} on".format(self.slaveindex, self.dummyvial)
            logging.debug(command)
            line = self.send_command(command)
            logging.debug(line)
            if not line.split()[0] == "Error":
                logging.info('Dummy ON.')
                self.vialChanged.emit(self.dummyvial)
                self.checked_id = 0
            else:
                logging.error('Cannot set dummy vial.')
                logging.error(line)
        elif self.checked_id == self.dummyvial and valvestate:  # valve is already open, do nothing and return success!
            success = True
        elif self.checked_id == 0 and valvestate:  # dummy is already (closed)
            command = "vial {0} {1} off".format(self.slaveindex, self.dummyvial)
            logging.debug(command)
            line = self.send_command(command)
            logging.debug(line)
            if not line.split()[0] == "Error":
                logging.info("Dummy OFF.")
                self.vialChanged.emit(self.dummyvial)
                self.checked_id = self.dummyvial
                success = True
                self.vialChanged.emit(self.dummyvial)
        elif self.checked_id != self.dummyvial and valvestate:  # another valve is open. close it.
            success = self._set_valveset(self.checked_id, 0)  # close open vial.
            if success:
                self.vialChanged.emit(self.dummyvial)
                QtCore.QTimer.singleShot(1000, self._valve_lockout_clear)
                self.checked_id = self.dummyvial
        else:
            logging.error("THIS SHOULDN'T HAPPEN!!!")
        return success
    
    
    def _set_valveset(self, vial_num, valvestate=1, suppress_errors=False):

        if vial_num == self.dummyvial:
            self.set_dummy_vial(valvestate)
        if valvestate:
            command = "vialOn {0} {1}".format(self.slaveindex, vial_num)
        else:
            command = "vialOff {0} {1}".format(self.slaveindex, vial_num)
        line = self.send_command(command)
        if not line.split()[0] == 'Error':
            return True
        elif not suppress_errors:
            logging.error('Cannot set valveset for vial {0}'.format(vial_num))
            logging.error(repr(line))
            return False
            
    def send_command(self, command, tries=1):
        self.serial.flushInput()
        for i in range(tries):
            # logging.debug("Sending command: {0}".format(command))
            self.serial.write(bytes("{0}\r".format(command), 'utf8'))
            line = self.read_line()
            line = self.read_line()
            morebytes = self.serial.inWaiting()
            if morebytes:
                extrabytes = self.serial.read(morebytes)
            if line:
                return line

    
    def read_line(self):
        line = None
        try:
            line = self.serial.readline()
            # logging.debug("Recieved line: {0}".format(repr(line)))
        except SerialException as e:
            print('pySerial exception: Exception that is raised on write timeouts')
        return line


class olfactometer_window(QGroupBox):
    
    def __init__(self):
        super().__init__()

        
        self.setTitle('Olfactometer')
        self.setDefaultParams()
        self.olfa_device = TeensyOlfa()
        self.generate_ui()
        #self.MFC_settings, self.COM_settings_mfc, flow_units='SCCM', setflow=-1
    
    def setDefaultParams(self):
        self.COM_settings_mfc = dict()
        self.COM_settings_mfc['baudrate'] = 115200
        
        self.MFC_settings = dict()
        self.MFC_settings['MFC_type'] = 'alicat_digital'
        self.MFC_settings['address'] = 'A'
        self.MFC_settings['arduino_port_num'] = 2
        self.MFC_settings['capacity'] = 1000
        self.MFC_settings['gas'] = "Air"
        self.MFC_settings["slave_index"] = 1 # this in full honestly is a teensy 

        # self.COM_settings_flowmeter = dict()
        # self.COM_settings_flowmeter['baudrate'] = 9600
        # self.COM_settings_flowmeter['com_port'] = 7

        self.filepath = 'R:/rinberglabspace/Users/Bea/olfactometry/flow_sensor_calibration/calibration_files/test.csv'
        self.folderpath = 'R:/rinberglabspace/Users/Bea/olfactometry/flow_sensor_calibration/calibration_files'

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
            v_vialNum = str(v+5)
            v_vial = Vial(parent=self, vialNum=v_vialNum)
            self.vials.append(v_vial)

        self.vials_layout = QVBoxLayout()
        for v in range(number_of_vials):
            #print(self.vials[v])
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
            print(int(self.portStr[3:]))
            self.COM_settings_mfc['com_port'] = int(self.portStr[3:])
            self.olfa_device.connect_olfa(self.MFC_settings, self.COM_settings_mfc, flow_units='SCCM', setflow=-1)
            

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