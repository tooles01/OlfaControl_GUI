
import numpy as np
from PyQt5.QtWidgets import *
import pyqtgraph as pg


timer_interval_ms = 10          # interval for updating plot
max_time_displayed_s = 10       # time frame to display


class plot_window(QMainWindow):
    
    def __init__(self, parent):
        super().__init__()

        self.parent = parent    # parent is the slave object
        self.vialNum = self.parent.full_vialNum

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)        
        
        
        self.plot_widget = pg.PlotWidget()
        self.p1 = self.plot_widget.plotItem

        self.plot_widget.setLabel('bottom', 'Time (s)')                 # Set X-axis label
        self.plot_widget.setLabel('left','Flow (SCCM)')#, color = 'b')                 # Set Y-axis label
        
        self.plot_widget.getPlotItem().setRange(yRange = [-10,260])     # Set Y-axis limits
        
        self.plot_widget.getAxis('bottom').setStyle(showValues=False)   # Disable X-axis labels
        self.plot_widget.getAxis('bottom').setTicks(None)               # Disable X-axis tick marks

        self.plot_widget.showAxis('right')                              # Create second Y-axis
        self.plot_widget.getAxis('right').setLabel('Ctrl value (int)')  # Set Y-axis label
        self.plot_widget.getPlotItem().getViewBox().setYRange(min=0, max=255, padding=0)
        
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
        
        self.legend = self.plot_widget.addLegend()
        self.legend.setParentItem(self.plot_widget.getViewBox())                # Set location of the legend
        self.legend.anchor(itemPos=(1,1), parentPos=(1,1), offset=(-30,-30))    # offset 0 = left/top edge

        self.timer = self.startTimer(timer_interval_ms)

        # Initialize empty data
        self.x_data = np.array([])
        self.y_data1 = np.array([])
        self.y_data2 = np.array([])
        self.new_x = 0
        

        # LAYOUT
        layout = QVBoxLayout(self.central_widget)
        layout.addWidget(self.plot_widget)
        self.setWindowTitle(self.vialNum + ' flow')
    
    def timerEvent(self, event):
        
        # Fetch new real-time data
        num_data_points_displayed = int((max_time_displayed_s * 1000) / timer_interval_ms)
        self.new_x = self.new_x + timer_interval_ms
        self.new_y1 = int(self.parent.parent.flow_value_sccm)   # parent.parent is the vial object
        self.new_y2 = int(self.parent.parent.ctrl_value_int)

        # Append new data to existing data
        self.x_data = np.append(self.x_data, self.new_x)
        self.y_data1 = np.append(self.y_data1, self.new_y1)
        self.y_data2 = np.append(self.y_data2, self.new_y2)

        # Keep only the last x data points to avoid excessive memory usage
        self.x_data = self.x_data[-num_data_points_displayed:]
        self.y_data1 = self.y_data1[-num_data_points_displayed:]
        self.y_data2 = self.y_data2[-num_data_points_displayed:]

        # Plot and clear previous plot
        self.plot_widget.plot(self.x_data, self.y_data1, pen = 'b', clear=True, name = 'Flow (sccm)', yAxis='left')
        self.plot_widget.plot(self.x_data, self.y_data2, pen = 'r', clear=False, name = 'Ctrl (int)', yAxis='right')


        # Update legend
        self.legend.scene().invalidate()

        
        
