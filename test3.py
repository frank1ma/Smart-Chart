import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCharts import QChart, QChartView, QValueAxis, QLineSeries
from PySide6.QtGui import QPainter
from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent, QWheelEvent
from PySide6.QtCharts import QChartView, QChart
from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent, QWheelEvent
from PySide6.QtWidgets import QApplication
from PySide6.QtCharts import QChartView, QChart
from PySide6.QtCore import Qt, Signal

class MyChartView(QChartView):

    def __init__(self, chart: QChart):
        super().__init__(chart)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QChartView.RubberBandDrag)
        self.setInteractive(True)
        self.setRubberBand(QChartView.RectangleRubberBand)
        self.chart().legend().setVisible(True)
        self.chart().legend().setAlignment(Qt.AlignBottom)
        self.chart().setTitle("My Chart")
        self.chart().createDefaultAxes()


        # connect the rangeChanged signal to the on_range_changed slot
        #self.chart().axes(Qt.Horizontal)[0].rangeChanged.connect(self.on_range_changed)

        # variables to track the last mouse position and the initial chart position
        self.last_mouse_pos = None
        self.chart_pos = None

    def wheelEvent(self, event: QWheelEvent):
        # zoom in or out using the mouse wheel
        zoom_factor = 1.2
        if event.angleDelta().y() > 0:
            self.chart().zoomIn()
        else:
            self.chart().zoomOut()
        QApplication.processEvents()

    def mousePressEvent(self, event: QMouseEvent):
        # start panning when the left mouse button is pressed
        if event.button() == Qt.LeftButton:
            chart_point = self.chart().mapToValue(event.position())
            self.setDragMode(QChartView.ScrollHandDrag)
            self.last_mouse_pos = chart_point
            #print(self.last_mouse_pos)
        QApplication.processEvents()

    def mouseReleaseEvent(self, event: QMouseEvent):
        # stop panning when the left mouse button is released
        if event.button() == Qt.LeftButton:
            self.setDragMode(QChartView.RubberBandDrag)
            self.last_mouse_pos = None
        QApplication.processEvents()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.LeftButton:
            # pan the chart
            chart_point = self.chart().mapToValue(event.position())
            # pan the chart by the difference between the last mouse position and the current mouse position
            delta = chart_point - self.last_mouse_pos
            self.chart().scroll(-10*delta.x(), -10*delta.y())
            # print the current min and max value of the horizontal axis of the chart
            #print(self.chart().axes(Qt.Horizontal)[0].min(), self.chart().axes(Qt.Horizontal)[0].max())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create two QChart instances for the subplots
        chart1 = QChart()
        chart2 = QChart()

        # Create the first subplot (top)
        series1 = QLineSeries()
        series1.append(0, 1)
        series1.append(1, 3)
        series1.append(2, 2)
        chart1.addSeries(series1)

        # Create the second subplot (bottom)
        series2 = QLineSeries()
        series2.append(0, 5)
        series2.append(1, 7)
        series2.append(2, 6)
        chart2.addSeries(series2)

        # Create axes for the subplots
        axisX1 = QValueAxis()
        axisY1 = QValueAxis()
        axisX2 = QValueAxis()
        axisY2 = QValueAxis()

# Connect the rangeChanged signals of the X axes

        # Add the axes to the respective charts
        chart1.addAxis(axisX1, Qt.AlignBottom)
        chart1.addAxis(axisY1, Qt.AlignLeft)
        chart2.addAxis(axisX2, Qt.AlignBottom)
        chart2.addAxis(axisY2, Qt.AlignLeft)

        # Attach the axes to the respective series
        series1.attachAxis(axisX1)
        series1.attachAxis(axisY1)
        series2.attachAxis(axisX2)
        series2.attachAxis(axisY2)

        # Create QChartView instances for the charts
        chart_view1 = MyChartView(chart1)
        chart1.axes(Qt.Horizontal)[0].rangeChanged.connect(lambda: self.align_x_axes(chart1.axes(Qt.Horizontal)[0].min(),chart1.axes(Qt.Horizontal)[0].max(),chart2))
        chart_view1.setRenderHint(QPainter.Antialiasing)
        chart_view2 = MyChartView(chart2)
        chart_view2.setRenderHint(QPainter.Antialiasing)


        
    
        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(chart_view1)
        layout.addWidget(chart_view2)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def align_x_axes(self,min,max,chart2):
        # Align the X axes of the two charts
        chart2.axes(Qt.Horizontal)[0].setRange(min,max)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
