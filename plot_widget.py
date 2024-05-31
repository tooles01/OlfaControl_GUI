
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5 import sip
import pyqtgraph as pg


timer_interval_ms = 100         # interval for updating plot

# Plot Display Variables
max_time_displayed_s = 10       # time frame to display
flow_min = -5
flow_max = 120


# Slave: all vials (flow & ctrl plots)
class slave_plot_window(QMainWindow):

    def __init__(self, parent):
        super().__init__()

        self.parent = parent
        self.slave_object = parent
        self.slave_name = self.parent.name
        #self.num_vials = len(self.parent.vials)

        self.vials_to_plot = ['0','0','0','0']
        self.vials_to_plot_names = ['0','0','0','0']

        self.generate_ui()

        # Layout
        self.central_widget = QWidget(self)
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.flow_plot_groupbox)
        self.main_layout.addWidget(self.ctrl_plot_groupbox)
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

        '''
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('bottom', 'Time (ms)')                # Set X-axis label
        self.plot_widget.setLabel('left','Flow (SCCM)')                 # Set Y-axis label
        self.plot_widget.getPlotItem().setRange(yRange = [-10,210])     # Set Y-axis limits

        self.legend = self.plot_widget.addLegend()

        self.timer = self.startTimer(timer_interval_ms)

        # Initialize empty data
        self.x_data = np.array([])
        self.y_data_array = []
        for v in self.parent.vials:
            this_y_data = np.array([])
            self.y_data_array.append(this_y_data)
        self.new_x = 0
        '''
        
        # layout
        #layout = QVBoxLayout(self.central_widget)
        #layout.addWidget(self.plot_widget)
        self.setWindowTitle('Olfa ' + self.slave_name + ' flow data')
    
    
    def generate_ui(self):
        
        #### FLOW PLOT
        self.flow_plot_groupbox = QGroupBox()
        
        # Vial Select Buttons
        self.vial_select_flow_groupbox = QGroupBox('Select to plot flow')
        self.vial_flow_btn_layout = QVBoxLayout()
        for v in self.slave_object.vials:
            self.vial_flow_btn_layout.addWidget(v.plot_flow_btn)    # create a button for each vial
        self.vial_select_flow_groupbox.setLayout(self.vial_flow_btn_layout)
        
        # Plot Widget
        self.flow_plot_widget = pg.PlotWidget()
        self.flow_plot_widget.setLabel('bottom', 'Time (ms)')                # Set X-axis label
        self.flow_plot_widget.setLabel('left','Flow (SCCM)')                 # Set Y-axis label
        self.flow_plot_widget.getPlotItem().setRange(yRange = [-5,120])      # Set Y-axis limits
        self.legend = self.flow_plot_widget.addLegend()
        self.timer = self.startTimer(timer_interval_ms)
        
        # Initialize empty data
        self.x_data = np.array([])
        self.y_data0 = np.array([])
        self.y_data1 = np.array([])
        self.y_data2 = np.array([])
        self.y_data3 = np.array([])
        self.new_x = 0
        
        # Flow Layout
        self.flow_plot_layout = QHBoxLayout()
        self.flow_plot_layout.addWidget(self.vial_select_flow_groupbox)
        self.flow_plot_layout.addWidget(self.flow_plot_widget)
        self.flow_plot_groupbox.setLayout(self.flow_plot_layout)
        
        
        #### CTRL PLOT
        self.ctrl_plot_groupbox = QGroupBox()
        
        # Vial Select Buttons
        self.vial_select_ctrl_groupbox = QGroupBox('Select to plot ctrl')
        self.vial_ctrl_btn_layout = QVBoxLayout()
        for v in self.slave_object.vials:
            self.vial_ctrl_btn_layout.addWidget(v.plot_ctrl_btn)   # create a button for each vial
        self.vial_select_ctrl_groupbox.setLayout(self.vial_ctrl_btn_layout)
        
        # Plot Widget
        self.ctrl_plot_widget = pg.PlotWidget()
        self.ctrl_plot_widget.setLabel('bottom','Time (ms)')
        self.ctrl_plot_widget.setLabel('left','Ctrl (int)')
        self.ctrl_plot_widget.getPlotItem().setRange(yRange = [-5,260])
        self.legend = self.ctrl_plot_widget.addLegend()
        
        # Ctrl Layout
        self.ctrl_plot_layout = QHBoxLayout()
        self.ctrl_plot_layout.addWidget(self.vial_select_ctrl_groupbox)
        self.ctrl_plot_layout.addWidget(self.ctrl_plot_widget)
        self.ctrl_plot_groupbox.setLayout(self.ctrl_plot_layout)
    
    def timerEvent(self, event):
        # Fetch new real-time (flow) data
        self.new_x = self.new_x + timer_interval_ms
        self.new_ydata0 = 0 if self.vials_to_plot[0] == '0' else float(self.vials_to_plot[0].flow_value_sccm)
        self.new_ydata1 = 0 if self.vials_to_plot[1] == '0' else float(self.vials_to_plot[1].flow_value_sccm)
        self.new_ydata2 = 0 if self.vials_to_plot[2] == '0' else float(self.vials_to_plot[2].flow_value_sccm)
        self.new_ydata3 = 0 if self.vials_to_plot[3] == '0' else float(self.vials_to_plot[3].flow_value_sccm)
        
        # Append new data to existing data
        self.x_data = np.append(self.x_data,self.new_x)
        self.y_data0 = np.append(self.y_data0, self.new_ydata0)
        self.y_data1 = np.append(self.y_data1, self.new_ydata1)
        self.y_data2 = np.append(self.y_data2, self.new_ydata2)
        self.y_data3 = np.append(self.y_data3, self.new_ydata3)

        # Keep only the last x data points to avoid excessive memory usage
        num_data_points_displayed = int((max_time_displayed_s * 1000) / timer_interval_ms)
        self.x_data = self.x_data[-num_data_points_displayed:]
        self.y_data0 = self.y_data0[-num_data_points_displayed:]
        self.y_data1 = self.y_data1[-num_data_points_displayed:]
        self.y_data2 = self.y_data2[-num_data_points_displayed:]
        self.y_data3 = self.y_data3[-num_data_points_displayed:]

        # Plot and clear previous plot
        self.flow_plot_widget.plot(self.x_data, self.y_data0, pen='r', clear=True, name = self.vials_to_plot_names[0])
        self.flow_plot_widget.plot(self.x_data, self.y_data1, pen='b', clear=False, name = self.vials_to_plot_names[1])
        self.flow_plot_widget.plot(self.x_data, self.y_data2, pen='g', clear=False, name = self.vials_to_plot_names[2])
        self.flow_plot_widget.plot(self.x_data, self.y_data3, pen='m', clear=False, name = self.vials_to_plot_names[3])

        '''
        for n in range(self.num_vials):
            new_y1 = int(self.parent.vials[n].flow_value_sccm)  # get this vial's flow value
            
            old_y_data = self.y_data_array[n]   # append to existing data
            new_y_data = np.append(old_y_data, new_y1)
            
            new_y_data = new_y_data[-num_data_points_displayed:]    # keep only the last x data points
            self.x_data = self.x_data[-num_data_points_displayed:]
            self.y_data_array[n] = new_y_data   # update the array

            # plot and clear previous plot
            if n == 0:  # if it's the first, one, clear the previous plot
                self.plot_widget.plot(self.x_data, new_y_data, clear=True, name = self.parent.vials[n].full_vialNum)
            else:
                self.plot_widget.plot(self.x_data, new_y_data, clear=False, name = self.parent.vials[n].full_vialNum)
        '''
        
        # Update legend
        self.legend.scene().invalidate()
    
    def closeEvent(self, event):
        # Untoggle button in olfa GUI
        self.parent.show_plot_btn.setChecked(False)
