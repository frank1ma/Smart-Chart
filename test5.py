from PySide6.QtWidgets import QApplication
from PySide6.QtCharts import QChartView, QLineSeries, QChart, QValueAxis
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QMouseEvent
#import QPainter
from PySide6.QtGui import QPainter


class DraggableVerticalLineChartView(QChartView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.Antialiasing)

        self.vertical_line_series = QLineSeries()
        self.is_line_dragging = False

    def set_chart(self, chart):
        self.setChart(chart)
        chart.addSeries(self.vertical_line_series)
        chart.setAxisX(chart.axes(Qt.Horizontal)[0], self.vertical_line_series)
        chart.setAxisY(chart.axes(Qt.Vertical)[0], self.vertical_line_series)

    def update_vertical_line(self, x_value):
        min_y = self.chart().axisY().min()
        max_y = self.chart().axisY().max()

        self.vertical_line_series.clear()
        self.vertical_line_series.append(x_value, min_y)
        self.vertical_line_series.append(x_value, max_y)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            x_value = self.chart().mapToValue(event.localPos()).x()
            line_start = self.chart().mapToPosition(self.vertical_line_series.at(0))

            if abs(event.localPos().x() - line_start.x()) < 10:  # 10 pixels tolerance
                self.is_line_dragging = True

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.is_line_dragging:
            x_value = self.chart().mapToValue(event.localPos()).x()
            self.update_vertical_line(x_value)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.is_line_dragging = False

        super().mouseReleaseEvent(event)
app = QApplication([])

chart_view = DraggableVerticalLineChartView()
chart = QChart()

# Add your data series and configure the chart's axes as needed

chart_view.set_chart(chart)

x_value = 5  # Replace this with the initial x-value of the vertical line
chart_view.update_vertical_line(x_value)

chart_view.show()

app.exec()
