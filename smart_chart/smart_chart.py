# import necessary modules in PySide6
from PySide6.QtWidgets import QApplication,QMainWindow,QMenu,QFrame,QGridLayout
from PySide6.QtCharts import QChart, QChartView,QLineSeries
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction,QResizeEvent
from plot_navigator.plot_navigator import PlotNavigator
from smart_chart_view import SmartChartView
import control
import numpy as np

# create smart chart class as QFrame
class SmartChart(QFrame):
    """
    SmartChart is a QFrame that contains a chart view and a navigation bar.
    """
    # constructor
    def __init__(self, *args, plot_type:str="normal",sub_plot_type:str="bode_phase", **kwargs):
        # call super class constructor
        super().__init__(*args, **kwargs)
        layout = QGridLayout(self)
        # add a chart to the smart chart
        self.chart = QChart()
        self.chart.setTitle("My Chart")
        # add chart to the chart view
        self.chart_view = SmartChartView(self.chart,self,plot_type)
        # add navigation bar to the smart chart
        self.nav_bar = PlotNavigator(self.chart_view)

        # create a new chart
        self.chart2 = QChart()
        self.chart2.setTitle("My Chart2")
        # add another chart view to the smart chart
        self.chart_view2 = SmartChartView(self.chart2,self,sub_plot_type)
        # add navigation bar to the smart chart
        self.nav_bar2 = PlotNavigator(self.chart_view2)
        self.nav_bar2.setVisible(False)

        # add the chart view and navigation bar to the smart chart
        self.chart_view.setupNavigator(self.nav_bar)
        self.chart_view2.setupNavigator(self.nav_bar2)

        # add subchart to the smart chart
        self.chart_view.setSubChat(self.chart_view2)
        self.chart_view2.setSubChat(self.chart_view)

        #self.chart_view.plotXY([1,2,3],[1,2,3])
    # setup the layout of the smart chart   
        layout.addWidget(self.nav_bar,0,0,1,2)
        # add hide button to the layout
        layout.addWidget(self.chart_view,1,0,1,3)

        layout.addWidget(self.nav_bar2,2,0,1,2)
        # add hide button to the layout
        layout.addWidget(self.chart_view2,3,0,1,3)

        self.setLayout(layout)

        # right click on the smart chart to pop up a menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
    
    def showContextMenu(self, pos):
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

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.chart_view.updateAuxLineMarker()
        self.chart_view.updateMarkerText()
        self.chart_view.updateAllVLM()
        self.chart_view2.updateAuxLineMarker()
        self.chart_view2.updateMarkerText()
        self.chart_view2.updateAllVLM()
        #self.chart_view.adjustYTicks()
        return super().resizeEvent(event)
        


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Add the custom frame to the main window
        #custom_frame = SmartChart(plot_type="bode_mag",sub_plot_type="bode_phase")
        custom_frame = SmartChart(plot_type="nichols")
        self.setCentralWidget(custom_frame)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.setGeometry(800, 400, 800, 600)
    window.show()
    widget:SmartChart = window.centralWidget()
    widget.chart_view.sub_chart=None
    widget.chart_view2.hide()

    sys1 = control.tf([10], [1,2,1,1])
    #sys1 = control.zpk([-1,-2,4],[-30,-1,-2,-3],100)
    mag,phase,omega = control.bode_plot(sys1,dB=True,deg=True,omega_limits=(0.1,2500),omega_num=500,plot=False)
    sys2 = control.tf([1000], [1,5,5,1])
    mag1,phase1,omega1 = control.bode_plot(sys2,dB=True,deg=True,omega_limits=(0.1,2500),omega_num=500,plot=False)

    
    #wrapped_phase_degree = widget.chart_view.wrapPhase(phase)
    widget.chart_view.plotXY(phase/np.pi*180,20*np.log10(mag))
    widget.chart_view.setNicholsFrequencyData(omega)
    #widget.chart_view.showNicholsGrid()

    widget.chart_view.plotXY(phase1/np.pi*180,20*np.log10(mag1))
    widget.chart_view.setNicholsFrequencyData(omega1)

    # widget.chart_view.plotXY(omega,20*np.log10(mag))
    # #widget.chart_view.changeAxesType(new_x_axis_type="log",new_y_axis_type="linear")
    # widget.chart_view.x_axis.setTitleText("Frequency (Hz)")
    # widget.chart_view.y_axis.setTitleText("Magnitude (dB)")
    # widget.chart_view2.plotXY(omega,phase/np.pi*180)
    # #widget.chart_view2.changeAxesType(new_x_axis_type="log",new_y_axis_type="linear")
    # widget.chart_view2.x_axis.setTitleText("Frequency (Hz)")
    # widget.chart_view2.y_axis.setTitleText("Phase (deg)")
    # widget.chart_view.calculateGainMargin(omega,20*np.log10(mag),phase/np.pi*180)
    # widget.chart_view.showGainMarginMarker(omega,20*np.log10(mag),phase/np.pi*180,True)
    # a = widget.chart_view.calculatePhaseMargin(omega,20*np.log10(mag),phase/np.pi*180,True)
    app.exec()
