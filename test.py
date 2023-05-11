from PySide6.QtCharts import QChartView,QChart,QLineSeries,QValueAxis
from PySide6.QtWidgets import QMainWindow, QApplication,QGraphicsView,QWidget,QVBoxLayout,QPushButton
#import QPainter
from PySide6.QtGui import QPainter
#import Qt 
from PySide6.QtCore import Qt

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # add vertical layout to QMainwindow
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # create a chart
        self.chart = QChart()

        # add some data to the chart
        series = QLineSeries()
        series.append(0, 1)
        series.append(1, 3)
        series.append(2, 4)
        series.append(3, 2)
        self.chart.addSeries(series)

        # create a chart view
        self.chartView = QChartView(self.chart)
        # # add a navigator to the chart view
        # chartView.setRubberBand(QChartView.RubberBand.RectangleRubberBand)
        # chartView.setRenderHint(QPainter.Antialiasing)
        # chartView.setOptimizationFlag(QGraphicsView.DontAdjustForAntialiasing, True)
        # chartView.setDragMode(QGraphicsView.ScrollHandDrag)

        #add QChartView to the layout
        self.layout.addWidget(self.chartView)

        #add a button to enable zooming to layout
        self.button = QPushButton("Enable Zooming")
        self.button.setCheckable(True)
        self.button.setChecked(False)
        self.button.clicked.connect(self.enableZooming)
        self.layout.addWidget(self.button)
        # create a new Qwidget
        widget = QWidget()
        # set the layout of the widget
        widget.setLayout(self.layout)

        # add the chart view to the main window
        self.setCentralWidget(widget)
        
    # enable zooming
    def enableZooming(self):
        #if button is pressed
        if not self.button.isChecked():
            # change the style of cursor to open hand
            self.chartView.setCursor(Qt.OpenHandCursor)
            # disable the zooming
            self.chartView.setRubberBand(QChartView.NoRubberBand)
            self.chartView.setDragMode(QGraphicsView.NoDrag)
        else:
            print("button is down")
            self.button.setDown(True)
            # change the style of cursor to arrow
            self.chartView.setCursor(Qt.ArrowCursor)
            # enable the zooming
            self.chartView.setRubberBand(QChartView.RubberBand.RectangleRubberBand)
            self.chartView.setRenderHint(QPainter.Antialiasing)
            self.chartView.setOptimizationFlag(QGraphicsView.DontAdjustForAntialiasing, True)
            # enable the drag mode
            #self.chartView.setDragMode(QGraphicsView.ScrollHandDrag)
            # enable the pan mode
            self.chartView.setDragMode(QGraphicsView.DragMode.RubberBandDrag)


if __name__ == '__main__':
    app = QApplication([])
    window = MyMainWindow()
    window.show()
    app.exec()
