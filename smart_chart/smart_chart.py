# import necessary modules in PySide6
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication,QMainWindow,QMenu,QToolButton,QFrame,QGridLayout
from PySide6.QtCharts import QChart, QChartView,QLineSeries
from PySide6.QtCore import QObject, QEvent,Qt
from PySide6.QtGui import QAction
#import plot_navigator
from plot_navigator.plot_navigator import PlotNavigator
from smart_chart_view import SmartChartView
import control
import numpy as np
#add plot_navigator/icon/plot_navigator_rc.py into python path

# create smart chart class as QFrame
class SmartChart(QFrame):
    # constructor
    def __init__(self, *args, **kwargs):
        # call super class constructor
        super().__init__(*args, **kwargs)
        layout = QGridLayout(self)
        # add a chart to the smart chart
        self.chart = QChart()
        self.chart.setTitle("My Chart")
        # add chart to the chart view
        self.chart_view = SmartChartView(self.chart,self)
        # add navigation bar to the smart chart
        self.nav_bar = PlotNavigator(self.chart_view)

        # create a new chart
        #self.chart2 = QChart()
        #self.chart2.setTitle("My Chart2")
        # add another chart view to the smart chart
        #self.chart_view2 = SmartChartView(self.chart2,self)
        # add navigation bar to the smart chart
        #self.nav_bar2 = PlotNavigator(self.chart_view2)
        #self.nav_bar2.setVisible(False)

        # add the chart view and navigation bar to the smart chart
        self.chart_view.setupNavigator(self.nav_bar)
        #self.chart_view2.setupNavigator(self.nav_bar2)

        # add subchart to the smart chart
        #self.chart_view.setSubChat(self.chart_view2)
        #self.chart_view2.setSubChat(self.chart_view)

        #self.chart_view.plotXY([1,2,3],[1,2,3])
    # setup the layout of the smart chart   
        layout.addWidget(self.nav_bar,0,0,1,2)
        # add hide button to the layout
        layout.addWidget(self.chart_view,1,0,1,3)

        #layout.addWidget(self.nav_bar2,2,0,1,2)
        # add hide button to the layout
        #layout.addWidget(self.chart_view2,3,0,1,3)

        self.setLayout(layout)

        # right click on the smart chart to pop up a menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def show_context_menu(self, pos):
        # if pos is on any chart view, return
        if self.chart_view.geometry().contains(pos) or self.chart_view2.geometry().contains(pos):
            return
        menu = QMenu()
        menu.addSeparator()
        if self.nav_bar.isVisible():
            menu.addAction(QAction("Hide Navigator Bar", self,triggered=self.toggleMainNavBar))
        else:
            menu.addAction(QAction("Show Navigator Bar", self,triggered=self.toggleMainNavBar))
        if self.nav_bar2.isVisible():
            menu.addAction(QAction("Hide Sub Navigator Bar", self,triggered=self.toggleSubNavBar))
        else:
            menu.addAction(QAction("Show Sub Navigator Bar", self,triggered=self.toggleSubNavBar))
        menu.exec(self.mapToGlobal(pos))

    def toggleMainNavBar(self):
        self.nav_bar.setVisible(not self.nav_bar.isVisible())
    
    def toggleSubNavBar(self):
        self.nav_bar2.setVisible(not self.nav_bar2.isVisible())
        


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Add the custom frame to the main window
        custom_frame = SmartChart()
        self.setCentralWidget(custom_frame)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.setGeometry(800, 400, 800, 600)
    window.show()
    
    sys1 = control.tf([1], [1,2,1])
    mag,phase,omega = control.bode_plot(sys1,dB=True,deg=True,omega_limits=(0.1,1000),omega_num=500,plot=False)

    widget:SmartChart = window.centralWidget()
    widget.chart_view.plotXY(omega,20*np.log10(mag),series=widget.chart_view.chart().series()[0])
    #widget.chart_view2.plotXY(omega,phase,series=widget.chart_view.chart().series()[0])
    app.exec()
