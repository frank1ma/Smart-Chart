from plot_navigator.plot_navigator import PlotNavigator
from PySide6.QtCharts import QChart, QChartView, QValueAxis, QLineSeries,QScatterSeries
from PySide6.QtGui import QPainter, QMouseEvent,QWheelEvent
from PySide6.QtCore import Qt,QEvent,QPointF
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QGraphicsEllipseItem,QGraphicsTextItem

class SmartChartView(QChartView):

    def __init__(self, chart: QChart,parent=None):
        super().__init__(chart,parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setInteractive(True)
        self.initChart()
        self.updateDefaultRange()
        self.vertical_line_series = QLineSeries()
        self.chart().addSeries(self.vertical_line_series)
        # add vetical line to axes
        self.chart().setAxisX(self.x_axis, self.vertical_line_series)
        self.chart().setAxisY(self.y_axis, self.vertical_line_series)
        self.update_vertical_line(0)
        self.vertical_line_series.setVisible(False)
    # initialize the chart
    def initChart(self):
        # add a series to the chart
        self.series = QLineSeries()
        self.series.append(0, 6)
        self.series.append(2, 4)
        self.series.append(3, 8)
        self.series.append(7, 4)
        self.series.append(10, 5)
        self.chart().addSeries(self.series)
        # set legend
        self.chart().legend().setVisible(True)
        self.chart().legend().setAlignment(Qt.AlignBottom)
        # set title
        self.chart().setTitle("My Chart")

        # set x y axes
        self.x_axis = QValueAxis()
        self.y_axis = QValueAxis()
        self.chart().setAxisX(self.x_axis, self.series)
        self.chart().setAxisY(self.y_axis, self.series)

        # set limit of axes
        self.x_axis.setRange(0, 10)
        self.y_axis.setRange(0, 10)

        # add graphicstextitem
        self.text_item = QGraphicsTextItem()
        self.scene().addItem(self.text_item)

    def update_vertical_line(self, x_value):
        self.vertical_line_series.setVisible(True)
        min_y = self.chart().axisY().min()
        max_y = self.chart().axisY().max()

        self.vertical_line_series.clear()
        self.vertical_line_series.append(x_value, min_y)
        self.vertical_line_series.append(x_value, max_y)
        # color of the line red
        self.vertical_line_series.setColor(Qt.red)
        y_value = self._interpolate_y_value(self.series,x_value)
        if y_value != None:
            self.text_item.setPlainText(f"({x_value:.2f},{y_value:.2f})")
            text_pos = self.chart().mapToPosition(QPointF(x_value,y_value)) + QPointF(10, -20)  # Adjust the offset as needed
            self.text_item.setPos(text_pos)
        else:
            self.text_item.setPlainText("")
    def updateDefaultRange(self):
        # update the default range of the axes
        self.default_x_range = (self.x_axis.min(), self.x_axis.max())
        self.default_y_range = (self.y_axis.min(), self.y_axis.max())

    # update the series with new (x,y) data
    def updateSeries(self, x, y):
        #clear series
        self.series.clear()
        #add new data
        for i in range(len(x)):
            self.series.append(x[i],y[i])
        #update chart
        self.chart().update()

    # setup navigator
    def setupNavigator(self, navigator: PlotNavigator):
        self.navigator = navigator

    def wheelEvent(self, event: QWheelEvent):
        # zoom in or out using the mouse wheel
        if event.angleDelta().y() > 0:
            self.chart().zoomIn()
        else:
            self.chart().zoomOut()
        QApplication.processEvents()

    def mousePressEvent(self, event: QMouseEvent):
        # pan the chart by left click and drag or middle click and drag
        if ((event.button() == Qt.LeftButton and self.navigator.ui.pan_view_button.isChecked()) or
            event.button()==Qt.MiddleButton):

            chart_point = self.chart().mapToValue(event.position())
            self.setDragMode(QChartView.ScrollHandDrag)
            self.last_mouse_pos = chart_point

        elif event.button() == Qt.LeftButton and self.navigator.ui.vertical_marker_button.isChecked():
            chart_point_x = self.chart().mapToValue(event.position()).x()
            line_start_x = self.vertical_line_series.at(0).x()
            if abs(chart_point_x- line_start_x) < 0.05:  # 10 pixels tolerance
                self.is_line_dragging = True
    
        super().mousePressEvent(event)
        QApplication.processEvents()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton or event.button() == Qt.MiddleButton:
            self.setDragMode(QChartView.RubberBandDrag)
            self.last_mouse_pos = None
            self.is_line_dragging = False
        QApplication.processEvents()

    def mouseMoveEvent(self, event: QMouseEvent):
        # pan the chart if the pan tool is active or the middle mouse button is pressed
        if ((event.buttons() & Qt.LeftButton and self.navigator.ui.pan_view_button.isChecked()) or 
            event.buttons() & Qt.MiddleButton):
            self.panChart(event)
        # if the vertical marker tool is active and the left mouse button is pressed, 
        # update the position of the vertical line
        elif event.buttons() & Qt.LeftButton and self.navigator.ui.vertical_marker_button.isChecked() and self.is_line_dragging:
            chart_point = self.chart().mapToValue(event.position())
            if chart_point.x() >= self.x_axis.min() and chart_point.x() <= self.x_axis.max():
                self.update_vertical_line(chart_point.x())
        # show the current mouse position in the position_label of the navigator, 2 decimal places
        else:
            chart_point = self.chart().mapToValue(event.position())
            self.navigator.ui.position_label.setText(f"({chart_point.x():.2f}, {chart_point.y():.2f})")
            ##reveal the nearest point in the series to the current mouse position
            #self.revealNearestPoint(chart_point)

    # pan the chart by the given event
    def panChart(self, event: QMouseEvent):
        # convert the mouse position to a chart point
        chart_point = self.chart().mapToValue(event.position())
        # pan the chart by the difference between the last mouse position and the current mouse position
        delta = chart_point - self.last_mouse_pos
        # the pan sensitivity is inversely proportional to the zoom level
        zoom_level_x = self.x_axis.max() / self.default_x_range[1]
        zoom_level_y = self.y_axis.max() / self.default_y_range[1]
        # pan the chart
        self.chart().scroll(-10/zoom_level_x*delta.x(), -20/zoom_level_y*delta.y())
        # print the current min and max value of the horizontal axis of the chart
        #print(self.chart().axes(Qt.Horizontal)[0].min(), self.chart().axes(Qt.Horizontal)[0].max())
    # # reveal the nearest point in the series to the current mouse position
    # def revealNearestPoint(self, chart_point):
    #     # find the nearest point in the series to the given chart point
    #     self.point = None
    #     for i, point in enumerate(self.series.points()):
    #             if self._is_point_near(chart_point, point):
    #                 self.selected_point = i
    #                 self.point = point
    #                 break
    #     if self.point!=None:
    #         point_in_chart = self.chart().mapToPosition(self.point)
    #         point_in_scene = self.mapToScene(point_in_chart.toPoint())
    #         viewport_position = self.mapFromScene(point_in_scene)
    #         ellipse = QGraphicsEllipseItem(viewport_position.x()-5, viewport_position.y()-5,2 * 5, 2 * 5)
    #         self.scene().addItem(ellipse)
    #     return  
    
    # def _is_point_near(self, point1, point2):
    #     threshold = 1.0  # You can adjust this value for your needs
    #     return (
    #         abs(point1.x() - point2.x()) <= threshold
    #         and abs(point1.y() - point2.y()) <= threshold
    #     )

    def _interpolate_y_value(self,lineseries:QLineSeries, x_value):
        points = [(p.x(), p.y()) for p in lineseries.pointsVector()]
        if not points:
            return None

        # If x_value is out of range, return the nearest point's y-value
        if x_value <= points[0][0]:
            return None
        if x_value >= points[-1][0]:
            return None

        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]

            if x1 <= x_value <= x2:
                # Linear interpolation
                y_value = y1 + (x_value - x1) * (y2 - y1) / (x2 - x1)
                return y_value

        return None