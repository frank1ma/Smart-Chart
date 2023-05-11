from __future__ import annotations
from plot_navigator.plot_navigator import PlotNavigator
from PySide6.QtCharts import QChart, QChartView, QValueAxis, QLineSeries,QScatterSeries
from PySide6.QtGui import QPainter, QMouseEvent,QWheelEvent,QPen
from PySide6.QtCore import Qt,QEvent,QPointF
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QGraphicsEllipseItem,QGraphicsTextItem,QGraphicsItemGroup

class SmartChartView(QChartView):

    def __init__(self, chart: QChart,parent=None):
        super().__init__(chart,parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setInteractive(True)
        self.initGraphicsGroup()
        self.initChart()
        self.initOptions()
        self.updateDefaultRange()
        #self.initVerticalLineMarker()
        #self.vertical_line_series.setVisible(False)

    def initGraphicsGroup(self):
        # add a dictionario to store all series for data
        self.series_dict = {}
        # add a dictionary to store all series for markers
        self.vertical_marker_dict = {}
        # add a dictionary to store all series for mesaurements
        self.measurement_dict = {}

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

        # set legend text
        self.series.setName("My Series")

    # init options of charts
    def initOptions(self):
        self.markerLimitRangeToSeries = False

    def initVerticalLineMarker(self):
        self.vlm_circle_radius = 5
        self.vlm_circle = QGraphicsEllipseItem(0,0, 2 * self.vlm_circle_radius, 2 * self.vlm_circle_radius)
        self.vertical_line_series = QLineSeries()
        pen = QPen(Qt.red)
        pen.setWidth(3)
        self.vertical_line_series.setPen(pen)
        self.chart().addSeries(self.vertical_line_series)
        self.chart().setAxisX(self.x_axis, self.vertical_line_series)
        self.chart().setAxisY(self.y_axis, self.vertical_line_series)
        self.scene().addItem(self.vlm_circle)
        self.vlm_circle.setVisible(False)
        self.vertical_line_series.setVisible(False)
        # init vertical line marker at x=0
        min_y = self.chart().axisY().min()
        max_y = self.chart().axisY().max()
        self.vertical_line_series.clear()
        self.vertical_line_series.append(0, min_y)
        self.vertical_line_series.append(0, max_y)
        self.last_vertical_line_x_pos = (self.chart().axisX().min() + self.chart().axisX().max())/2
        # set legend of series
        self.vertical_line_series.setName("Vertical Line Marker")

    def update_vertical_line(self, vertical_line_marker:VerticalLineMarker, x_value):
        # get min and max of the self.chart().axisY()
        min_y = self.chart().axisY().min()
        max_y = self.chart().axisY().max()
        min_x = self.chart().axisX().min()
        max_x = self.chart().axisX().max()
        # get min and max of the self.series.x()
        series_min_x,series_max_x= self._get_min_max_x_values(self.series)

        # limit the x_value to the range of the series if enabled
        if self.markerLimitRangeToSeries:
            if x_value < series_min_x:
                x_value = series_min_x
            elif x_value > series_max_x:
                x_value = series_max_x
        
        # update the vertical line series
        vertical_line_marker.clear()
        vertical_line_marker.append(x_value, min_y)
        vertical_line_marker.append(x_value, max_y)
        vertical_line_marker.last_vertical_line_x_pos = x_value
        vertical_line_marker.last_vertical_line_x_percent = (x_value-min_x) / (max_x-min_x)
        # set the position of the circle to top of the vertical line
        top_point = self.chart().mapToPosition(QPointF(x_value,max_y))
        top_point_in_scene = self.mapToScene(top_point.toPoint())
        top_point_viewport_position = self.mapFromScene(top_point_in_scene)
        vertical_line_marker.vlm_circle.setPos(top_point_viewport_position.x()-vertical_line_marker.vlm_circle_radius,
                               top_point_viewport_position.y()-vertical_line_marker.vlm_circle_radius)
        vertical_line_marker.setVisible(True)
        vertical_line_marker.vlm_circle.setVisible(True)

        # interpolate y value and show (x,y) in the text item
        y_value = self._interpolate_y_value(self.series,x_value)
        if y_value != None:
            vertical_line_marker.text_item.setPlainText(f"({x_value:.2f},{y_value:.2f})")
            text_pos = self.chart().mapToPosition(QPointF(x_value,y_value)) + QPointF(10, -20)  # Adjust the offset as needed
            vertical_line_marker.text_item.setPos(text_pos)
        else:
            vertical_line_marker.text_item.setPlainText("")

    def updateDefaultRange(self):
        # update the default range of the axes
        self.default_x_range = (self.x_axis.min(), self.x_axis.max())
        self.default_y_range = (self.y_axis.min(), self.y_axis.max())
        self.original_x_range = self.default_x_range
        self.original_y_range = self.default_y_range

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
        if self.navigator.ui.vertical_marker_button.isChecked():
            self.update_vertical_line(self.vertical_marker_dict[1],self.vertical_marker_dict[1].last_vertical_line_x_pos)
        QApplication.processEvents()

    def mousePressEvent(self, event: QMouseEvent):
        # pan the chart by left click and drag or middle click and drag
        if self.navigator.ui.zoom_button.isChecked():
            self.setRubberBand(QChartView.RectangleRubberBand)
            self.setDragMode(QChartView.NoDrag)
        if ((event.button() == Qt.LeftButton and self.navigator.ui.pan_view_button.isChecked()) or
            event.button()==Qt.MiddleButton):
            self.setDragMode(QChartView.ScrollHandDrag) # override the default rubber band drag mode
            # if dict has a vertical line marker, hide it
            if len(self.vertical_marker_dict)!=0:
                self.vertical_marker_dict[1].vlm_circle.setVisible(False)
            chart_point = self.chart().mapToValue(event.position())
            self.last_mouse_pos = chart_point

        elif event.button() == Qt.LeftButton and self.navigator.ui.vertical_marker_button.isChecked():
            chart_point_x = self.chart().mapToValue(event.position()).x()
            line_start_x = self.vertical_marker_dict[1].at(0).x()
            if line_start_x!=None and abs(chart_point_x - line_start_x) < 0.1: # if the mouse is close to the start of the line
                self.vertical_marker_dict[1].is_line_dragging = True
                self.vlm_selected = 2
        super().mousePressEvent(event)
        QApplication.processEvents()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            super().mouseReleaseEvent(event)
            self.last_mouse_pos = None
            if len(self.vertical_marker_dict)!=0:
                self.vertical_marker_dict[1].is_line_dragging = False
        elif event.button() == Qt.MiddleButton:
            self.last_mouse_pos = None
            if len(self.vertical_marker_dict)!=0:
                self.vertical_marker_dict[1].is_line_dragging  = False
            self.vlm_selected = 0
        if self.navigator.ui.vertical_marker_button.isChecked():
            self.update_vertical_line(self.vertical_marker_dict[1],self.vertical_marker_dict[1].last_vertical_line_x_pos)
        self.setDragMode(QChartView.NoDrag)
        super().mouseReleaseEvent(event)        
        QApplication.processEvents()

    def mouseMoveEvent(self, event: QMouseEvent):
        # pan the chart if the pan tool is active or the middle mouse button is pressed
        if ((event.buttons() & Qt.LeftButton and self.navigator.ui.pan_view_button.isChecked()) or 
            event.buttons() & Qt.MiddleButton):
            self.panChart(event)
        # if the vertical marker tool is active and the left mouse button is pressed, 
        # update the position of the vertical line
        elif event.buttons() & Qt.LeftButton and self.navigator.ui.vertical_marker_button.isChecked() and self.vertical_marker_dict[1].is_line_dragging:
            self.setRubberBand(QChartView.NoRubberBand)  # make sure no rubber band is shown when moving the vertical line
            chart_point = self.chart().mapToValue(event.position())
            if chart_point.x() >= self.x_axis.min() and chart_point.x() <= self.x_axis.max():
                self.update_vertical_line(self.vertical_marker_dict[1],chart_point.x())

        # show the current mouse position in the position_label of the navigator, 2 decimal places
        elif event.buttons() & Qt.LeftButton and self.navigator.ui.zoom_button.isChecked():
            pass

        # show the SizeHorCursor when the mouse is near the vertical line
        elif self.navigator.ui.vertical_marker_button.isChecked():
            chart_point_x = self.chart().mapToValue(event.position()).x()
            line_start_x = self.vertical_marker_dict[1].at(0).x()
            if abs(chart_point_x- line_start_x) < 0.1:  # 10 pixels tolerance
                # set mouse cursor to pan cursor
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)

        # show the current mouse position in the position_label of the navigator, 2 decimal places
        else:
            chart_point = self.chart().mapToValue(event.position())
            self.navigator.ui.position_label.setText(f"({chart_point.x():.2f}, {chart_point.y():.2f})")
        #     ##reveal the nearest point in the series to the current mouse position
        #     #self.revealNearestPoint(chart_point)
        super().mouseMoveEvent(event)  # call the base class method to allow zooming by rubber band
        QApplication.processEvents()

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
    def revealNearestPoint(self, chart_point):
        # find the nearest point in the series to the given chart point
        self.point = None
        for i, point in enumerate(self.series.points()):
                if self._is_point_near(chart_point, point):
                    self.selected_point = i
                    self.point = point
                    break
        if self.point!=None:
            point_in_chart = self.chart().mapToPosition(self.point)
            point_in_scene = self.mapToScene(point_in_chart.toPoint())
            viewport_position = self.mapFromScene(point_in_scene)
            ellipse = QGraphicsEllipseItem(viewport_position.x()-5, viewport_position.y()-5,2 * 5, 2 * 5)
            self.scene().addItem(ellipse)
        return  
    
    def _is_point_near(self, point1, point2):
        threshold = 1.0  # You can adjust this value for your needs
        return (
            abs(point1.x() - point2.x()) <= threshold
            and abs(point1.y() - point2.y()) <= threshold
        )
    
    def addVerticalLineMarker(self, x_pos: float):
        new_vlm = VerticalLineMarker(self,x_pos)
        return new_vlm

    def _interpolate_y_value(self,lineseries:QLineSeries, x_value):
        points = [(p.x(), p.y()) for p in lineseries.pointsVector()]
        if not points:
            return None

        # If x_value is out of range, return the nearest point's y-value
        if x_value < points[0][0]:
            return None
        if x_value > points[-1][0]:
            return None

        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]

            if x1 <= x_value <= x2:
                # Linear interpolation
                y_value = y1 + (x_value - x1) * (y2 - y1) / (x2 - x1)
                return y_value

        return None
    
    def _get_min_max_x_values(self,series: QLineSeries):
        if not series.points():
            return None, None

        min_x = float("inf")
        max_x = float("-inf")

        for point in series.points():
            min_x = min(min_x, point.x())
            max_x = max(max_x, point.x())

        return min_x, max_x
    
class VerticalLineMarker(QLineSeries):
    count = 0
    id_pool = set()

    def __init__(self, chart_view:SmartChartView,x_value:float,vlm_circle_radius:float=5):
        super().__init__()
        VerticalLineMarker.count += 1
        self.setupID()                                         # set up the id
        self.setName(f"Vertical Line Marker {self.id}")        # set legend of series
        self.setVisible(False)                                 # set invisible
        self.chart_view = chart_view
        self.is_line_dragging = False                          # set up the dragging flag
        min_y = self.chart_view.chart().axisY().min()          # Set up the vertical line position
        max_y = self.chart_view.chart().axisY().max()
        self.append(x_value, min_y) 
        self.append(x_value, max_y)

        self.vlm_circle_radius = vlm_circle_radius             # set up the circle radius
        self.vlm_circle = QGraphicsEllipseItem(0,0, 2 * self.vlm_circle_radius, 2 * self.vlm_circle_radius)
        self.chart_view.scene().addItem(self.vlm_circle)       # add the circle to the scene
        self.vlm_circle.setVisible(False)

        pen = QPen(Qt.green)                                   # set up the pen color
        pen.setWidth(3)                                        # set up the pen width
        self.setPen(pen)                                       # set up the pen

        self.chart_view.chart().addSeries(self)                # add the VLM to the chart               
        self.chart_view.chart().setAxisX(self.chart_view.x_axis, self)    # set the x axis of the VLM
        self.chart_view.chart().setAxisY(self.chart_view.y_axis, self)    # set the y axis of the VLM

        # init vertical line marker at middle of the chart
        min_x = self.chart_view.chart().axisX().min()
        max_x = self.chart_view.chart().axisX().max()

        self.last_vertical_line_x_pos = (min_x + max_x)/2
        self.last_vertical_line_x_percent = (self.last_vertical_line_x_pos - min_x)/ (max_x-min_x)
        print(self.last_vertical_line_x_percent)
        # add graphicstextitem
        self.text_item = QGraphicsTextItem()
        self.chart_view.scene().addItem(self.text_item)

        # add the VLM to the vertical_marker_dict
        self.chart_view.vertical_marker_dict[self.id] = self

    def setupID(self):
        # assign an id and try from 1,2,3,4,5... until an id is not in the id_pool
        while True:
            self.id = 1
            if self.id not in VerticalLineMarker.id_pool:
                VerticalLineMarker.id_pool.add(self.id)
                break
            self.id += 1


        