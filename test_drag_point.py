import sys
from PySide6.QtCore import Qt, QPointF,QPoint
from PySide6.QtCharts import QChart, QChartView, QLineSeries,QValueAxis
from PySide6.QtGui import QPainter,QPen
from PySide6.QtWidgets import QApplication


class DraggableChartView(QChartView):
    def __init__(self, chart: QChart, parent=None):
        super().__init__(chart, parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setMouseTracking(True)
        self.selected_point = None
        self.series = None

    def set_series(self, series: QLineSeries):
        self.series = series

    def mousePressEvent(self, event):
# Convert mouse position to scene coordinate system
        if self.series:
            pos = event.position()  # Get the position of the mouse click
            chart = self.chart()  # Get the QChart object
            x_axis = chart.axes(Qt.Orientation.Horizontal)  # Get the x-axis object
            y_axis = chart.axes(Qt.Orientation.Vertical)   # Get the y-axis object
            chart_point = chart.mapToValue(pos,self.series)  # Map the x-coordinate to the chart's coordinate system

            for i, point in enumerate(self.series.points()):
                if self.is_near(chart_point, point):
                    self.selected_point = i
                    print(point)
                    break
            else:
                self.selected_point = None

    def mouseMoveEvent(self, event):
        if self.selected_point is not None and self.series:
            chart_point = chart.mapToValue(event.position(),self.series)
            self.series.replace(self.selected_point, chart_point)
            #update the chart
            self.chart().update()

    def mouseReleaseEvent(self, event):
        self.selected_point = None

    def is_near(self, point1, point2):
        threshold = 15.0  # You can adjust this value for your needs
        return (
            abs(point1.x() - point2.x()) <= threshold
            and abs(point1.y() - point2.y()) <= threshold
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    chart = QChart()
    chart_view = DraggableChartView(chart)

    line_series = QLineSeries()
    line_series.append(20, 20)
    line_series.append(100, 100)
    line_series.append(200, 200)
    # show points to red
    line_series.setPointsVisible(True)
    pen = QPen(Qt.red)
    pen.setWidth(5)
    line_series.setPen(pen)

    chart.addSeries(line_series)
    chart.createDefaultAxes()

    chart_view.set_series(line_series)
    chart_view.setWindowTitle("Draggable Points Example")
    chart_view.resize(500, 300)
    chart_view.show()

    sys.exit(app.exec())
