from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QFrame,QApplication
from .ui_plot_navigator import Ui_plot_navigator
from PySide6.QtCharts import QChartView
from PySide6.QtCore import QEvent,Qt
from PySide6.QtGui import QWheelEvent,QMouseEvent

# create a class for the plot navigator as QFrame  
class PlotNavigator(QFrame):
    #init the class with Ui_plot_navigator
    def __init__(self, main_chart_view:QChartView, parent = None):
        super().__init__(parent)
        self.ui = Ui_plot_navigator()
        self.ui.setupUi(self)
        self.initSignalSlot()
        self.main_chart_view = main_chart_view
        
    # init signal and slot
    def initSignalSlot(self):
        # set pan_view_button to checkable
        self.ui.pan_view_button.setCheckable(True)
        # click the pan_button to pan the chart
        #self.ui.pan_view_button.clicked.connect(self.panChart)
        self.ui.vertical_marker_button.setCheckable(True)
        #click the home_button to reset the chart
        self.ui.origin_view_button.clicked.connect(self.resetChart)

    # reset the chart
    def resetChart(self):
        # reset the plot area
        self.main_chart_view.chart().zoomReset()
        # reset the axis
        self.main_chart_view.chart().axisX().setRange(self.main_chart_view.default_x_range[0], self.main_chart_view.default_x_range[1])
        self.main_chart_view.chart().axisY().setRange(self.main_chart_view.default_y_range[0], self.main_chart_view.default_y_range[1])

        if self.ui.vertical_marker_button.isChecked():
            self.main_chart_view.update_vertical_line(self.main_chart_view.vertical_line_series.at(0).x())
    # # pan the chart
    # def panChart(self):
    #     # check if the pan_view_button is checked
    #     if not self.ui.pan_view_button.isChecked():
    #         # change the cursor to arrow
    #         self.main_chartView.setCursor(QtCore.Qt.ArrowCursor)
    #         # set the rubber band to NoRubberBand
    #         self.main_chartView.setRubberBand(QChartView.NoRubberBand)
    #         # set the drag mode to NoDrag
    #         self.main_chartView.setDragMode(QtWidgets.QGraphicsView.NoDrag)

    #         # if the second chart view is not None
    #         if self.second_chartView != None:
    #             # set the cursor to open hand
    #             self.second_chartView.setCursor(QtCore.Qt.ArrowCursor)
    #             # set the rubber band to NoRubberBand
    #             self.second_chartView.setRubberBand(QtWidgets.QChartView.NoRubberBand)
    #             # set the drag mode to NoDrag
    #             self.second_chartView.setDragMode(QtWidgets.QGraphicsView.NoDrag)
    #     else:
    #         self.ui.pan_view_button.setDown(True)
    #         # set the rubber band to RectangleRubberBand
    #         self.main_chartView.setRubberBand(QChartView.RectangleRubberBand)
    #         # set the drag mode to ScrollHandDrag
    #         self.main_chartView.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
    #         # if the second chart view is not None
    #         if self.second_chartView != None:
    #             # set the rubber band to RectangleRubberBand
    #             self.second_chartView.setRubberBand(QtWidgets.QChartView.RectangleRubberBand)
    #             # set the drag mode to ScrollHandDrag
    #             self.second_chartView.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
    #             # change the cursor to arrow
    #             self.second_chartView.setCursor(QtCore.Qt.ArrowCursor)
    
    # def eventFilter(self, obj, event):
    #     if obj == self.main_chartView or obj == self.second_chartView:

    #         if event.type() == QEvent.Type.MouseButtonPress:            # mouse press
    #             self.chartMousePressEvent(event)
    #             return True
    #         elif event.type() == QEvent.Type.MouseMove:                 # mouse release
    #             self.chartMouseMove(event)
    #             return True
    #         elif event.type() == QEvent.Type.Wheel:                     # mouse wheel     
    #             self.chartWheelEvent(event)
    #             return True
    #     return super().eventFilter(obj, event)
    
    # def chartWheelEvent(self, event: QWheelEvent):
    #     # zoom in or out using the mouse wheel
    #     if event.angleDelta().y() > 0:
    #         self.main_chartView.chart().zoomIn()
    #         if self.second_chartView != None:
    #             self.second_chartView.chart().zoomIn()
    #     else:
    #         self.main_chartView.chart().zoomOut()
    #         if self.second_chartView != None:
    #             self.second_chartView.chart().zoomOut()
    #     QApplication.processEvents()

    # def chartMousePressEvent(self, event: QMouseEvent):
    #     # start panning when the left mouse button is pressed
    #     if event.button() == Qt.MouseButton.LeftButton:
    #         print("godo")
    #         point_pos_on_chart= self.main_chartView.chart().mapToValue(event.position())
    #         self.last_mouse_pos = point_pos_on_chart
    #         print(point_pos_on_chart)
    #     QApplication.processEvents()

    # def chartMouseMove(self,event):
    #     print("moving")
    #     # show the current mouse position on the chart
    #     point_pos_on_chart= self.main_chartView.chart().mapToValue(event.position())
    #     # show point_pos_on chart on the "position_label" Qlabel
    #     self.ui.position_label.setText(f"X: {point_pos_on_chart.x():.2f}, Y: {point_pos_on_chart.y():.2f}")

    # def chartMouseReleaseEvent(self, event: QMouseEvent):
    #     if event.button() == Qt.MouseButton.LeftButton:
    #         self.main_chartView.setDragMode(QChartView.DragMode.NoDrag)
    #     QApplication.processEvents()
