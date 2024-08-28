
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5 import sip
import pyqtgraph as pg


timer_interval_ms = 100         # interval for updating plot # TODO change ms to s

# Plot Display Variables
max_time_displayed_s = 15       # time frame to display # TODO remove
max_time_displayed_ms = max_time_displayed_s * 1000
flow_min = -5       # Min & Max flow values (Y-axis)
flow_max = 150

# Main plot window in olfactometer_window
class plot_window_all(QMainWindow):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent    # olfactometer_window
        self.vials_to_plot = ['-','-','-','-']          # List of vials being plotted (List items are Vial objects)
        self.vials_to_plot_names = ['-','-','-','-']
        
        self.generate_ui()

        # Layout
        self.central_widget = QWidget(self)
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)
        self.setWindowTitle('plot_window_all')
    
    def generate_ui(self):
        self.create_vial_select_groupbox()

        # Create Plot Widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('bottom', 'Time (s)')                    # Set X-axis label
        self.plot_widget.setLabel('left','Flow (SCCM)')                     # Set Y-axis label
        self.plot_widget.getPlotItem().setRange(yRange=[flow_min,flow_max]) # Set Y-axis limits
        self.legend = self.plot_widget.addLegend()                          # Add Legend

        # Initialize empty data arrays (Data to be plotted)
        self.x_data = np.array([])
        self.y_data0 = np.array([])
        self.y_data1 = np.array([])
        self.y_data2 = np.array([])
        self.y_data3 = np.array([])
        self.new_x = 0

        # Layout
        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.vial_select_groupbox)
        self.main_layout.addWidget(self.plot_widget)

    def create_vial_select_groupbox(self):
        self.vial_select_groupbox = QGroupBox('Select vials to plot flow values')   # NOTE: only 4 can be plotted at once

        # Create a button for each vial currently available
        vial_btn_layout = QHBoxLayout()
        self.active_slaves = self.parent.active_slaves
        # For each currently active slave (in olfactometer_window)
        for s in self.parent.slave_objects:
            if s.name in self.active_slaves:
                # Add the "plot_flow_btn" to a layout (button is initialized within vial)
                this_slave_layout = QVBoxLayout()
                for v in s.vials:
                    this_slave_layout.addWidget(v.plot_flow_btn)    
                # Add this slave's buttons to the layout
                vial_btn_layout.addLayout(this_slave_layout)

        self.vial_select_groupbox.setLayout(vial_btn_layout)
    
    def timerEvent(self, event):
        
        # Fetch new real-time data (get current flow from the Vial objects in "self.vials_to_plot")
        self.new_x = self.new_x + (timer_interval_ms/1000)
        self.new_ydata0 = 0 if self.vials_to_plot[0] == '-' else float(self.vials_to_plot[0].flow_value_sccm)
        self.new_ydata1 = 0 if self.vials_to_plot[1] == '-' else float(self.vials_to_plot[1].flow_value_sccm)
        self.new_ydata2 = 0 if self.vials_to_plot[2] == '-' else float(self.vials_to_plot[2].flow_value_sccm)
        self.new_ydata3 = 0 if self.vials_to_plot[3] == '-' else float(self.vials_to_plot[3].flow_value_sccm)
        
        # Append new data to existing data
        self.x_data = np.append(self.x_data, self.new_x)
        self.y_data0 = np.append(self.y_data0, self.new_ydata0)
        self.y_data1 = np.append(self.y_data1, self.new_ydata1)
        self.y_data2 = np.append(self.y_data2, self.new_ydata2)
        self.y_data3 = np.append(self.y_data3, self.new_ydata3)
        
        # Keep only the last x data points to avoid excessive memory usage
        num_data_points_displayed = int(max_time_displayed_ms/timer_interval_ms)
        self.x_data = self.x_data[-num_data_points_displayed:]
        self.y_data0 = self.y_data0[-num_data_points_displayed:]
        self.y_data1 = self.y_data1[-num_data_points_displayed:]
        self.y_data2 = self.y_data2[-num_data_points_displayed:]
        self.y_data3 = self.y_data3[-num_data_points_displayed:]
        
        # Plot and clear previous plot
        self.plot_widget.plot(self.x_data, self.y_data0, pen='b', clear=True, name = self.vials_to_plot_names[0], yAxis='left')
        self.plot_widget.plot(self.x_data, self.y_data1, pen='r', clear=False, name = self.vials_to_plot_names[1], yAxis='left')
        self.plot_widget.plot(self.x_data, self.y_data2, pen='g', clear=False, name = self.vials_to_plot_names[2], yAxis='left')
        self.plot_widget.plot(self.x_data, self.y_data3, pen='m', clear=False, name = self.vials_to_plot_names[3], yAxis='left')
        
        # Update legend
        self.legend.scene().invalidate()

    def update_vial_select_groupbox(self):  # NOTE: don't think this is working 7/30/2024
        # Called from olfa window, rechecks which slaves are active
        self.prev_active_slaves = self.active_slaves
        if self.active_slaves == []:
            self.active_slaves = self.parent.active_slaves
            
        if self.prev_active_slaves != self.active_slaves:
            sip.delete(self.vial_select_groupbox)   # remove the vial select groupbox
            self.create_vial_select_groupbox()      # create it again
            self.main_layout.insertWidget(0, self.vial_select_groupbox) # add it back into the layout

    def timer_start(self):
        # Called from olfa window, creates & starts timer 
        self.timer = self.startTimer(timer_interval_ms)

    def closeEvent(self, event):
        # Untoggle button in olfa GUI
        self.parent.show_flow_plot_btn.setChecked(False)

# Single vial plot in vial details popup
class plot_window_single_vial(QMainWindow):
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent    # vial details popup window
        self.vialNum = self.parent.full_vialNum

        self.generate_ui()

        # LAYOUT
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)
        layout.addWidget(self.plot_widget)
        self.setWindowTitle(self.vialNum + ' flow/ctrl plot: WARNING: not fully debugged')
    
    def generate_ui(self):

        # Create Plot Widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('bottom', 'Time (s)')                # Set X-axis label
        self.plot_widget.setLabel('left','Flow (SCCM)')#, color = 'b')  # Set Y-axis1 label
        self.plot_widget.getPlotItem().setRange(yRange = [-10,200])     # Set Y-axis1 limits
        '''
        #self.plot_widget.getAxis('bottom').setStyle(showValues=False)   # Disable X-axis labels
        #self.plot_widget.getAxis('bottom').setTicks(None)              # Disable X-axis tick marks
        '''
        self.plot_widget.showAxis('right')                              # Create Y-axis2
        self.plot_widget.getAxis('right').setLabel('Ctrl value (int)')  # Set Y-axis2 label
        self.plot_widget.getPlotItem().getViewBox().setYRange(min=0, max=255, padding=0)    # Set Y-axis2 limits
        
        '''
        # plots ctrl on the left axis
        self.p2 = pg.ViewBox()
        self.p1.showAxis('right')
        self.p1.scene().addItem(self.p2)
        self.p1.getAxis('right').linkToView(self.p2)
        self.p2.setXLink(self.p1)
        self.p1.getAxis('right').setLabel('Ctrl value (int)')#, color='r')
        self.p2.setRange(yRange=[0,260])
        '''
        '''
        #self.plot_widget.getPlotItem().setRange(yRange = [0,255])   # sets them both to shi
        #self.plot_widget.getPlotItem().getViewBox().setRange(yRange=[0, 255])
        #self.plot_widget.getPlotItem().getAxis('right').setRange(yRange=[0,255])    # Set Y-axis limits
        #self.plot_widget.getPlotItem().getViewBox().setYRange([0,255])
        '''
        
        self.legend = self.plot_widget.addLegend()                              # Add Legend
        self.legend.setParentItem(self.plot_widget.getViewBox())                # Set location of the legend
        self.legend.anchor(itemPos=(1,1), parentPos=(1,1), offset=(-30,-30))    # offset 0 = left/top edge

        # Initialize empty data arrays (Data to be plotted)
        self.x_data = np.array([])
        self.y_data1 = np.array([])
        self.y_data2 = np.array([])
        self.new_x = 0
    
    def timerEvent(self, event):
        
        # Fetch new real-time data
        self.new_x = self.new_x + (timer_interval_ms/1000)
        self.new_y1 = int(self.parent.parent.flow_value_sccm)   # parent.parent is the vial object
        self.new_y2 = int(self.parent.parent.ctrl_value_int)

        # Append new data to existing data
        self.x_data = np.append(self.x_data, self.new_x)
        self.y_data1 = np.append(self.y_data1, self.new_y1)
        self.y_data2 = np.append(self.y_data2, self.new_y2)

        # Keep only the last x data points to avoid excessive memory usage
        num_data_points_displayed = int(max_time_displayed_ms/timer_interval_ms)
        self.x_data = self.x_data[-num_data_points_displayed:]
        self.y_data1 = self.y_data1[-num_data_points_displayed:]
        self.y_data2 = self.y_data2[-num_data_points_displayed:]

        # Plot and clear previous plot
        self.plot_widget.plot(self.x_data, self.y_data1, pen = 'w', clear=True, name = 'Flow (sccm)', yAxis='left')
        self.plot_widget.plot(self.x_data, self.y_data2, pen = 'c', clear=False, name = 'Ctrl (int)', yAxis='right')

        # Update legend
        self.legend.scene().invalidate()

    def timer_start(self):
        # Called from vial popup, creates & starts timer
        self.timer = self.startTimer(timer_interval_ms)

    def closeEvent(self, event):
        # Untoggle button in vial details window
        self.parent.show_plot_btn.setChecked(False)
