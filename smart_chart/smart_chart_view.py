from __future__ import annotations
from typing import Union
from .plot_navigator.plot_navigator import PlotNavigator
from .plot_navigator.measure import Measure, MeasureMarker, PointMarker, VerticalAuxLineMarker, HorizontalAuxLineMarker
from PySide6.QtCharts import QChart, QChartView, QValueAxis, QLineSeries, QScatterSeries, QLogValueAxis, QAbstractAxis
from PySide6.QtGui import QPainter, QMouseEvent, QWheelEvent, QPen, QAction, QCursor, QFont, QColor
from PySide6.QtCore import Qt, QPointF
from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem, QMenu, QColorDialog, QInputDialog
import math
import sys
import numpy as np
import time


class SmartChartView(QChartView):

    def __init__(self, chart: QChart, parent=None, plot_type="bode_mag"):
        super().__init__(chart, parent)
        self.plot_type = plot_type
        self.setRenderHint(QPainter.Antialiasing)
        self.setInteractive(True)
        self.initOptions()
        self.initGraphicsGroup()
        self.initChart()
        self.updateDefaultRange()
        
    def initGraphicsGroup(self):
        # add a dictionario to store all series for data
        self.series_dict = {}
        # add a dictionary to store all series for markers
        self.vertical_marker_dict = {}
        # add a dictionary to store all series for mesaurements
        self.measure_marker_dict = {}
        # add a dictionary to store all series for auxilary lines
        self.aux_line_dict = {}

        self.active_measure_marker = None
        self.current_measure_type = "p2p"

    # initialize the chart
    def initChart(self):
        # add a default series to self.series_dict
        # default_series = SmartLineSeries(self,"Default Series")
        # self.series_dict[default_series.id] = default_series

        # add 5000 random points to default series
        # for i in range(1,1000):
        #     default_series.addData(np.log10(i),100*math.sin(i))

        # add transfer function to default series
        # sys1 = control.tf([1], [1,2,1])
        # mag,phase,omega = control.bode_plot(sys1,dB=True,deg=True,omega_limits=(0.1,1000),omega_num=500,plot=False)

        # for i in range(len(mag)):
        #     default_series.addData(omega[i],20*np.log10(mag[i]))

        self.chart().legend().setVisible(True)
        self.chart().legend().setAlignment(Qt.AlignBottom)

        # set title
        self.chart().setTitle("My Chart")
        self.chart().setContentsMargins(0, 0, 0, 0)
        self.setAxesProperty()

    # init options of charts
    def initOptions(self):
        self.sub_chart = None
        self.measure_marker_order = []
        self.new_measure_request = False
        self.moving_mm: MeasureMarker = None
        self.moving_measure_marker_text_flag = False
        self.marker_limit_range_to_series = False
        self.vlm_selected = None
        self.point_marker = None
        self.series_select_sensitivity = 1
        self.point_marker_radius = 3
        self.is_point_near_threshold_x = 0.1
        self.is_point_near_threshold_y = 0.1
        self.interpolated_series_step = 0.01
        self.pan_x_sensitivity = 0.05
        self.pan_y_sensitivity = 0.005
        self.zoom_in_level = 1.1
        self.last_highlighted_alm = None
        self.subchart_sync_x_axis = True
        self.subchart_sync_y_axis = True
        self.nichols_grid = None
        self.nichols_grid_text = False
        self.nichols_margin_lines = False
        self.nichols_frequency_data = None
        self.nichols_frequency_series = None
        self.pan_direction = "both"
    
    def updateChartElements(self):
        self.updateSubChart()
        self.updateAuxLineMarker()
        self.updateMarkerText()

    def updateDefaultRange(self):
        # update the default range of the axes
        self.default_x_range = (self.x_axis.min(), self.x_axis.max())
        self.default_y_range = (self.y_axis.min(), self.y_axis.max())
        self.original_x_range = self.default_x_range
        self.original_y_range = self.default_y_range

    def addSeriestoXY(self, series: QLineSeries, x_axis: QAbstractAxis, y_axis: QAbstractAxis, legend_visible=False):
        self.chart().addSeries(series)
        self.chart().setAxisX(x_axis, series)
        self.chart().setAxisY(y_axis, series)
        if not legend_visible:
            self.chart().legend().markers(series)[0].setVisible(False)

    def appendData(self, series: QLineSeries, point_x:float, point_y:float):
        series.append(QPointF(point_x, point_y))
        # find the max y of the series
        max_y = max([point.y() for point in series.pointsVector()])
        # find the min y of the series
        min_y = min([point.y() for point in series.pointsVector()])
        # find the max x of the series
        max_x = max([point.x() for point in series.pointsVector()])
        # find the min x of the series
        min_x = min([point.x() for point in series.pointsVector()])
        # update the range of the axes
        self.x_axis.setRange(min_x, max_x)
        self.y_axis.setRange(min_y, max_y)
        self.updateAuxLineMarker()
        self.updateMarkerText()
        self.chart().update()

    def plotXY(self, x, y, series_type="line", series: SmartLineSeries = None,hold_on=False):
        if not hold_on:
            self.setAxesProperty(x, y)
        if series is None:
            series = self.addNewSeries(series_type)
        self.updateSeries(series, x, y)
        self.updateDefaultRange()

    def addNewSeries(self, series_type: str):
        # create a new series
        if series_type == "line":
            new_series = SmartLineSeries(
                self, f"Series {len(self.series_dict)}")
        elif series_type == "scatter":
            new_series = SmartScatterSeries(
                self, f"Series {len(self.series_dict)}")
        # add series to self.series_dict
        self.series_dict[new_series.id] = new_series
        # add series to chart
        self.addSeriestoXY(new_series, self.x_axis, self.y_axis, True)
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
    def updateSeries(self, series: SmartLineSeries, x, y):
        # clear series
        series.updateSeries(x, y)
        # update chart
        self.chart().update()
        return True

    def addMeasureMarker(self, event: QMouseEvent):
        # create a new measure marker
        if self.active_measure_marker is None:
            self.active_measure_marker = MeasureMarker(self, Measure())
        point_selected = self.chart().mapToValue(event.position())
        finish_flag = self.active_measure_marker.setPoint(point_selected)
        if finish_flag:
            marker = self.active_measure_marker
            if self.current_measure_type == "horizontal":
                marker.drawHorizontalMeasureLine()
            elif self.current_measure_type == "vertical":
                marker.drawVerticalMeasureLine()
            elif self.current_measure_type == "p2p":
                marker.drawPointToPointMeasureLine()
            self.addSeriestoXY(marker, self.x_axis, self.y_axis)
            marker.setVisible(True)
            self.measure_marker_dict[marker.id] = marker
            self.measure_marker_order.append(marker.id)
            self.active_measure_marker = None
            self.current_measure_type = "p2p"
            self.new_measure_request = False

    # update the visibility of all the series with given id in self.series_dict
    # if id is in the list, set visibility to True, else set visibility to False
    def updateSeriesVisibility(self, id_list: list):
        for id in self.series_dict:
            if id in id_list:
                self.series_dict[id].setVisible(True)
            else:
                self.series_dict[id].setVisible(False)
        self.chart().update()

    # update the graphics of auxiliary lines
    def updateAuxLineMarker(self):
        if self.aux_line_dict != {}:
            for alm in self.aux_line_dict.values():
                if alm.aux_line_mode == "normal":
                    alm.redraw()
        self.chart().update()

    # sync the x range of the sub chart with the main chart(self)
    def updateSubChart(self):
        if self.sub_chart is not None:
            if self.subchart_sync_x_axis:
                self.sub_chart.x_axis.setRange(self.x_axis.min(), self.x_axis.max())
                self.sub_chart.chart().update()
            if self.subchart_sync_y_axis:
                y_min_percent = (self.y_axis.min(
                )-self.default_y_range[0])/(self.default_y_range[1]-self.default_y_range[0])
                y_max_percent = (self.y_axis.max(
                )-self.default_y_range[1])/(self.default_y_range[1]-self.default_y_range[0])
                sub_y_range = self.sub_chart.default_y_range[1] - \
                    self.sub_chart.default_y_range[0]
                self.sub_chart.y_axis.setRange(sub_y_range*y_min_percent+self.sub_chart.default_y_range[0],
                                                        sub_y_range*y_max_percent+self.sub_chart.default_y_range[1])
                self.sub_chart.chart().update()
            self.sub_chart.updateAuxLineMarker()
            self.sub_chart.updateMarkerText()
            self.sub_chart.updateAllVLM()

    # setup navigator
    def setupNavigator(self, navigator: PlotNavigator):
        self.navigator = navigator

    def setSubChat(self, sub_chart: SmartChartView):
        self.sub_chart = sub_chart

    def setNicholsFrequencyData(self, frequency_data):
        self.nichols_frequency_series = QLineSeries()
        for index, data in enumerate(frequency_data):
            self.nichols_frequency_series.append(index, data)

    def setDarkMode(self):
        # set the background of chart to dark
        self.chart().setBackgroundBrush(QColor(53, 53, 53))
        # set all the fonts to white
        self.chart().setTitleBrush(QColor(255, 255, 255))
        self.chart().legend().setLabelBrush(QColor(255, 255, 255))
        self.chart().legend().setBrush(QColor(53, 53, 53))
        self.chart().legend().setPen(QColor(255, 255, 255))
        self.x_axis.setLabelsBrush(QColor(255, 255, 255))
        self.x_axis.setTitleBrush(QColor(255, 255, 255))
        self.x_axis.setLinePen(QColor(255, 255, 255))
        self.x_axis.setGridLinePen(QColor(255, 255, 255))
        self.y_axis.setLabelsBrush(QColor(255, 255, 255))
        self.y_axis.setTitleBrush(QColor(255, 255, 255))
        self.y_axis.setLinePen(QColor(255, 255, 255))
        self.y_axis.setGridLinePen(QColor(255, 255, 255))

    def wheelEvent(self, event: QWheelEvent):
        if self.navigator.ui.zoom_button.isChecked():
            # zoom in or out using the mouse wheel
            if event.angleDelta().y() > 0:
                self.chart().zoomIn()
            else:
                self.chart().zoomOut()
            if self.navigator.ui.vertical_marker_button.isChecked():
                self.updateAllVLM()
            if self.navigator.ui.measure_button.isChecked():
                self.updateMarkerText()
            self.updateAuxLineMarker()
            self.updateSubChart()
            self.updateMarkerText()

    def wrapPhase(self, phase: np.ndarray):
        return np.remainder(phase/np.pi*180 + 180, 360) - 180

    def mousePressEvent(self, event: QMouseEvent):
        # pan the chart by left click and drag or middle click and drag
        if self.navigator.ui.zoom_button.isChecked():
            self.setRubberBand(QChartView.RectangleRubberBand)
            self.setDragMode(QChartView.NoDrag)
        if ((event.button() == Qt.LeftButton and self.navigator.ui.pan_view_button.isChecked()) or
                event.button() == Qt.MiddleButton):
            # override the default rubber band drag mode
            self.setDragMode(QChartView.ScrollHandDrag)
            # if dict has a vertical line marker, hide it
            if len(self.vertical_marker_dict) != 0:
                self.hideAllVLMCircle()
            #chart_point = self.chart().mapToValue(event.position())
            chart_point = event.position()
            self.last_mouse_pos = chart_point

        elif event.button() == Qt.LeftButton and self.navigator.ui.vertical_marker_button.isChecked():
            chart_point_x = self.chart().mapToValue(event.position()).x()
            chosen_VLM = self.findNearestVLM(chart_point_x)
            if chosen_VLM is not None:
                chosen_VLM.is_line_dragging = True
                self.vlm_selected = chosen_VLM

        # if left click on the measure button, create a new measure marker
        elif event.button() == Qt.LeftButton and self.navigator.ui.measure_button.isChecked():
            if self.moving_mm is not None:
                self.moving_mm = None
                self.moving_measure_marker_text_flag = False
            else:
                if len(self.measure_marker_dict) < 1 or self.new_measure_request == True:
                    self.addMeasureMarker(event)
                    self.updateMarkerText()

        # if right click on the vertical line marker, popups a menu
        elif event.button() == Qt.RightButton and self.navigator.ui.vertical_marker_button.isChecked():
            chart_point_x = self.chart().mapToValue(event.position()).x()
            chosen_VLM = self.findNearestVLM(chart_point_x)
            if chosen_VLM is not None:
                self.createVLMMenu(chosen_VLM)

        # if right click on the measure marker, popups a menu
        elif event.button() == Qt.RightButton and self.navigator.ui.measure_button.isChecked():
            chart_point = self.chart().mapToValue(event.position())
            chosen_measure_marker = self.findNearestMeasureMarker(chart_point)
            if chosen_measure_marker is not None:
                self.createMeasureMenu(chosen_measure_marker)
            # if right click on the blank area and there is a measure marker whose fisrt point is selected, delete the measure marker
            if self.active_measure_marker is not None and not self.active_measure_marker.checkCompleteStatus():
                self.active_measure_marker.clearPoint()
                self.active_measure_marker = None
                self.current_measure_type = "horizontal"
                self.point_selected = None
                self.new_measure_request = False

        # right click on the blank area and show the add auxiliary line menu
        if event.button() == Qt.RightButton and self.navigator.isVisible():
            # find nearst auxilary line
            chart_point = self.chart().mapToValue(event.position())
            # if chart_point is out of x and y range, return None
            if not (chart_point.x() < self.x_axis.min() or
                    chart_point.x() > self.x_axis.max() or
                    chart_point.y() < self.y_axis.min() or
                    chart_point.y() > self.y_axis.max()):
                chosen_aux_line = self.findNearestAuxiliaryLine(chart_point)
                if chosen_aux_line is not None:
                    self.createAuxLineMenu(chosen_aux_line)
                elif (not self.navigator.ui.measure_button.isChecked() and
                      not self.navigator.ui.vertical_marker_button.isChecked() and
                      not self.navigator.ui.zoom_button.isChecked()):
                    self.createGeneralMenu(chart_point)

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            super().mouseReleaseEvent(event)
            self.last_mouse_pos = None
            if len(self.vertical_marker_dict) != 0:
                if self.vlm_selected is not None:
                    self.vlm_selected.is_line_dragging = False
                self.vlm_selected = None

        elif event.button() == Qt.MiddleButton:
            self.last_mouse_pos = None
            if len(self.vertical_marker_dict) != 0:
                if self.vlm_selected is not None:
                    self.vlm_selected.is_line_dragging = False
                self.vlm_selected = None

        if self.navigator.ui.vertical_marker_button.isChecked():
            self.updateAllVLM()

        self.updateChartElements()
        self.setDragMode(QChartView.NoDrag)
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        # pan the chart if the pan tool is active or the middle mouse button is pressed
        if ((event.buttons() & Qt.LeftButton and self.navigator.ui.pan_view_button.isChecked()) or
                event.buttons() & Qt.MiddleButton):
            self.panChart(event,self.pan_direction)

        # if the vertical marker tool is active and the left mouse button is pressed,
        # update the position of the vertical line
        elif event.buttons() & Qt.LeftButton and self.navigator.ui.vertical_marker_button.isChecked() and self.vlm_selected is not None:
            # make sure no rubber band is shown when moving the vertical line
            self.setRubberBand(QChartView.NoRubberBand)
            chart_point = self.chart().mapToValue(event.position())
            if chart_point.x() >= self.x_axis.min() and chart_point.x() <= self.x_axis.max():
                self.vlm_selected.updateVLM(chart_point.x())
                if self.vlm_selected.extended_vlm is not None:
                    self.vlm_selected.extended_vlm.updateVLM(chart_point.x())

        # show the current mouse position in the position_label of the navigator, 2 decimal places
        elif event.buttons() & Qt.LeftButton and self.navigator.ui.zoom_button.isChecked():
            pass

        # show the SizeHorCursor when the mouse is near the vertical line
        elif self.navigator.ui.vertical_marker_button.isChecked():
            chart_point_x = self.chart().mapToValue(event.position()).x()
            chosen_VLM = self.findNearestVLM(chart_point_x)
            if chosen_VLM is not None:
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)

        # show the current mouse position in the position_label of the navigator, 2 decimal places
        else:
            chart_point = self.chart().mapToValue(event.position())
            self.navigator.ui.position_label.setText(
                f"({chart_point.x():.2f}, {chart_point.y():.2f})")
        #     ##reveal the nearest point in the series to the current mouse position
        #     #self.revealNearestPoint(chart_point)
        nearest_alm: Union[VerticalAuxLineMarker, HorizontalAuxLineMarker] = self.findNearestAuxiliaryLine(
            self.chart().mapToValue(event.position()))
        if nearest_alm is not None:
            # highlight the nearest auxiliary line
            self.last_highlighted_alm = nearest_alm
            nearest_alm.highlightOn(2)
            nearest_alm.redraw()
            self.chart().update()
        else:
            if self.last_highlighted_alm is not None and self.last_highlighted_alm:
                self.last_highlighted_alm.highlightOff()
                self.last_highlighted_alm.redraw()
                self.chart().update()

        if self.measure_marker_dict != {} and self.moving_measure_marker_text_flag == True:
            chart_point = self.chart().mapToValue(event.position())
            if self.moving_mm is not None:
                pos = self.moving_mm._convertPointFromChartViewtoViewPort(chart_point)
                try:
                    self.moving_mm.text_item.setPos(pos)
                    self.chart().update()
                except:
                    print("text position error")

        if self.nichols_grid is not None and self.nichols_grid_text:
            chart_point = self.chart().mapToValue(event.position())
            nearest_mc, dB_label = self.findNearestMCircle(chart_point)
            nearest_nc, deg_label = self.findNearestNCircle(chart_point)
            if nearest_mc is not None and nearest_nc is not None:
                self.navigator.showLabelMsg(
                    f"{dB_label:g} dB, {deg_label:g} deg", time=5000)
            elif nearest_mc is not None:
                self.navigator.showLabelMsg(f"{dB_label:g} dB", time=5000)
            elif nearest_nc is not None:
                self.navigator.showLabelMsg(f"{deg_label:g} deg", time=5000)

        # call the base class method to allow zooming by rubber band
        super().mouseMoveEvent(event)

    def clearAllIntersectionPoint(self, alm: Union[VerticalAuxLineMarker, HorizontalAuxLineMarker]):
        alm.deletePointMarkers()
        alm.redraw()
        self.chart().update()

    # create right click popup menu for vertical line marker
    def createVLMMenu(self, vlm: VerticalLineMarker):
        # create a menu
        menu = QMenu(self)
        # create a change position action
        change_position_action = QAction("Change Position", self)
        change_position_action.triggered.connect(
            lambda: self.changeVLMPosition(vlm))
        # create a change width action
        change_width_action = QAction("Change Width", self)
        change_width_action.triggered.connect(lambda: self.changeVLMWidth(vlm))
        # create a change color action
        change_color_action = QAction("Change Color", self)
        change_color_action.triggered.connect(lambda: self.changeVLMColor(vlm))
        # extend the line to the top and bottom of the chart
        extend_line_action = QAction("Extend Line to Subchart", self)
        extend_line_action.triggered.connect(
            lambda: self.extendVLMToSubchart(vlm))
        # cancel the extension of the line
        cancel_extend_line_action = QAction("Cancel Extension", self)
        cancel_extend_line_action.triggered.connect(
            lambda: self.cancelVLMExtension(vlm))
        # create a delete action
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(
            lambda: self.deleteVerticalLineMarker(vlm))

        # add actions to menu
        menu.addAction(change_position_action)
        menu.addAction(change_width_action)
        menu.addAction(change_color_action)
        if vlm.extended:
            menu.addAction(cancel_extend_line_action)
        else:
            menu.addAction(extend_line_action)
        menu.addAction(delete_action)
        # show menu
        menu.popup(QCursor.pos())

    # create right click popup menu for measure marker
    def createMeasureMenu(self, mm: MeasureMarker):
        # create a menu
        menu = QMenu(self)
        # create change measure type action
        change_type_action = QAction("Change Measure Type", self)
        # create submenu for measure type: Horizontal,Vertical,Point-to-Point
        measure_type_menu = QMenu("Measure Type", self)
        # create menu action to text position of measure marker's item text
        text_position_action = QAction("Change Measure Text Position", self)
        text_position_action.triggered.connect(
            lambda: self.changeMeasureTextPosition(mm))
        # create menu action to lock the position of measure marker's item text
        lock_text_position_action = QAction("Lock Measure Text Position", self)
        lock_text_position_action.triggered.connect(
            lambda: self.lockMeasureTextPosition(mm))
        # checkable action
        lock_text_position_action.setCheckable(True)
        if mm.text_pos_lock:
            lock_text_position_action.setChecked(True)
        else:
            lock_text_position_action.setChecked(False)
        # create actions for measure type
        horizontal_action = QAction("Horizontal", self)
        horizontal_action.triggered.connect(
            lambda: self.changeMeasureType(mm, "horizontal"))
        vertical_action = QAction("Vertical", self)
        vertical_action.triggered.connect(
            lambda: self.changeMeasureType(mm, "vertical"))
        point_to_point_action = QAction("Point-to-Point", self)
        point_to_point_action.triggered.connect(
            lambda: self.changeMeasureType(mm, "p2p"))
        # add actions to measure type menu
        measure_type_menu.addAction(horizontal_action)
        measure_type_menu.addAction(vertical_action)
        measure_type_menu.addAction(point_to_point_action)
        # add measure type menu to change type action
        change_type_action.setMenu(measure_type_menu)
        # create a change color action
        change_color_action = QAction("Change Color", self)
        change_color_action.triggered.connect(
            lambda: self.changeMeasureColor(mm))
        # create a delete action
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.deleteMeasureMarker(mm))

        # add actions to menu
        menu.addAction(change_type_action)
        menu.addAction(text_position_action)
        menu.addAction(lock_text_position_action)
        menu.addAction(change_color_action)
        menu.addAction(delete_action)
        # show menu
        menu.popup(QCursor.pos())

    # create auxiliary vertical line marker
    def createAuxLineMenu(self, alm: Union[VerticalAuxLineMarker, HorizontalAuxLineMarker]):
        # create a menu
        menu = QMenu(self)
        # create a show point position action
        show_point_position_action = QAction("Show Intersection Point", self)
        # show_point_position_action.triggered.connect(lambda: self.showIntersectionPoint(alm))
        # create a change position action
        change_position_action = QAction("Change Position", self)
        change_position_action.triggered.connect(
            lambda: self.changeAuxLinePosition(alm))
        # create a change color action
        change_color_action = QAction("Change Color", self)
        change_color_action.triggered.connect(
            lambda: self.changeAuxLineColor(alm))
        # create a delete action
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(
            lambda: self.deleteAuxiliaryLineMarker(alm))

        # create sub menu for show_point_position_action
        show_point_position_menu = QMenu("Show Intersection Point", self)
        # create actions for show_point_position_action
        show_next_intersection_point_action = QAction(
            "Show Next Intersection Point", self)
        show_next_intersection_point_action.triggered.connect(
            lambda: self.showIntersectionPoint(alm, "next"))
        show_all_intersection_point_action = QAction(
            "Show All Intersection Point", self)
        show_all_intersection_point_action.triggered.connect(
            lambda: self.showIntersectionPoint(alm, "all"))
        select_intersection_point_action = QAction(
            "Select Intersection Point", self)
        select_intersection_point_action.triggered.connect(
            lambda: self.selectIntersectionPoint(alm))
        clear_all_intersection_point_action = QAction(
            "Clear All Intersection Point", self)
        clear_all_intersection_point_action.triggered.connect(
            lambda: self.clearAllIntersectionPoint(alm))
        # add actions to show_point_position_menu
        show_point_position_menu.addAction(show_next_intersection_point_action)
        show_point_position_menu.addAction(show_all_intersection_point_action)
        show_point_position_menu.addAction(select_intersection_point_action)
        show_point_position_menu.addAction(clear_all_intersection_point_action)
        # add show_point_position_menu to show_point_position_action
        show_point_position_action.setMenu(show_point_position_menu)
        # add actions to menu
        menu.addAction(show_point_position_action)
        menu.addAction(change_position_action)
        menu.addAction(change_color_action)
        menu.addAction(delete_action)
        # show menu
        menu.popup(QCursor.pos())

    # create popup menu for adding the auxiliary line marker at the blank area
    def createGeneralMenu(self, pos: QPointF):
        # create a menu
        menu = QMenu(self)
        # create a add vertical auxiliary line marker action
        add_vertical_action = QAction(
            "Add Vertical Auxiliary Line Marker", self)
        add_vertical_action.triggered.connect(
            lambda: self.addAuxiliaryLineMarker("vertical", pos.x()))
        # create a add horizontal auxiliary line marker action
        add_horizontal_action = QAction(
            "Add Horizontal Auxiliary Line Marker", self)
        add_horizontal_action.triggered.connect(
            lambda: self.addAuxiliaryLineMarker("horizontal", pos.y()))

        # if self.plot_type == "nichols", create a add turn on/off nichols grid action
        if self.plot_type == "nichols":
            if self.nichols_grid is None:
                add_nichols_grid_action = QAction("Turn on Nichols Grid", self)
                add_nichols_grid_action.triggered.connect(
                    lambda: self.showNicholsGrid())
                menu.addAction(add_nichols_grid_action)
            else:
                remove_nichols_grid_action = QAction(
                    "Turn off Nichols Grid", self)
                remove_nichols_grid_action.triggered.connect(
                    lambda: self.showNicholsGrid())
                menu.addAction(remove_nichols_grid_action)
                # add actions to turn off the M N circle's text
                if self.nichols_grid_text:
                    remove_nichols_grid_text_action = QAction(
                        "Turn off Nichols Grid Text", self)
                    remove_nichols_grid_text_action.triggered.connect(
                        self.nichols_grid.hideText)
                    menu.addAction(remove_nichols_grid_text_action)
                else:
                    add_nichols_grid_text_action = QAction(
                        "Turn on Nichols Grid Text", self)
                    add_nichols_grid_text_action.triggered.connect(
                        self.nichols_grid.showText)
                    menu.addAction(add_nichols_grid_text_action)

                alm_h_exist, alm_v_exist = self._checkNicholsMarginLine()

                if (self.nichols_margin_lines) and (alm_h_exist or alm_v_exist):
                    remove_nichols_margin_lines_action = QAction(
                        "Turn off Stability Margin Lines", self)
                    remove_nichols_margin_lines_action.triggered.connect(
                        self.hideNicholsMargin)
                    menu.addAction(remove_nichols_margin_lines_action)
                else:
                    add_nichols_margin_lines_action = QAction(
                        "Turn on Stability Margin Lines", self)
                    add_nichols_margin_lines_action.triggered.connect(
                        self.showNicholsMargin)
                    menu.addAction(add_nichols_margin_lines_action)
        # add actions to menu
        menu.addAction(add_vertical_action)
        menu.addAction(add_horizontal_action)
        # show menu
        menu.popup(QCursor.pos())

    # calculate the cartisian distance between two points
    def calculateDistance(self, p1: QPointF, p2: QPointF):
        return math.sqrt((p1.x() - p2.x())**2 + (p1.y() - p2.y())**2)

    # calculate the gain margin of given the frequency as freq and magnitude as mag, and phase as phase
    def calculateGainMargin(self, freq: list, mag: list, phase: list, dB: bool = True):
        # check if -180 is in between any two points in phase list
        for i in range(len(phase)-1):
            if (phase[i] < -180 and phase[i+1] > -180) or (phase[i] > -180 and phase[i+1] < -180):
                # interpolate the phase value at phase = -180
                freq_at_neg_180 = (-180-phase[i]) * (freq[i+1] -
                                                     freq[i]) / (phase[i+1] - phase[i]) + freq[i]
                # calculate the mag at the same index with interpolated
                mag_at_neg_180 = (
                    mag[i+1] - mag[i]) / (freq[i+1] - freq[i]) * (freq_at_neg_180 - freq[i]) + mag[i]
                # calculate the gain margin
                if dB:
                    gain_margin = 0 - mag_at_neg_180
                else:
                    gain_margin = 1 / mag_at_neg_180
                return gain_margin, freq_at_neg_180
        print("Error no gain margin found!")
        return None, None

    def calculatePhaseMargin(self, freq: list, mag: list, phase: list, dB: bool = True):
        for i in range(len(mag)-1):
            if (mag[i] < 0 and mag[i+1] > 0) or (mag[i] > 0 and mag[i+1] < 0):
                # interpolate the phase value at phase = -180
                freq_at_0dB = (-mag[i]) * (freq[i+1] - freq[i]
                                           ) / (mag[i+1] - mag[i]) + freq[i]
                # calculate the mag at the same index with interpolated
                phase_at_0dB = (phase[i+1] - phase[i]) / (freq[i+1] -
                                                          freq[i]) * (freq_at_0dB - freq[i]) + phase[i]
                # calculate the gain margin
                phase_margin = phase_at_0dB + 180
                # print("the gain margin is ",gain_margin)
                return phase_margin, freq_at_0dB
        print("Error no phase margin found!")
        return None

    # find nearst vertical line marker to the given x value
    def findNearestVLM(self, x: float):
        min_dis = min([abs(vlm.at(0).x() - x)/(x+0.01)
                      for vlm in self.vertical_marker_dict.values()])
        # if there is no vertical line marker nearby with 0.05 tolerance, return None
        if abs(min_dis) > 0.05:
            return None
        # find the vertical line marker with the minimum distance to the given x value
        nearest_vlm = min(self.vertical_marker_dict.values(),
                          key=lambda vlm: abs(vlm.at(0).x() - x)/(x+0.01))
        return nearest_vlm

    # find nearst measure marker to the given point value
    def findNearestMeasureMarker(self, point: QPointF):
        # if the point is on any measure marker, return True
        min_dis = 100
        nearst_mm = None
        for mm in self.measure_marker_dict.values():
            p1 = mm.at(0)
            p2 = mm.at(1)
            # if p1 p2 form a vertical line
            if p1.x() == p2.x():
                # if the point's y value is not between p1 and p2, the dis is the distance between the point and point that close to the point on the line between p1 and p2
                if not (p1.y() <= point.y() <= p2.y() or p2.y() <= point.y() <= p1.y()):
                    # return the point that is closer to point
                    if self.calculateDistance(point, p1) <= self.calculateDistance(point, p2):
                        close_point = p1
                    else:
                        close_point = p2
                    dis = self.calculateDistance(point, close_point)
                    dis1 = abs(point.x() - close_point.x())
                    dis2 = abs(point.y() - close_point.y())
                    if (dis1 < 0.05*(self.x_axis.max() - self.x_axis.min()) and dis2 < 0.05*(self.y_axis.max() - self.y_axis.min())
                            and dis < min_dis):
                        nearst_mm = mm
                        min_dis = dis
                else:
                    # if the point's y value is between p1 and p2, the dis is the distance between the point and the vertical line
                    dis = abs(point.x() - p1.x())
                    if dis < 0.05*(self.x_axis.max() - self.x_axis.min()) and dis < min_dis:
                        nearst_mm = mm
                        min_dis = dis
            # if p1 p2 form a horizontal line
            elif p1.y() == p2.y():
                # if the point's x value is not between p1 and p2, the dis is the distance between the point and point that close to the point on the line between p1 and p2
                if not (p1.x() <= point.x() <= p2.x() or p2.x() <= point.x() <= p1.x()):
                    # return the point that is closer to point
                    if self.calculateDistance(point, p1) <= self.calculateDistance(point, p2):
                        close_point = p1
                    else:
                        close_point = p2
                    dis = self.calculateDistance(point, close_point)
                    dis1 = abs(point.x() - close_point.x())
                    dis2 = abs(point.y() - close_point.y())
                    if (dis1 < 0.05*(self.x_axis.max() - self.x_axis.min()) and dis2 < 0.05*(self.y_axis.max() - self.y_axis.min())
                            and dis < min_dis):
                        nearst_mm = mm
                        min_dis = dis
                else:
                    # if the point is on the horizontal line, return True
                    dis = abs(point.y() - p1.y())
                    if dis < 0.05*(self.y_axis.max() - self.y_axis.min()) and dis < min_dis:
                        nearst_mm = mm
                        min_dis = dis
            # if p1 p2 form a oblique line
            else:
                # find the y value of the point on line between p1 and p2 with x value of point.x()
                y = (p2.y() - p1.y()) / (p2.x() - p1.x()) * \
                    (point.x() - p1.x()) + p1.y()
                # find the x value of the point on line between p1 and p2 with y value of point.y
                x = (p2.x() - p1.x()) / (p2.y() - p1.y()) * \
                    (point.y() - p1.y()) + p1.x()
                if (abs(y-point.y()) < 0.05*(self.y_axis.max() - self.y_axis.min()) and
                        abs(x-point.x()) < 0.05*(self.x_axis.max() - self.x_axis.min()) and
                        math.sqrt((y-point.y())**2+(x-point.x())**2) < min_dis):
                    nearst_mm = mm
                    min_dis = math.sqrt((y-point.y())**2+(x-point.x())**2)

        if nearst_mm is not None:
            return nearst_mm
        else:
            return None
    # find nearst auxiliary line to the given point value

    def findNearestAuxiliaryLine(self, point: QPointF):
        """
        find nearst auxiliary line to the given point value.
        The distance is calculated by the relative distance between the point and the auxiliary line, which is in percentage.
        The threshold is 5%, which means if the distance is less than 5%, the point is considered to be on the auxiliary line.
        """
        # if the point is on any auxiliary line, return True
        min_dis = 100000
        nearst_al = None
        for al in self.aux_line_dict.values():
            if al.__class__.__name__ == "HorizontalAuxLineMarker" and al.aux_line_mode != "measure":
                if al.points()[0].y() == 0:
                    al_min_dis = abs(al.points()[0].y() - point.y())
                else:
                    # al_min_dis = abs(al.points()[0].y() - point.y())/abs(al.points()[0].y())4
                    if self.y_axis.type() == QAbstractAxis.AxisType.AxisTypeValue and self.plot_type == "bode_mag":
                        if al.points()[0].y() - point.y() == 0:
                            al_min_dis = 0
                        else:
                            al_min_dis = 20 * \
                                np.log(
                                    abs(al.points()[0].y() - point.y()))/abs(self.y_axis.max() - self.y_axis.min())
                    elif self.y_axis.type() == QAbstractAxis.AxisType.AxisTypeValue and self.plot_type == "bode_phase":
                        al_min_dis = abs(
                            al.points()[0].y() - point.y())/abs(self.y_axis.max() - self.y_axis.min())
                    elif self.y_axis.type() == QAbstractAxis.AxisType.AxisTypeLogValue:
                        al_min_dis = np.log(abs(al.points()[0].y(
                        ) - point.y()))/abs(np.log(self.y_axis.max() / self.y_axis.min()))
                    else:
                        al_min_dis = abs(
                            al.points()[0].y() - point.y())/abs(self.y_axis.max() - self.y_axis.min())

                if min_dis > al_min_dis:
                    min_dis = al_min_dis
                    nearst_al = al
            if al.__class__.__name__ == "VerticalAuxLineMarker" and al.aux_line_mode != "measure":
                if al.points()[0].x() == 0:
                    al_min_dis = abs(al.points()[0].x() - point.x())
                else:
                    # al_min_dis = abs(al.points()[0].x() - point.x())/abs(al.points()[0].x())
                    if self.x_axis.type() == QAbstractAxis.AxisType.AxisTypeValue:
                        al_min_dis = abs(
                            al.points()[0].x() - point.x())/abs(self.x_axis.max() - self.x_axis.min())
                    elif self.x_axis.type() == QAbstractAxis.AxisType.AxisTypeLogValue:
                        if abs(al.points()[0].x() - point.x()) == 0:
                            al_min_dis = 0
                        else:
                            al_min_dis = np.log(
                            abs(al.points()[0].x() - point.x()))/np.log(self.x_axis.max() / self.x_axis.min())
                if min_dis > al_min_dis:
                    min_dis = al_min_dis
                    nearst_al = al

        if nearst_al is None:
            return None
        if nearst_al.__class__.__name__ == "HorizontalAuxLineMarker" and nearst_al.aux_line_mode != "measure" and nearst_al.points()[0].y() == 0:
            threshold = 0.08 * (self.y_axis.max() - self.y_axis.min())
        elif nearst_al.__class__.__name__ == "VerticalAuxLineMarker" and nearst_al.aux_line_mode != "measure" and nearst_al.points()[0].x() == 0:
            threshold = 0.08 * (self.x_axis.max() - self.x_axis.min())
        else:
            threshold = 0.08
        # print("threshold:",threshold,"min_dis:",min_dis,"nearst_al:",nearst_al)
        if min_dis <= threshold:  # self.auxiliaryLinethreshold:
            return nearst_al
        else:
            return None

    # pan the chart by the given event
    def panChart(self, event: QMouseEvent,direction:str="both"):

        #chart_point = self.chart().mapToValue(event.position())
        chart_point = event.position()
        # pan the chart by the difference between the last mouse position and the current mouse position
        try:
            delta = chart_point - self.last_mouse_pos
        except:
            print("wrong point for pan")
            return
        # # the pan sensitivity is inversely proportional to the zoom level
        # if self.default_x_range[1] == 0:
        #     zoom_level_x = 1
        # else:
        #     zoom_level_x = abs(self.x_axis.max()) / \
        #         abs(self.default_x_range[1])
        # if self.default_y_range[1] == 0:
        #     zoom_level_y = 1
        # else:
        #     zoom_level_y = abs(self.y_axis.max()) / \
        #         abs(self.default_y_range[1])
        zoom_level_x = 1
        zoom_level_y = 1
        # pan the chart
        if direction == "both":
            self.chart().scroll(-self.pan_x_sensitivity/(zoom_level_x) *
                                delta.x(), self.pan_y_sensitivity/(zoom_level_y)*delta.y())
        elif direction == "x":
            self.chart().scroll(-self.pan_x_sensitivity/(zoom_level_x) *delta.x(), 0)
            #self.chart().scroll(-self.pan_x_sensitivity * delta.x(), 0)
        elif direction == "y":
            self.chart().scroll(0, self.pan_y_sensitivity/(zoom_level_y)*delta.y())
        self.updateSubChart()
        self.updateMarkerText()
        self.updateAuxLineMarker()
    def updateMarkerText(self):
        # pan all the text item together with the chart
        for mm in self.measure_marker_dict.values():
            viewport_text_pos = mm._convertPointFromChartViewtoViewPort(QPointF(mm.measure_line.center().x(),
                                                                                mm.measure_line.center().y()))
            viewport_point1_pos = mm.point1_marker._convertPointFromChartViewtoViewPort(QPointF(mm.point1_marker.x_value,
                                                                                                mm.point1_marker.y_value))
            viewport_point2_pos = mm.point2_marker._convertPointFromChartViewtoViewPort(QPointF(mm.point2_marker.x_value,
                                                                                                mm.point2_marker.y_value))
            if not mm.text_pos_lock:
                mm.text_item.setPos(viewport_text_pos)
            mm.point1_marker.point_coordinate_label.setPos(viewport_point1_pos)
            mm.point2_marker.point_coordinate_label.setPos(viewport_point2_pos)

        # pan all the point coordinate label together with the auxiliary line marker
        for alm in self.aux_line_dict.values():
            if alm.aux_line_mode == "measure":
                continue
            for point_marker in alm.point_marker.values():
                point_marker_viewport_text_pos = point_marker._convertPointFromChartViewtoViewPort(QPointF(point_marker.x_value,
                                                                                                           point_marker.y_value))
                point_marker.point_coordinate_label.setPos(
                    point_marker_viewport_text_pos)

    def addVerticalLineMarker(self, series: QLineSeries, x_pos: float):
        new_vlm = VerticalLineMarker(self, series, x_pos)
        return new_vlm

    def addMCircles(self, m: float):
        center = QPointF(-m**2/(m**2-1), 0)
        radius = np.sqrt(m**2/(m**2-1)**2)
        angle_array = []
        mag_array = []
        # create a circle data series
        iter_array = np.concatenate(
            (np.arange(0, 10, .1), np.arange(10, 350, 1), np.arange(350, 360, 0.1)))
        for i in iter_array:
            x = center.x() + radius * math.cos(math.radians(i))
            y = center.y() + radius * math.sin(math.radians(i))
            mag = np.abs(x+y*1j)
            angle = np.angle(x+y*1j, deg=True)
            angle_array.append(angle)
            mag_array.append(mag)
        angle_array = np.unwrap(angle_array, period=360, discont=180)
        centers = self.findMCircleCenter()
        for center in centers:
            new_series = QLineSeries()
            new_series.setPen(
                QPen(Qt.GlobalColor.gray, 1, Qt.PenStyle.DashLine))
            angle_arr = self.adjustNicholsPhase(center, angle_array)
            for angle, mag in zip(angle_arr, mag_array):
                new_series.append(angle, 20*np.log10(mag))
            self.chart().addSeries(new_series)
            self.chart().setAxisX(self.x_axis, new_series)
            self.chart().setAxisY(self.y_axis, new_series)

    def getNCircles(self, alpha: float):
        # phase_array = [10,20,30,40,60,80,120,-120,-80,-60,-40,-30,-20,-10]
        N = np.tan(alpha/180*np.pi)
        center = QPointF(-1/2, 1/(2*N))
        radius = np.sqrt(1/4+(1/(2*N))**2)
        angle_array = []
        mag_array = []
        iter_array = np.concatenate(
            (np.arange(0, 10, .1), np.arange(10, 350, 1), np.arange(350, 360.1, 0.1)))
        for i in iter_array:
            if i == 270:
                continue
            x = center.x() + radius * math.cos(math.radians(i))
            y = center.y() + radius * math.sin(math.radians(i))
            mag = np.abs(x+y*1j)
            angle = np.angle(x+y*1j, deg=True)
            if mag == 0 and angle == 0:
                continue
            if 20*np.log10(mag) < -40:
                continue
            angle_array.append(angle)
            mag_array.append(mag)
        angle_array = list(np.unwrap(angle_array, period=360, discont=180))
        angle_array.append(min(angle_array)-0.1)
        mag_array.append(10**(-1000/20))
        angle_array.append(max(angle_array)+0.1)
        mag_array.append(10**(-1000/20))
        centers = self.findMCircleCenter()
        for center in centers:
            new_series = QLineSeries()
            angle_arr = self.adjustNicholsPhase(center, np.array(angle_array))
            for angle, mag in zip(angle_arr, mag_array):
                new_series.append(angle, 20*np.log10(mag))
            points = new_series.points()
            points.sort(key=lambda point: (point.x(), point.y()))
            new_series = QLineSeries()
            new_series.setPen(
                QPen(Qt.GlobalColor.gray, 1, Qt.PenStyle.DashLine))
            for point in points:
                new_series.append(point)
            self.chart().addSeries(new_series)
            self.chart().setAxisX(self.x_axis, new_series)
            self.chart().setAxisY(self.y_axis, new_series)

    def findMCircleCenter(self):
        # determine if -180,180,180+360,-180-360 is in the current x range
        center = []
        for multiple in range(-10, 11):
            if -180 + multiple * 360 >= self.x_axis.min() and -180 + multiple * 360 <= self.x_axis.max():
                center.append(-180 + multiple * 360)
        center.append(min(center)-360)
        center.append(max(center)+360)
        return center

    def findNearestMCircle(self, point: QPointF):
        if self.nichols_grid is None:
            return None
        min_dis = 100000
        nearst_mc = None
        for mc in self.nichols_grid.m_circles_series_list:
            # find the minimum distance between the point and the point on the circle
            min = 100000
            for mc_point in mc.points():
                if self.calculateDistance(point, mc_point) < min:
                    min = self.calculateDistance(point, mc_point)
            if min < min_dis:
                min_dis = min
                nearst_mc = mc

        # return the index of nearst_mc in the m_circles_series_list
        index = self.nichols_grid.m_circles_series_list.index(nearst_mc)

        if min_dis < 0.08*(self.x_axis.max() - self.x_axis.min()):
            num_of_mag = len(self.nichols_grid.m_circle_magnitude)
            db_label = 20 * \
                np.log10(
                    self.nichols_grid.m_circles_list[index % num_of_mag].magnitude)
            return nearst_mc, db_label

        return None, None
        self.navigator.showLabelMsg(f"{db_label:g} dB")

    def findNearestNCircle(self, point: QPointF):
        if self.nichols_grid is None:
            return None
        min_dis = 100000
        nearst_nc = None
        for nc in self.nichols_grid.n_circles_series_list:
            # find the minimum distance between the point and the point on the circle
            min = 100000
            for nc_point in nc.points():
                if self.calculateDistance(point, nc_point) < min:
                    min = self.calculateDistance(point, nc_point)
            if min < min_dis:
                min_dis = min
                nearst_nc = nc

        # return the index of nearst_mc in the m_circles_series_list
        index = self.nichols_grid.n_circles_series_list.index(nearst_nc)

        if min_dis < 0.08*(self.x_axis.max() - self.x_axis.min()):
            num_of_phase = len(self.nichols_grid.n_circle_phase)
            phase_label = self.nichols_grid.n_circles_list[index %
                                                           num_of_phase].phase
            return nearst_nc, phase_label
        return None, None

    def adjustNicholsPhase(self, center, phase_array: np.ndarray):
        # adjust the phase array by adding 360 or minusing 360 to make sure the center is in the array
        min_phase = min(phase_array)
        max_phase = max(phase_array)
        while min_phase - center >= 180:
            phase_array -= 360
            min_phase = min(phase_array)
        while max_phase - center <= -180:
            phase_array += 360
            max_phase = max(phase_array)
        # for i in range(len(phase_array)):
        #     while phase_array[i] - center > 180:
        #         phase_array[i] -= 360
        #     while phase_array[i] - center < -180:
        #         phase_array[i] += 360
        return phase_array

    # delete the given vertical line marker
    def deleteVerticalLineMarker(self, vlm: VerticalLineMarker):
        # remove the given vertical line marker from the chart
        self.chart().removeSeries(vlm)
        self.chart().scene().removeItem(vlm.vlm_circle)
        self.chart().scene().removeItem(vlm.text_item)
        # remove the given vertical line marker from the vertical_marker_dict
        del self.vertical_marker_dict[vlm.id]
        # dremove the id of the given vertical line marker from the id_pool
        VerticalLineMarker.id_pool.remove(vlm.id)
        # delete the given vertical line marker
        del vlm
        # if there is no vertical line marker left, uncheck the vertical line marker button
        if len(self.vertical_marker_dict) == 0:
            self.navigator.ui.vertical_marker_button.setChecked(False)
        # update the chart
        self.chart().update()

    # delete the given measure marker
    def deleteMeasureMarker(self, mm: MeasureMarker):
        # remove the given measure marker from the chart
        self.chart().removeSeries(mm)
        mm.clearMeasureLine()
        # remove the given measure marker from the measure_marker_dict
        del self.measure_marker_dict[mm.id]
        # pop the id in the measure_marker_order list
        self.measure_marker_order.remove(mm.id)
        # dremove the id of the given measure marker from the id_pool
        MeasureMarker.id_pool.remove(mm.id)
        MeasureMarker.isinstance_count -= 1
        # delete the given measure marker
        del mm
        # if there is no measure marker left, uncheck the measure marker button
        if len(self.measure_marker_dict) == 0:
            self.navigator.ui.measure_button.setChecked(False)
            if self.point_marker is not None:
                self.point_marker.setVisible(False)
        # update the chart
        self.chart().update()

    # delete the given auxiliary line marker
    def deleteAuxiliaryLineMarker(self, alm: Union[VerticalAuxLineMarker, HorizontalAuxLineMarker]):
        # remove the given auxiliary line marker from the chart
        alm.clearMarker()
        # remove the given auxiliary line marker from the auxiliary_line_dict
        del self.aux_line_dict[alm.id]

        # delete the variable to prevent alm being used after it was removed from dict
        del alm

        # update the chart
        self.chart().update()

    def deleteAllAuxiliaryLineMarkers(self):
        if len(self.aux_line_dict) == 0:
            return
        # size of dictionary will be change during iteration, so use while loop not for loop
        while len(self.aux_line_dict) > 0:
            self.deleteAuxiliaryLineMarker(
                self.aux_line_dict.values().__iter__().__next__())
        self.aux_line_dict.clear()
        self.chart().update()

    def deleteLastMeasure(self):
        if self.measure_marker_dict != {} and self.measure_marker_order != []:
            self.deleteMeasureMarker(
                self.measure_marker_dict[self.measure_marker_order[-1]])
            return True
        return False

    def deleteAllMeasure(self):
        while len(self.measure_marker_dict) > 0:
            self.deleteLastMeasure()

    def extendVLMToSubchart(self, vlm: VerticalLineMarker):
        if self.sub_chart is None:
            self.navigator.showLabelMsg("No SubChart!")
            return
        if vlm.extended == True:
            return
        # get the x value of the given vertical line marker
        x_value = vlm.at(0).x()
        if len(self.sub_chart.series_dict) == 0:
            return
        elif len(self.sub_chart.series_dict) == 1:
            new_vlm = self.sub_chart.addVerticalLineMarker(
                list(self.sub_chart.series_dict.values())[0], x_value)
            new_vlm.showVLM()
            new_vlm.setExtended(vlm)
            vlm.setExtended(new_vlm)

        elif len(self.sub_chart.series_dict) > 1:
            # open a dialog to let user choose a series
            series_name, ok = QInputDialog.getItem(
                self, "Choose a series", "Series:", self.sub_chart.series_dict.keys(), 0, False)
            if ok:
                new_vlm = self.sub_chart.addVerticalLineMarker(
                    self.sub_chart.series_dict[series_name], x_value)
                new_vlm.showVLM()
                new_vlm.setExtended(vlm)
                vlm.setExtended(new_vlm)

    def cancelVLMExtension(self, vlm: VerticalLineMarker):
        if vlm.extended == False or vlm.extended_vlm is None:
            return
        self.sub_chart.deleteVerticalLineMarker(vlm.extended_vlm)
        vlm.disableExtension()

    # change the color of the given measure marker
    def changeMeasureColor(self, mm: MeasureMarker):
        # open a color dialog
        color = QColorDialog.getColor()
        # if the user clicks OK, change the color of the given measure marker
        if color.isValid():
            mm.setColor(color)  # set Measure Marker color
            # set Auxiliary Line Marker color
            for aux_line in [mm.halm1, mm.halm2, mm.valm1, mm.valm2]:
                if aux_line is not None:
                    aux_line.setColor(color)
            # set mm's text item's color
            mm.text_item.setDefaultTextColor(color)

    # change the mesuare marker's item text's position by cursor position
    def changeMeasureTextPosition(self, mm: MeasureMarker):
        self.moving_mm = mm
        self.moving_measure_marker_text_flag = True
        mm.text_pos_lock = True

    # if lock the text position, it will not be auto updated if chart is paned, zoomed or resized
    def lockMeasureTextPosition(self, mm: MeasureMarker):
        mm.text_pos_lock = not mm.text_pos_lock

    # change the color of the given vertical line marker
    def changeVLMColor(self, vlm: VerticalLineMarker):
        # open a color dialog
        color = QColorDialog.getColor()
        # if the user clicks OK, change the color of the given vertical line marker
        if color.isValid():
            vlm.setColor(color)

    # change the width of the given vertical line marker
    def changeVLMWidth(self, vlm: VerticalLineMarker):
        # open a dialog to get the new width
        new_width, ok = QInputDialog.getDouble(self, "Change Width", "New Width", vlm.pen().widthF(),
                                               0.0, sys.float_info.max, decimals=4)
        # if the user clicks OK, change the width of the given vertical line marker
        if ok:
            pen = QPen()
            pen.setColor(vlm.color())
            pen.setWidthF(new_width)
            vlm.setPen(pen)

    # change the position of the vertical line marker
    def changeVLMPosition(self, vlm: VerticalLineMarker):
        # open a dialog to get the new position
        new_pos, ok = QInputDialog.getDouble(self, "Change Position", "New Position", vlm.at(0).x(),
                                             -sys.float_info.max, sys.float_info.max, decimals=4)
        # if the user clicks OK, change the position of the vertical line marker
        if ok:
            vlm.updateVLM(new_pos)
    # change the color of the given auxiliary line marker

    def changeAuxLineColor(self, alm: Union[VerticalAuxLineMarker, HorizontalAuxLineMarker], color: QColor = None):
        if color is None:
            # open a color dialog
            color = QColorDialog.getColor()
        else:
            color = QColor(color)
        # if the user clicks OK, change the color of the given auxiliary line marker
        if color.isValid():
            alm.pen_backup.setColor(color)
            alm.setColor(color)

    # change the position of the auxiliary line marker
    def changeAuxLinePosition(self, alm: Union[VerticalAuxLineMarker, HorizontalAuxLineMarker]):
        # open a dialog to get the new position
        if alm.__class__.__name__ == "HorizontalAuxLineMarker":
            pos = alm.y_value
        else:
            pos = alm.x_value

        new_pos, ok = QInputDialog.getDouble(self, "Change Position", "New Position", pos,
                                             -sys.float_info.max, sys.float_info.max, decimals=4)
        # if the user clicks OK, change the position of the auxiliary line marker
        if ok:
            alm.setPosition(new_pos)
            alm.deletePointMarkers()

    # update the position of all vertical line marker in self.vertical_marker_dict
    def updateAllVLM(self,circular_marker_hide=False,text_not_update=False):
        for vlm in self.vertical_marker_dict.values():
            vlm.updateVLM(vlm.last_vertical_line_x_pos,circular_marker_hide,text_not_update)

    # hide all vertical line markers' circles
    def hideAllVLMCircle(self):
        for vlm in self.vertical_marker_dict.values():
            vlm.vlm_circle.setVisible(False)

    # change Measure Type of measure marker
    def changeMeasureType(self, mm: MeasureMarker, measure_type: str):
        # if measure_type is "Horizontal", change the measure marker to horizontal
        mm.changeType(measure_type)
        mm.setVisible(True)

    def addAuxiliaryLineMarker(self, type: str, pos: float):
        if type == "horizontal":
            new_alm = HorizontalAuxLineMarker(self, pos)
        elif type == "vertical":
            new_alm = VerticalAuxLineMarker(self, pos)
        self.aux_line_dict[new_alm.id] = new_alm
        return new_alm

    # # reveal the nearest point in the series to the current mouse position
    def revealNearestSinglePoint(self, chart_point: QPointF):
        # find the nearst series to the given chart point
        nearest_series: SmartLineSeries = None
        min_distance = 10
        for series in self.series_dict.values():
            series = series.interpolated_series  # use interpolated ones
            if series.isVisible():
                # find the closest point in the series to the given chart point
                for point in series.points():
                    dis = self._calculatePointDistance(chart_point, point)
                    if dis < min_distance:
                        min_distance = dis
                        nearest_series = series

        # if the nearest series is too far away from chart_point selected by cursor, return
        if min_distance > self.series_select_sensitivity or nearest_series is None:
            return

        # interpolate the nearest series with x value step size 0.01
        interpolated_series = nearest_series

        # find the nearest point in the series to the given chart point
        revealed_point = None
        for i, point in enumerate(interpolated_series.points()):
            if self._is_point_near(chart_point, point):
                revealed_point = point
                break

        if revealed_point is not None:
            if self.point_marker is not None:
                self.scene().removeItem(self.point_marker)
                pass
            point_in_chart = self.chart().mapToPosition(revealed_point)
            point_in_scene = self.mapToScene(point_in_chart.toPoint())
            viewport_position = self.mapFromScene(point_in_scene)
            self.point_marker = QGraphicsEllipseItem(viewport_position.x()-self.point_marker_radius,
                                                     viewport_position.y()-self.point_marker_radius,
                                                     2 * self.point_marker_radius, 2 * self.point_marker_radius)
            self.scene().addItem(self.point_marker)
        return revealed_point

    def revealAuxLineIntersectionPoint(self, alm: Union[VerticalAuxLineMarker, HorizontalAuxLineMarker], series: SmartLineSeries):
        # if alm pass through series, return the intersection point
        intersection_point = []
        if alm.__class__.__name__ == "HorizontalAuxLineMarker":
           # verify if the alm.y_value is between the y value of the point before and after the point
            for i in range(1, len(series.points())):
                point1 = series.points()[i-1]
                point2 = series.points()[i]
                if point1.y() <= alm.y_value <= point2.y() or point1.y() >= alm.y_value >= point2.y():
                    # calculate the intersection point
                    x = point1.x()+(point2.x()-point1.x()) * \
                        (alm.y_value-point1.y())/(point2.y()-point1.y())
                    intersection_point.append(QPointF(x, alm.y_value))
        elif alm.__class__.__name__ == "VerticalAuxLineMarker":
            # verify if the alm.x_value is between the x value of the point before and after the point
            for i in range(1, len(series.points())):
                point1 = series.points()[i-1]
                point2 = series.points()[i]
                if point1.x() <= alm.x_value <= point2.x() or point1.x() >= alm.x_value >= point2.x():
                    # calculate the intersection point
                    y = point1.y()+(point2.y()-point1.y()) * \
                        (alm.x_value-point1.x())/(point2.x()-point1.x())
                    intersection_point.append(QPointF(alm.x_value, y))
        return intersection_point

    def setAxesProperty(self, x_data: Union[list, np.ndarray] = [0.1, 2500], y_data: Union[list, np.ndarray] = [0, 100],
                        x_label: str = "", y_label: str = ""):
        if hasattr(self,"x_axis") and hasattr(self,"y_axis"):
            if self.x_axis is not None and self.y_axis is not None:
                if self.chart().axes() != []:
                    self.chart().removeAxis(self.x_axis)
                    self.chart().removeAxis(self.y_axis)
            # if any series is attached to the axis, remove the series from the axis
            for series in self.series_dict.values():
                self.chart().removeSeries(series)
            self.series_dict.clear()
        # set default x y axes
        if self.plot_type == "bode_mag":
            self.x_axis = QLogValueAxis()
            self.x_axis.setBase(10)
            self.x_axis.setRange(0.1, 2500)
            self.x_axis.setMinorTickCount(-1)
            self.x_axis.setLabelFormat("%g")
            self.x_axis.setTitleText(x_label)

            self.y_axis = QValueAxis()
            self.y_axis.setLabelFormat("%g")
            self.y_axis.setRange(((min(y_data)-20)//20+1)
                                 * 20, ((max(y_data)+20)//20+1)*20)
            # self.y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
            # self.y_axis.setTickInterval(20)
            # self.y_axis.setTickAnchor(0)
            self.y_axis.setTitleText(y_label)

        elif self.plot_type == "bode_phase":
            self.x_axis = QLogValueAxis()
            self.x_axis.setBase(10)
            self.x_axis.setRange(0.1, 2500)
            self.x_axis.setMinorTickCount(-1)
            self.x_axis.setLabelFormat("%g")
            self.x_axis.setTitleText(x_label)

            self.y_axis = QValueAxis()
            self.y_axis.setTickType(QValueAxis.TicksDynamic)
            self.y_axis.setTickInterval(45)
            self.y_axis.setTickAnchor(0)
            self.y_axis.setTickAnchor(90)
            self.y_axis.setTickAnchor(-90)
            self.y_axis.setTickAnchor(180)
            self.y_axis.setTickAnchor(-180)
            self.y_axis.setRange(min(y_data)-45, max(y_data)+45)
            self.y_axis.setTitleText(y_label)

        elif self.plot_type == "nichols":
            self.x_axis = QValueAxis()
            self.x_axis.setLabelFormat("%g")
            self.x_axis.setRange(min(x_data)-20, max(x_data)+20)
            #self.x_axis.setRange(-360, 0)
            self.x_axis.setTitleText(x_label)
            self.x_axis.setTickType(QValueAxis.TicksDynamic)
            self.x_axis.setTickInterval(45)

            self.y_axis = QValueAxis()
            self.y_axis.setLabelFormat("%g")
            self.y_axis.setRange(((min(y_data)-20)//20+1)
                                 * 20, ((max(y_data)+20)//20+1)*20)
            self.y_axis.setTitleText(y_label)

        elif self.plot_type == "normal":
            self.x_axis = QValueAxis()
            self.x_axis.setLabelFormat("%g")
            self.x_axis.setRange(min(x_data), max(x_data))
            self.x_axis.setTitleText(x_label)
            self.x_axis.setTickType(QValueAxis.TicksDynamic)
            self.x_axis.setTickInterval(10)

            self.y_axis = QValueAxis()
            self.y_axis.setLabelFormat("%g")
            self.y_axis.setRange(min(y_data), max(y_data))
            self.y_axis.setTitleText(y_label)
            self.y_axis.setTickType(QValueAxis.TicksDynamic)
            self.y_axis.setTickInterval(10)
        # series.updateProperty() # add interpolated version of series if necessary
        # x label font size
        self.x_axis.setLabelsFont(QFont("Arial", 8))
        # y label font size
        self.y_axis.setLabelsFont(QFont("Arial", 8))

    def adjustYTicks(self):
        if isinstance(self.y_axis, QValueAxis) and self.plot_type == "bode_mag":
            height = self.chart().plotArea().height()
            multiplier = 1
            if height > 200:
                multiplier = 1.5
            elif height > 100:
                multiplier = 2
            elif height > 50:
                multiplier = 2.5
            elif height > 10:
                multiplier = 3
            dis = self.y_axis.max()-self.y_axis.min()
            self.y_axis.setTickCount(dis//(20*multiplier))

    # set the chart title and subchart title as optional
    def setChartTitle(self, title: str, subchart_title: str = ""):
        if self.chart() is not None:
            self.chart().setTitle(title)
            if self.sub_chart is not None:
                self.sub_chart.chart().setTitle(subchart_title)

    def changeAxesType(self, new_x_axis_type, new_y_axis_type):
        if new_x_axis_type == "log":
            new_x_axis_type = QAbstractAxis.AxisType.AxisTypeLogValue
        elif new_x_axis_type == "linear":
            new_x_axis_type = QAbstractAxis.AxisType.AxisTypeValue
        if new_y_axis_type == "log":
            new_y_axis_type = QAbstractAxis.AxisType.AxisTypeLogValue
        elif new_y_axis_type == "linear":
            new_y_axis_type = QAbstractAxis.AxisType.AxisTypeValue

        if new_x_axis_type not in [QAbstractAxis.AxisType.AxisTypeLogValue, QAbstractAxis.AxisType.AxisTypeValue] or \
                new_y_axis_type not in [QAbstractAxis.AxisType.AxisTypeLogValue, QAbstractAxis.AxisType.AxisTypeValue]:
            return

        if new_x_axis_type == self.x_axis.type() and new_y_axis_type == self.y_axis.type():
            return
        change_X = False
        change_Y = False
        if new_x_axis_type != self.x_axis.type():
            if new_x_axis_type == QAbstractAxis.AxisType.AxisTypeLogValue:
                self.x_axis = QLogValueAxis()
                self.x_axis.setBase(10)
                self.x_axis.setRange(self.x_axis.min(), self.x_axis.max())
                self.x_axis.setMinorTickCount(-1)
                self.x_axis.setLabelFormat("%g")
                self.x_axis.setTitleText(self.x_axis.titleText())
            elif new_x_axis_type == QAbstractAxis.AxisType.AxisTypeValue:
                self.x_axis = QValueAxis()
                self.x_axis.setLabelFormat("%g")
                self.x_axis.setRange(self.x_axis.min(), self.x_axis.max())
                self.x_axis.setTickCount(10)
                self.x_axis.setTickInterval(10)
                self.x_axis.setTitleText(self.x_axis.titleText())
            change_X = True

        if new_y_axis_type != self.y_axis.type():
            if new_y_axis_type == QAbstractAxis.AxisType.AxisTypeLogValue:
                self.y_axis = QLogValueAxis()
                self.y_axis.setBase(10)
                self.y_axis.setRange(self.y_axis.min(), self.y_axis.max())
                self.y_axis.setMinorTickCount(-1)
                self.y_axis.setLabelFormat("%g")
                self.y_axis.setTitleText(self.y_axis.titleText())
            elif new_y_axis_type == QAbstractAxis.AxisType.AxisTypeValue:
                self.y_axis = QValueAxis()
                self.y_axis.setLabelFormat("%g")
                self.y_axis.setRange(self.y_axis.min(), self.y_axis.max())
                self.y_axis.setTickType(QValueAxis.TicksDynamic)
                self.y_axis.setTickInterval(10)
                self.y_axis.setTitleText(self.y_axis.titleText())
            change_Y = True

        if change_X:
            for series in self.series_dict.values():
                if series._isNegValueContained() and new_x_axis_type == QAbstractAxis.AxisType.AxisTypeLogValue:
                    self.navigator.showLabelMsg(
                        "Negative value is contained in the series, cannot change to log value axis")
                    return
                self.chart().setAxisX(self.x_axis, series)
        elif change_Y:
            for series in self.series_dict.values():
                if series._isNegValueContained() and new_y_axis_type == QAbstractAxis.AxisType.AxisTypeLogValue:
                    self.navigator.showLabelMsg(
                        "Negative value is contained in the series, cannot change to log value axis")
                    return
                self.chart().setAxisY(self.y_axis, series)
                # self.chart().setAxisY(self.y_axis, series)

        self.chart().update()
        self.updateSubChart()
        self.updateMarkerText()
        self.updateAuxLineMarker()

    # show the next intersection point of the given auxiliary line marker
    def showNextIntersectionPoint(self, alm: Union[VerticalAuxLineMarker, HorizontalAuxLineMarker], series=None):
        # pop up a dialog to ask user to select a series to show intersection point, if no series is selected, return
        # add a checkbox to ask user if he wants to show intersection point of all series
        if series is None:
            series_list = list(self.series_dict.values())
            series_list = [
                series for series in series_list if series.isVisible()]
            if len(series_list) == 0:
                # show navigation's label message to tell user that there is no series to select
                self.navigator.showLabelMsg("No series to select")
                return
            elif len(series_list) == 1:
                series = series_list[0]
            else:
                series_name_list = [series.name() for series in series_list]
                series_name, ok = QInputDialog.getItem(
                    self, "Select a series", "Series:", series_name_list, 0, False)
                if not ok:
                    return
                series = series_list[series_name_list.index(series_name)]
        intersection_points = self.revealAuxLineIntersectionPoint(alm, series)
        # show the next intersection point of the given auxiliary line marker
        if intersection_points != []:
            alm.deletePointMarkers()
            for point in intersection_points:
                alm.addPointMarker(PointMarker(self, point.x(), point.y()))

    def showIntersectionPoint(self, alm: Union[VerticalAuxLineMarker, HorizontalAuxLineMarker], which_point: str = "next"):
        # pop up a dialog to ask user to select a series to show intersection point, if no series is selected, return
        # add a checkbox to ask user if he wants to show intersection point of all series
        series_list = list(self.series_dict.values())
        series_list = [series for series in series_list if series.isVisible()]
        if len(series_list) == 0:
            # show navigation's label message to tell user that there is no series to select
            self.navigator.showLabelMsg("No series to select")
            return
        series_name_list = [series.name() for series in series_list]
        if len(series_list) > 1:
            series_name, ok = QInputDialog.getItem(
                self, "Select a series", "Series:", series_name_list, 0, False)
            if not ok:
                return
            series = series_list[series_name_list.index(series_name)]
        else:
            series = series_list[0]
        intersection_points = self.revealAuxLineIntersectionPoint(alm, series)
        if intersection_points != []:
            alm.deletePointMarkers()  # clear all previous point markers
            if which_point == "next":
                if alm.intersection_series == series and alm.intersection_points == intersection_points:
                    if len(alm.intersection_points_copy) == 0:
                        alm.intersection_points_copy = intersection_points.copy()
                    next_point = alm.intersection_points_copy.pop(0)
                    alm.addPointMarker(PointMarker(
                        self, next_point.x(), next_point.y()))
                else:
                    # if the intersection points are not the same as the previous one, update the intersection points and series
                    alm.intersection_series = series
                    alm.setIntersectionPoints(intersection_points)
                    next_point = alm.intersection_points_copy.pop(0)
                    alm.addPointMarker(PointMarker(
                        self, next_point.x(), next_point.y()))
            elif which_point == "all":
                for point in intersection_points:
                    alm.addPointMarker(PointMarker(self, point.x(), point.y()))
        else:
            self.navigator.showLabelMsg("No intersection point found")

    # display gain margin marker on the main chart
    def showGainMarginMarker(self, freq: list, mag: list, phase: list, dB=True):
        gain_margin, freq_neg_180 = self.calculateGainMargin(
            freq, mag, phase, dB)
        if gain_margin is not None:
            alm = self.addAuxiliaryLineMarker("vertical", freq_neg_180)
            self.showNextIntersectionPoint(alm)
            if self.sub_chart is not None:
                self.sub_chart.addAuxiliaryLineMarker("vertical", freq_neg_180)

    def showNicholsGrid(self):
        # show nichols grid on the main chart
        if self.plot_type == "nichols":
            if self.nichols_grid is None:
                self.nichols_grid = NicholsGrid(self)
                self.nichols_grid.showGrid()
            else:
                self.nichols_grid.hideGrid()
                self.nichols_grid = None

    def showStabilityMargin(self):
        if self.plot_type == "nichols":
            self.showNicholsMargin()

    def showNicholsMargin(self, gm: float = 10, pm: float = 50, color: str = "red"):
        self.nichols_margin_alm_h = self.addAuxiliaryLineMarker(
            "horizontal", 0-gm)
        self.nichols_margin_alm_v = self.addAuxiliaryLineMarker(
            "vertical", -180+pm)
        self.changeAuxLineColor(self.nichols_margin_alm_h, color)
        self.changeAuxLineColor(self.nichols_margin_alm_v, color)
        self.nichols_margin_lines = True

    def hideNicholsMargin(self):
        if self.plot_type == "nichols":
            alm_h_exist, alm_v_exist = self._checkNicholsMarginLine()
            if alm_h_exist:
                self.deleteAuxiliaryLineMarker(self.nichols_margin_alm_h)
                del self.nichols_margin_alm_h
            if alm_v_exist:
                self.deleteAuxiliaryLineMarker(self.nichols_margin_alm_v)
                del self.nichols_margin_alm_v
            self.nichols_margin_lines = False

    def _checkNicholsMarginLine(self):
        if hasattr(self, "nichols_margin_alm_h"):
            if self.nichols_margin_alm_h is not None:
                if self.nichols_margin_alm_h in self.aux_line_dict.values():
                    alm_h_exist = True
                else:
                    alm_h_exist = False
            else:
                alm_h_exist = False
        else:
            alm_h_exist = False

        if hasattr(self, "nichols_margin_alm_v"):
            if self.nichols_margin_alm_v is not None:
                if self.nichols_margin_alm_v in self.aux_line_dict.values():
                    alm_v_exist = True
                else:
                    alm_v_exist = False
            else:
                alm_v_exist = False
        else:
            alm_v_exist = False

        return alm_h_exist, alm_v_exist

    # pop up a diag to input the index of the intersection point to show
    def selectIntersectionPoint(self, alm: Union[VerticalAuxLineMarker, HorizontalAuxLineMarker]):
        # pop up a dialog to ask user to select a series to show intersection point, if no series is selected, return
        # add a checkbox to ask user if he wants to show intersection point of all series
        series_list = list(self.series_dict.values())
        series_list = [series for series in series_list if series.isVisible()]
        if len(series_list) == 0:
            # show navigation's label message to tell user that there is no series to select
            self.navigator.showLabelMsg("No series to select")
            return
        series_name_list = [series.name() for series in series_list]
        if len(series_list) > 1:
            series_name, ok = QInputDialog.getItem(
                self, "Select a series", "Series:", series_name_list, 0, False)
            if not ok:
                return
            series = series_list[series_name_list.index(series_name)]
        else:
            series = series_list[0]
        intersection_points = self.revealAuxLineIntersectionPoint(alm, series)
        if intersection_points != []:
            alm.deletePointMarkers()
            index, ok = QInputDialog.getInt(
                self, "Select a point", "Index:", 1, 1, len(intersection_points), 1)
            if ok:
                alm.addPointMarker(PointMarker(
                    self, intersection_points[index-1].x(), intersection_points[index-1].y()))
        else:
            self.navigator.showLabelMsg("No intersection point found")

    def _is_point_near(self, point1, point2):
        threshold_x = self.is_point_near_threshold_x
        threshold_y = self.is_point_near_threshold_y
        return (
            abs(point1.x() - point2.x()) <= threshold_x
            and abs(point1.y() - point2.y()) <= threshold_y
        )

    def _calculatePointDistance(self, point1, point2):
        if point1 is None or point2 is None:
            return None
        return math.sqrt((point1.x()-point2.x())**2+(point1.y()-point2.y())**2)


# customize the qlineseries
class SmartLineSeries(QLineSeries):
    instance_count = 0
    id_pool = set()
    # init

    def __init__(self, chart_view: SmartChartView, label: str = ""):
        super().__init__()
        self.chart_view = chart_view
        self.instance_count += 1
        self.label = label
        self.setupID()
        self.interval = 0
        self.interpolated_series = None
        self.interpolated_flag = False

    def setupID(self):
        # assign an id and try from 1,2,3,4,5... until an id is not in the id_pool
        id = 1
        while True:
            if id not in SmartLineSeries.id_pool:
                SmartLineSeries.id_pool.add(id)
                break
            id = id + 1
        self.id = id

    def addData(self, x: float, y: float):
        self.append(x, y)
        # if self.count()>1:
        #     self.interval = self.at(self.count()-1).x()-self.at(self.count()-2).x()

    # update the series with x,y data given
    def updateSeries(self, x_data: list, y_data: list):
        self.clear()
        for i in range(len(x_data)):
            self.append(x_data[i], y_data[i])
        self.setName(f"{self.label}")
        if len(x_data) > 0:
            self.interval = x_data[1]-x_data[0]

    def updateProperty(self):
        if self.chart_view.interpolated_series_step <= 0:
            self.interpolated_series = self
            self.interpolated_flag = False
        elif self.chart_view.interpolated_series_step >= self.interval:
            self.interpolated_series = self
            self.interpolated_flag = False
        elif self.count() > 100:
            self.interpolated_series = self
            self.interpolated_flag = False
        else:
            self._interpolateSeries(self.chart_view.interpolated_series_step)
            self.interpolated_flag = True

    def _interpolateSeries(self, step: float):
        if self.count() == 0:
            return None
        if self.count() == 1:
            return self
        self.interpolated_series = SmartLineSeries(self)
        x_min = self.at(0).x()
        x_max = self.at(self.count()-1).x()
        x = x_min
        while x <= x_max:
            y = self._interpolate_y_value(self, x)
            self.interpolated_series.append(x, y)
            x = x + step

    def _interpolate_y_value(self, lineseries: QLineSeries, x_value):
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

    def _isNegValueContained(self):
        for point in self.points():
            if point.y() < 0:
                return True
        return False


class SmartScatterSeries(QScatterSeries):
    instance_count = 0
    id_pool = set()
    # init

    def __init__(self, chart_view: SmartChartView, label: str = ""):
        super().__init__()
        self.chart_view = chart_view
        self.instance_count += 1
        self.label = label
        self.setMarkerSize(5)
        self.setupID()

    def setupID(self):
        # assign an id and try from 1,2,3,4,5... until an id is not in the id_pool
        id = 1
        while True:
            # share id_pool with SmartLineSeries
            if (id not in SmartLineSeries.id_pool) and (id not in SmartScatterSeries.id_pool):
                SmartScatterSeries.id_pool.add(id)
                break
            id = id + 1
        self.id = id

    # add data
    def addData(self, x: float, y: float):
        self.append(x, y)

    def updateSeries(self, x_data: list, y_data: list):
        self.clear()
        for i in range(len(x_data)):
            self.append(x_data[i], y_data[i])
        self.setName(f"My Series {self.label}")


class VerticalLineMarker(QLineSeries):
    instance_count = 0
    id_pool = set()

    def __init__(self, chart_view: SmartChartView, series: QLineSeries, x_value: float, vlm_circle_radius: float = 5):
        super().__init__()
        VerticalLineMarker.instance_count += 1
        self.setupID()                                    # set up the id
        # set legend of series
        self.setName(f"Vertical Line Marker {self.id}")
        self.setVisible(False)
        self.chart_view = chart_view
        self.series = series
        # set up the dragging flag
        self.is_line_dragging = False
        # Set up the vertical line position
        min_y = self.chart_view.chart().axisY().min()
        max_y = self.chart_view.chart().axisY().max()
        self.append(x_value, min_y)
        self.append(x_value, max_y)

        self.vlm_circle_radius = vlm_circle_radius             # set up the circle radius
        self.vlm_circle = QGraphicsEllipseItem(
            0, 0, 2 * self.vlm_circle_radius, 2 * self.vlm_circle_radius)
        # add the circle to the scene
        self.chart_view.scene().addItem(self.vlm_circle)
        self.vlm_circle.setVisible(False)

        # set up the pen color
        pen = QPen(Qt.black)
        # set up the pen width
        pen.setWidth(2)
        self.setPen(pen)                                       # set up the pen

        # add the series to the chart
        self.chart_view.addSeriestoXY(
            self, self.chart_view.x_axis, self.chart_view.y_axis, True)

        # init vertical line marker at middle of the chart
        min_x = self.chart_view.chart().axisX().min()
        max_x = self.chart_view.chart().axisX().max()

        self.last_vertical_line_x_pos = self.id * (max_x - min_x) / 5 + min_x
        self.last_vertical_line_x_percent = (
            self.last_vertical_line_x_pos - min_x) / (max_x-min_x)

        # add graphicstextitem
        self.text_item = QGraphicsTextItem()
        self.chart_view.scene().addItem(self.text_item)

        # add the VLM to the vertical_marker_dict
        self.chart_view.vertical_marker_dict[self.id] = self

        self.extended = False
        self.extended_vlm = None

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

    def updateVLM(self, x_value: float, circular_marker_hide=False,text_not_update = False):
        # get min and max of the self.chart().axisY()
        min_y = self.chart_view.chart().axisY().min()
        max_y = self.chart_view.chart().axisY().max()
        min_x = self.chart_view.chart().axisX().min()
        max_x = self.chart_view.chart().axisX().max()

        # get min and max of the self.series.x()
        series_min_x, series_max_x = self._get_min_max_x_values(self.series)

        # limit the x_value to the range of the series if enabled
        if self.chart_view.marker_limit_range_to_series:
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
        if not circular_marker_hide:
            # set the position of the circle to top of the vertical line
            top_point_viewport_position = self._convertPointFromChartViewtoViewPort(
                QPointF(x_value, max_y))
            self.vlm_circle.setPos(top_point_viewport_position.x()-self.vlm_circle_radius,
                                top_point_viewport_position.y()-self.vlm_circle_radius)
            # show the vertical line marker
            self.showVLM()
        else:
            self.setVisible(True)
            self.vlm_circle.setVisible(False)
            self.text_item.setVisible(True)

        # interpolate y value and show (x,y) in the text item
        y_value, ratio, i = self._interpolate_y_value(self.series, x_value)
        if ratio is not None and self.chart_view.nichols_frequency_series is not None:
            freq_y_value = self._interpolate_freq_value(
                self.chart_view.nichols_frequency_series, i, ratio)
        if y_value is not None:
            if self.chart_view.plot_type == "nichols" and ratio is not None and self.chart_view.nichols_frequency_series is not None:
                if not text_not_update:
                    self.text_item.setPlainText(
                        f"({x_value:.2f},{y_value:.2f}),freq:{freq_y_value:.2f}")
            else:
                if not text_not_update:
                    self.text_item.setPlainText(f"({x_value:.2f},{y_value:.2f})")
            text_pos = self.chart().mapToPosition(QPointF(x_value, y_value)) + QPointF(10, -20)  # Adjust the offset as needed
            self.text_item.setPos(text_pos)
        else:
            if not text_not_update:
                self.text_item.setPlainText("")

    def setExtended(self, vlm: VerticalLineMarker):
        self.extended = True
        self.extended_vlm = vlm

    def disableExtension(self):
        self.extended = False
        self.extended_vlm = None

    def _convertPointFromChartViewtoViewPort(self, point: QPointF):
        top_point = self.chart_view.chart().mapToPosition(point)
        top_point_in_scene = self.chart_view.mapToScene(top_point.toPoint())
        top_point_viewport_position = self.chart_view.mapFromScene(
            top_point_in_scene)
        return top_point_viewport_position

    def _get_min_max_x_values(self, series: QLineSeries):
        if not series.points():
            return None, None

        min_x = float("inf")
        max_x = float("-inf")

        for point in series.points():
            min_x = min(min_x, point.x())
            max_x = max(max_x, point.x())

        return min_x, max_x

    def _interpolate_y_value(self, lineseries: QLineSeries, x_value):
        points = [(p.x(), p.y()) for p in lineseries.pointsVector()]
        if not points:
            return None, None, None
        min_x = min(points[0][0], points[-1][0])
        max_x = max(points[0][0], points[-1][0])
        # If x_value is out of range, return the nearest point's y-value
        if x_value < min_x:
            return None, None, None
        if x_value > max_x:
            return None, None, None

        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            point_left_x = min(x1, x2)
            point_right_x = max(x1, x2)
            if point_left_x <= x_value <= point_right_x:
                # Linear interpolation
                y_value = y1 + (x_value - x1) * (y2 - y1) / (x2 - x1)
                ratio = (x_value - point_left_x)/(point_right_x-point_left_x)
                return y_value, ratio, i

        return None, None, None

    def _interpolate_freq_value(self, lineseries: QLineSeries, i: int, ratio: float):
        points = [(p.x(), p.y()) for p in lineseries.pointsVector()]
        if not points:
            return None

        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        point_left_y = min(y1, y2)
        point_right_y = max(y1, y2)
        # Linear interpolation
        y_value = (point_right_y - point_left_y)*ratio + point_left_y
        return y_value


class NicholsGrid:
    def __init__(self, chart_view: SmartChartView):
        self.chart_view = chart_view
        self.chart = self.chart_view.chart()
        self.scene = self.chart_view.scene()
        self.mn_centers = self._findMNCircleCenter()
        self.m_circles_list = []
        self.n_circles_list = []
        self.m_circles_series_list = []
        self.n_circles_series_list = []

    def _initMCircle(self):
        self.m_circle_magnitude = [0, 0.25, 0.5, 3, 6, -1, -3, -6, -12, -20]
        # create a circle data series
        for mag in self.m_circle_magnitude:
            m_circle = MCircle(self.chart_view, 10**(mag/20))
            self.m_circles_list.append(m_circle)

    def _initNCircle(self):
        self.n_circle_phase = [1, 5, 10, 20, 30, 40, 60,
                               80, 100, 120, 140, 150, 160, 170, 175, 179]
        # self.n_circle_phase = [1]
        # create a circle data series
        for phase in self.n_circle_phase:
            n_circle = NCircle(self.chart_view, phase)
            self.n_circles_list.append(n_circle)

    def showGrid(self):
        self._initMCircle()
        self._initNCircle()
        for mn_center in self.mn_centers:
            for m_circle in self.m_circles_list:
                phase_array = self._adjustNicholsPhase(
                    mn_center, m_circle.angle_array)
                new_series = QLineSeries()
                new_series.setPen(
                    QPen(Qt.GlobalColor.gray, 1, Qt.PenStyle.DashLine))
                for angle, mag in zip(phase_array, m_circle.mag_array):
                    new_series.append(angle, 20*np.log10(mag))
                self.m_circles_series_list.append(new_series)
                self.chart_view.addSeriestoXY(
                    new_series, self.chart_view.x_axis, self.chart_view.y_axis)

            for n_circle in self.n_circles_list:
                new_series = QLineSeries()
                angle_arr = self._adjustNicholsPhase(
                    mn_center, np.array(n_circle.angle_array))
                for angle, mag in zip(angle_arr, n_circle.mag_array):
                    new_series.append(angle, 20*np.log10(mag))
                points = new_series.points()
                points.sort(key=lambda point: (point.x(), point.y()))
                new_series = QLineSeries()
                new_series.setPen(
                    QPen(Qt.GlobalColor.gray, 1, Qt.PenStyle.DashLine))
                for point in points:
                    new_series.append(point)
                self.n_circles_series_list.append(new_series)
                self.chart_view.addSeriestoXY(
                    new_series, self.chart_view.x_axis, self.chart_view.y_axis)

    def hideGrid(self):
        for series in self.m_circles_series_list:
            self.chart_view.chart().removeSeries(series)
        for series in self.n_circles_series_list:
            self.chart_view.chart().removeSeries(series)
        self.m_circles_series_list = []
        self.n_circles_series_list = []
        self.m_circles_list = []
        self.n_circles_list = []

    def hideText(self):
        self.chart_view.nichols_grid_text = False

    def showText(self):
        self.chart_view.nichols_grid_text = True

    def _findMNCircleCenter(self):
        # determine if -180,180,180+360,-180-360 is in the current x range
        center = []
        for multiple in range(-10, 11):
            if -180 + multiple * 360 >= self.chart_view.x_axis.min() and -180 + multiple * 360 <= self.chart_view.x_axis.max():
                center.append(-180 + multiple * 360)
        if center != []:
            center.append(min(center)-360)
            center.append(max(center)+360)
        return center

    def _adjustNicholsPhase(self, center, phase_array: np.ndarray):
        # adjust the phase array by adding 360 or minusing 360 to make sure the center is in the array
        min_phase = min(phase_array)
        max_phase = max(phase_array)
        while min_phase - center >= 180:
            phase_array -= 360
            min_phase = min(phase_array)
        while max_phase - center <= -180:
            phase_array += 360
            max_phase = max(phase_array)
        return phase_array


class MCircle:
    def __init__(self, chart_view: SmartChartView, magnitude: float):
        super().__init__()
        self.magnitude = magnitude
        self.chart_view = chart_view
        self.angle_array, self.mag_array, self.center, self.radius = self.calculateCircle(
            magnitude)

    def calculateCircle(self, magnitude: float):
        angle_array = []
        mag_array = []
        if magnitude == 1:
            iter_array = np.concatenate(
                (np.arange(-100, -5, 1), np.arange(-5, 5, .01), np.arange(5, 100, 1)))
            for y in iter_array:
                angle = np.angle(-1/2+y*1j, deg=True)
                mag = np.abs(-1/2+y*1j)
                angle_array.append(angle)
                mag_array.append(mag)
                angle_array_ndarray = np.unwrap(
                    angle_array, period=360, discont=180)
            return angle_array_ndarray, mag_array, QPointF(-1/2, 0), 0
        # center of M circle
        center = QPointF(-magnitude**2/(magnitude**2-1), 0)
        # radius of M circle
        radius = np.sqrt(magnitude**2/(magnitude**2-1)**2)

        # create a circle data series
        iter_array = np.concatenate(
            (np.arange(0, 10, .1), np.arange(10, 350, 1), np.arange(350, 360, 0.1)))

        for i in iter_array:
            x = center.x() + radius * math.cos(math.radians(i))
            y = center.y() + radius * math.sin(math.radians(i))
            mag = np.abs(x+y*1j)
            angle = np.angle(x+y*1j, deg=True)
            angle_array.append(angle)
            mag_array.append(mag)

        angle_array = np.unwrap(angle_array, period=360, discont=180)

        return angle_array, mag_array, center, radius


class NCircle:
    def __init__(self, chart_view: SmartChartView, phase: float):
        super().__init__()
        self.phase = phase
        self.chart_view = chart_view
        self.angle_array, self.mag_array, self.center, self.radius = self.calculateCircle(
            phase)

    def calculateCircle(self, alpha: float):
        N = np.tan(alpha/180*np.pi)
        center = QPointF(-1/2, 1/(2*N))
        radius = np.sqrt(1/4+(1/(2*N))**2)
        angle_array = []
        mag_array = []
        iter_array = np.concatenate(
            (np.arange(0, 5, .1), np.arange(5, 355, 1), np.arange(355, 360, 0.1)))
        for i in iter_array:
            if i == 270:
                continue
            x = center.x() + radius * math.cos(math.radians(i))
            y = center.y() + radius * math.sin(math.radians(i))
            mag = np.abs(x+y*1j)
            angle = np.angle(x+y*1j, deg=True)
            if mag == 0 and angle == 0:
                continue
            if 20*np.log10(mag) < -40:
                continue
            angle_array.append(angle)
            mag_array.append(mag)
        # mag_array,angle_array= self._removePhaseData(mag_array,angle_array)
        # mag_array1,mag_array2,angle_array1,angle_array2 = self._partitionPhaseData(mag_array,angle_array)
        angle_array = list(np.unwrap(angle_array, period=360, discont=180))
        angle_array.append(min(angle_array)-0.1)
        mag_array.append(10**(-1000/20))
        angle_array.append(max(angle_array)+0.1)
        mag_array.append(10**(-1000/20))

        return angle_array, mag_array, center, radius

    def _removePhaseData(self, mag_array: list, angle_array: list):
        magnitude = 10**(6/20)
        center = QPointF(-magnitude**2/(magnitude**2-1), 0)
        radius = np.sqrt(magnitude**2/(magnitude**2-1)**2)
        # check if the points on n_circle is in the circle that defined by center and radius
        new_mag_array = []
        new_angle_array = []
        for i in range(len(angle_array)):
            point_on_n_cirlce_x = mag_array[i]*np.cos(angle_array[i]/180*np.pi)
            point_on_n_cirlce_y = mag_array[i]*np.sin(angle_array[i]/180*np.pi)
            # if point_on_n_cirlce is in the circle, remove the point
            dis = (point_on_n_cirlce_x-center.x())**2 + \
                (point_on_n_cirlce_y-center.y())**2
            if dis > radius**2:
                # remove the ith point
                new_mag_array.append(mag_array[i])
                new_angle_array.append(angle_array[i])
        return new_mag_array, new_angle_array

    def _partitionPhaseData(self, mag_array: list, angle_array: list):
        for i in range(len(angle_array)):
            if abs(angle_array[i+1] - angle_array[i]) > 5:
                return mag_array[0:i+1], mag_array[i+1:], angle_array[0:i+1], angle_array[i+1:]
        return None
