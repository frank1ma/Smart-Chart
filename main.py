#import QmainWindow
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QWidget
# import PlotNavigator class
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QFrame
from plot_navigator.plot_navigator import PlotNavigator
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCharts import QChart, QChartView, QValueAxis, QLineSeries
from PySide6.QtGui import QPainter
from PySide6.QtCore import Qt
from PySide6.QtCharts import QChartView, QChart
from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent, QWheelEvent,QShowEvent
from PySide6.QtWidgets import QApplication
from PySide6.QtCharts import QChartView, QChart
from PySide6.QtCore import Qt, Signal
#QGraphicsView
from PySide6.QtWidgets import QGraphicsView

class MyChartView(QChartView):

    def __init__(self, chart: QChart):
        super().__init__(chart)
        #self.setRenderHint(QPainter.Antialiasing)
        #self.setDragMode(QChartView.RubberBandDrag)
        self.setInteractive(True)
        #self.setRubberBand(QChartView.RectangleRubberBand)
        self.chart().legend().setVisible(True)
        self.chart().legend().setAlignment(Qt.AlignBottom)
        self.chart().setTitle("My Chart")
        self.chart().createDefaultAxes()

    def wheelEvent(self, event: QWheelEvent):
        # zoom in or out using the mouse wheel
        if event.angleDelta().y() > 0:
            self.chart().zoomIn()
        else:
            self.chart().zoomOut()
        QApplication.processEvents()

class MainWindow(QMainWindow):
    def __init__(self):
        # init the class with QMainWindow
        super().__init__()
        # set the title of the window
        self.setWindowTitle("Plot Navigator")
        # add vertical layout to QMainWindow
        self.layout = QVBoxLayout()
        # add QChartView to the layout
        self.setupChart()
        # create a PlotNavigator object

        self.plot_navigator = PlotNavigator(self.chart_view)

        # set the layout of the QMainWindow
        self.setLayout(self.layout)
        # add the plot navigator to the layout
        self.layout.addWidget(self.plot_navigator)
        # create a new QWidget
        widget = QWidget()
        # set the layout of the widget
        widget.setLayout(self.layout)
        # add the widget to the QMainWindow
        self.setCentralWidget(widget)
    # set up QChart
    def setupChart(self):
        # create a QChart object
        self.chart = QChart()
        # add some data to the chart
        series = QLineSeries()
        series.append(0, 1)
        series.append(1, 3)
        series.append(2, 4)
        series.append(3, 2)
        self.chart.addSeries(series)

        axisX1 = QValueAxis()
        axisY1 = QValueAxis()
        self.chart.addAxis(axisX1, Qt.AlignBottom)
        self.chart.addAxis(axisY1, Qt.AlignLeft)
        series.attachAxis(axisX1)
        series.attachAxis(axisY1)

        # create a QChartView object
        self.chart_view = MyChartView(self.chart)
        # add QChartView to the layout
        self.layout.addWidget(self.chart_view)
        # add a navigator to the chart view
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setOptimizationFlag(QGraphicsView.DontAdjustForAntialiasing, True)
        
#create a QApplication
if __name__ == "__main__":
    app = QApplication([])
    # create a MainWindow object
    window = MainWindow()
    # show the window
    window.show()
    # execute the app
    app.exec()


