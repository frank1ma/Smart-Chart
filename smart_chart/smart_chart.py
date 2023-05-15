# import necessary modules in PySide6
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication,QMainWindow,QVBoxLayout,QListWidget,QFrame,QVBoxLayout,QLabel,QWidget,QToolBar
from PySide6.QtCharts import QChart, QChartView,QLineSeries
from PySide6.QtCore import QObject, QEvent,Qt
from PySide6.QtGui import QAction
#import plot_navigator
from plot_navigator.plot_navigator import PlotNavigator
from smart_chart_view import SmartChartView

#add plot_navigator/icon/plot_navigator_rc.py into python path

# create smart chart class as QFrame
class SmartChart(QFrame):
    # constructor
    def __init__(self, *args, **kwargs):
        # call super class constructor
        super().__init__(*args, **kwargs)
        layout = QVBoxLayout(self)
        # add a chart to the smart chart
        self.chart = QChart()
        self.chart.setTitle("My Chart")
        # add chart to the chart view
        self.chart_view = SmartChartView(self.chart,self)
        # add navigation bar to the smart chart
        self.nav_bar = PlotNavigator(self.chart_view)

        # create a new chart
        self.chart2 = QChart()
        self.chart2.setTitle("My Chart2")
        # add another chart view to the smart chart
        self.chart_view2 = SmartChartView(self.chart2,self)
        # add navigation bar to the smart chart
        self.nav_bar2 = PlotNavigator(self.chart_view2)
        self.nav_bar2.setVisible(False)

        # add the chart view and navigation bar to the smart chart
        self.chart_view.setupNavigator(self.nav_bar)
        self.chart_view2.setupNavigator(self.nav_bar2)

        # add subchart to the smart chart
        self.chart_view.setSubChat(self.chart_view2)

    # setup the layout of the smart chart   
        layout.addWidget(self.nav_bar)
        layout.addWidget(self.chart_view)
        layout.addWidget(self.nav_bar2)
        layout.addWidget(self.chart_view2)

        self.setLayout(layout)

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

    app.exec()
