from __future__ import annotations
from plot_navigator.plot_navigator import PlotNavigator
from PySide6.QtCharts import QChart, QChartView, QValueAxis, QLineSeries,QScatterSeries
from PySide6.QtGui import QPainter, QMouseEvent,QWheelEvent,QPen,QAction,QCursor
from PySide6.QtCore import Qt,QEvent,QPointF
from PySide6.QtWidgets import QGraphicsEllipseItem,QGraphicsTextItem,QApplication,QMenu,QColorDialog
class SmartChartView(QChartView):

    def __init__(self, chart: QChart,parent=None):
        super().__init__(chart,parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setInteractive(True)
        self.initGraphicsGroup()
        self.initChart()
        self.initOptions()
        self.updateDefaultRange()
        self.plotXY([1,2,3],[3,4,5])

    def initGraphicsGroup(self):
        # add a dictionario to store all series for data
        self.series_dict = {}
        # add a dictionary to store all series for markers
        self.vertical_marker_dict = {}
        # add a dictionary to store all series for mesaurements
        self.measurement_dict = {}

    # initialize the chart
    def initChart(self):
        #add a default series to self.series_dict
        default_series = SmartLineSeries(self,"Default Series")
        self.series_dict[default_series.id] = default_series

        # add some data to default series
        default_series.append(1, 5)
        default_series.append(2, 7)
        default_series.append(3, 6)
        default_series.append(4, 4)
        default_series.append(5, 3)
        default_series.append(6, 4)
        default_series.append(7, 5)

        # set legend
        self.chart().legend().setVisible(True)
        self.chart().legend().setAlignment(Qt.AlignBottom)

        # set title
        self.chart().setTitle("My Chart")

        # set default x y axes and add series
        self.x_axis = QValueAxis()
        self.y_axis = QValueAxis()
        self.addSeriestoXY(default_series, self.x_axis, self.y_axis)

        # set limit of axes
        self.x_axis.setRange(0, 10)
        self.y_axis.setRange(0, 10)

        # set legend text
        default_series.setName(default_series.label)

    # init options of charts
    def initOptions(self):
        self.markerLimitRangeToSeries = False
        self.vlm_selected = None

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

    def updateDefaultRange(self):
        # update the default range of the axes
        self.default_x_range = (self.x_axis.min(), self.x_axis.max())
        self.default_y_range = (self.y_axis.min(), self.y_axis.max())
        self.original_x_range = self.default_x_range
        self.original_y_range = self.default_y_range
    
    def addSeriestoXY(self, series: SmartLineSeries, x_axis: QValueAxis, y_axis: QValueAxis):
        self.chart().addSeries(series)
        self.chart().setAxisX(x_axis, series)
        self.chart().setAxisY(y_axis, series)

    def plotXY(self,x,y,series:SmartLineSeries= None):
        if series == None:
            series = self.addNewSeries()
        self.updateSeries(series,x,y)

    def addNewSeries(self):
        # create a new series
        new_series = SmartLineSeries(self,f"Series {len(self.series_dict)}")
        # add series to self.series_dict
        self.series_dict[new_series.id] = new_series
        # add series to chart
        self.addSeriestoXY(new_series, self.x_axis, self.y_axis)
        return new_series
    
    # remove series from chart and self.series_dict
    def removeSeries(self, series: SmartLineSeries):
        # remove series from chart
        self.chart().removeSeries(series)
        # remove series from self.series_dict
        del self.series_dict[series.id]
        # remove id from SmartLineSeries Class id_pool
        SmartLineSeries.id_pool.remove(series.id)
        # update chart
        self.chart().update()

    # update the series with new (x,y) data
    def updateSeries(self, series:SmartLineSeries, x, y):
        try:
            #clear series
            series.updateSeries(x,y)
            #update chart
            self.chart().update()
        except:
            print("Error: updateSeries()")
            return False
        return True
    
    # update the visibility of all the series with given id in self.series_dict
    # if id is in the list, set visibility to True, else set visibility to False
    def updateSeriesVisibility(self, id_list: list):
        for id in self.series_dict:
            if id in id_list:
                self.series_dict[id].setVisible(True)
            else:
                self.series_dict[id].setVisible(False)
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
            self.updateAllVLM()
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
                self.hideAllVLMCircle()
            chart_point = self.chart().mapToValue(event.position())
            self.last_mouse_pos = chart_point

        elif event.button() == Qt.LeftButton and self.navigator.ui.vertical_marker_button.isChecked():
            chart_point_x = self.chart().mapToValue(event.position()).x()
            #line_start_x = self.vertical_marker_dict[1].at(0).x()
            chosen_VLM = self.findNearestVLM(chart_point_x)
            if chosen_VLM!=None:
                chosen_VLM.is_line_dragging = True
                self.vlm_selected = chosen_VLM

        #if right click on the vertical line marker, popups a menu
        elif event.button() == Qt.RightButton and self.navigator.ui.vertical_marker_button.isChecked():
            chart_point_x = self.chart().mapToValue(event.position()).x()
            chosen_VLM = self.findNearestVLM(chart_point_x)
            if chosen_VLM!=None:
                self.createVLMMenu(chosen_VLM)
    
        super().mousePressEvent(event)
        QApplication.processEvents()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            super().mouseReleaseEvent(event)
            self.last_mouse_pos = None
            if len(self.vertical_marker_dict)!=0:
                if self.vlm_selected != None:
                    self.vlm_selected.is_line_dragging = False
                self.vlm_selected = None

        elif event.button() == Qt.MiddleButton:
            self.last_mouse_pos = None
            if len(self.vertical_marker_dict)!=0:
                if self.vlm_selected != None:
                    self.vlm_selected.is_line_dragging = False
                self.vlm_selected = None

        if self.navigator.ui.vertical_marker_button.isChecked():
            self.updateAllVLM()
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
        elif event.buttons() & Qt.LeftButton and self.navigator.ui.vertical_marker_button.isChecked() and self.vlm_selected!=None:
            self.setRubberBand(QChartView.NoRubberBand)  # make sure no rubber band is shown when moving the vertical line
            chart_point = self.chart().mapToValue(event.position())
            if chart_point.x() >= self.x_axis.min() and chart_point.x() <= self.x_axis.max():
                #self.update_vertical_line(self.vertical_marker_dict[1],chart_point.x())
                self.vlm_selected.updateVLM(chart_point.x())

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

    # create right click popup menu for vertical line marker
    def createVLMMenu(self, vlm: VerticalLineMarker):
        # create a menu
        menu = QMenu(self)
        # create a change color action
        change_color_action = QAction("Change Color", self)
        change_color_action.triggered.connect(lambda: self.changeVLMColor(vlm))
        # create a delete action
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.deleteVerticalLineMarker(vlm))
        
        # add actions to menu
        menu.addAction(delete_action)
        menu.addAction(change_color_action)
        # show menu
        menu.popup(QCursor.pos())

    # find nearst vertical line marker to the given x value
    def findNearestVLM(self, x: float):
        # if there is no vertical line marker nearby with 0.05 tolerance, return None
        if min([abs(vlm.at(0).x() - x) for vlm in self.vertical_marker_dict.values()]) > 0.05:
            return None
        # find the vertical line marker with the minimum distance to the given x value
        nearest_vlm = min(self.vertical_marker_dict.values(), key=lambda vlm: abs(vlm.at(0).x() - x))
        return nearest_vlm
    
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

    def addVerticalLineMarker(self, series:QLineSeries,x_pos: float):
        new_vlm = VerticalLineMarker(self,series,x_pos)
        return new_vlm
    
    # delete the given vertical line marker
    def deleteVerticalLineMarker(self, vlm: VerticalLineMarker):
        # remove the given vertical line marker from the chart
        self.chart().removeSeries(vlm)
        self.chart().scene().removeItem(vlm.vlm_circle)
        # remove the given vertical line marker from the vertical_marker_dict
        del self.vertical_marker_dict[vlm.id]
        # dremove the id of the given vertical line marker from the id_pool
        VerticalLineMarker.id_pool.remove(vlm.id)
        # delete the given vertical line marker
        del vlm
        # if there is no vertical line marker left, uncheck the vertical line marker button
        if len(self.vertical_marker_dict) == 0:
            self.navigator.ui.vertical_marker_button.setChecked(False)

    # change the color of the given vertical line marker
    def changeVLMColor(self, vlm: VerticalLineMarker):
        # open a color dialog
        color = QColorDialog.getColor()
        # if the user clicks OK, change the color of the given vertical line marker
        if color.isValid():
            vlm.setColor(color)
    # update the position of all vertical line marker in self.vertical_marker_dict
    def updateAllVLM(self):
        for vlm in self.vertical_marker_dict.values():
            vlm.updateVLM(vlm.last_vertical_line_x_pos)

    # hide all vertical line markers' circles
    def hideAllVLMCircle(self):
        for vlm in self.vertical_marker_dict.values():
            vlm.vlm_circle.setVisible(False)

    # addP2PMeasure function : measure the distance bwteen two points on the chart
    def addP2PMeasure(self, series: QLineSeries, x_pos1: float, x_pos2: float):
        # create a new P2PMeasure
        new_p2p_measure = P2PMeasure(self, series, x_pos1, x_pos2)
        return new_p2p_measure

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
    


# customize the qlineseries
class SmartLineSeries(QLineSeries):
    count = 0
    id_pool = set()
    #init
    def __init__(self,chart_view:SmartChartView,label:str=""):
        super().__init__()
        self.chart_view = chart_view
        self.label = label
        self.setupID()

    def setupID(self):
        # assign an id and try from 1,2,3,4,5... until an id is not in the id_pool
        id = 1
        while True:
            if id not in SmartLineSeries.id_pool:
                SmartLineSeries.id_pool.add(id)
                break
            id = id + 1
        self.id = id

    # update the series with x,y data given
    def updateSeries(self,x_data:list,y_data:list):
        self.clear()
        for i in range(len(x_data)):
            self.append(x_data[i],y_data[i])
        self.setName(f"My Series {self.label}")

class VerticalLineMarker(QLineSeries):
    count = 0
    id_pool = set()

    def __init__(self, chart_view:SmartChartView,series:QLineSeries,x_value:float,vlm_circle_radius:float=5):
        super().__init__()
        VerticalLineMarker.count += 1
        self.setupID()                                    # set up the id
        self.setName(f"Vertical Line Marker {self.id}")        # set legend of series
        self.setVisible(False)          
        self.chart_view = chart_view
        self.series = series
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

        self.last_vertical_line_x_pos = self.id * (max_x - min_x) / 5 + min_x
        self.last_vertical_line_x_percent = (self.last_vertical_line_x_pos - min_x)/ (max_x-min_x)

        # add graphicstextitem
        self.text_item = QGraphicsTextItem()
        self.chart_view.scene().addItem(self.text_item)

        # add the VLM to the vertical_marker_dict
        self.chart_view.vertical_marker_dict[self.id] = self

    def setupID(self):
        # assign an id and try from 1,2,3,4,5... until an id is not in the id_pool
        id = 1
        while True:
            if id not in VerticalLineMarker.id_pool:
                VerticalLineMarker.id_pool.add(id)
                break
            id = id + 1
        self.id = id

    def showVLM(self):
        self.setVisible(True)
        self.vlm_circle.setVisible(True)
        self.text_item.setVisible(True)

    def updateVLM(self, x_value:float):
        # get min and max of the self.chart().axisY()
        min_y = self.chart_view.chart().axisY().min()
        max_y = self.chart_view.chart().axisY().max()
        min_x = self.chart_view.chart().axisX().min()
        max_x = self.chart_view.chart().axisX().max()

        # get min and max of the self.series.x()
        series_min_x,series_max_x= self._get_min_max_x_values(self.series)

        # limit the x_value to the range of the series if enabled
        if self.chart_view.markerLimitRangeToSeries:
            if x_value < series_min_x:
                x_value = series_min_x
            elif x_value > series_max_x:
                x_value = series_max_x
        
        # update the vertical line series
        self.clear()
        self.append(x_value, min_y)
        self.append(x_value, max_y)
        self.last_vertical_line_x_pos = x_value
        self.last_vertical_line_x_percent = (x_value-min_x) / (max_x-min_x)
        # set the position of the circle to top of the vertical line
        top_point = self.chart_view.chart().mapToPosition(QPointF(x_value,max_y))
        top_point_in_scene = self.chart_view.mapToScene(top_point.toPoint())
        top_point_viewport_position = self.chart_view.mapFromScene(top_point_in_scene)
        self.vlm_circle.setPos(top_point_viewport_position.x()-self.vlm_circle_radius,
                               top_point_viewport_position.y()-self.vlm_circle_radius)
        # show the vertical line marker
        self.showVLM()

        # interpolate y value and show (x,y) in the text item
        y_value = self._interpolate_y_value(self.series,x_value)
        if y_value != None:
            self.text_item.setPlainText(f"({x_value:.2f},{y_value:.2f})")
            text_pos = self.chart().mapToPosition(QPointF(x_value,y_value)) + QPointF(10, -20)  # Adjust the offset as needed
            self.text_item.setPos(text_pos)
        else:
            self.text_item.setPlainText("")
    
    def _get_min_max_x_values(self,series: QLineSeries):
        if not series.points():
            return None, None

        min_x = float("inf")
        max_x = float("-inf")

        for point in series.points():
            min_x = min(min_x, point.x())
            max_x = max(max_x, point.x())

        return min_x, max_x

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

class Measure:
    