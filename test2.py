from PySide6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView
from PySide6.QtGui import QTransform, Qt
#import Qpainter
from PySide6.QtGui import QPainter

from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent, QWheelEvent
from PySide6.QtCharts import QChartView, QChart,QLineSeries

from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent, QWheelEvent
from PySide6.QtCharts import QChartView, QChart
from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent, QWheelEvent
from PySide6.QtWidgets import QApplication
from PySide6.QtCharts import QChartView, QChart

class MyChartView(QChartView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QChartView.RubberBandDrag)
        self.setInteractive(True)
        self.setRubberBand(QChartView.RectangleRubberBand)
        self.chart().legend().setVisible(True)
        self.chart().legend().setAlignment(Qt.AlignBottom)
        self.chart().setTitle("My Chart")
        #add sample data point to series   
        self.series = QLineSeries()
        self.series.append(0, 6)
        self.series.append(2, 4)
        self.series.append(3, 8)
        self.series.append(7, 4)
        self.series.append(10, 5)
        self.chart().addSeries(self.series)
        self.chart().createDefaultAxes()
        


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
            print(self.last_mouse_pos)
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


if __name__ == '__main__':
    app = QApplication()
    view = MyChartView()
    view.show()
    app.exec()
