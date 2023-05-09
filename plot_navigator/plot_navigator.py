from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QFrame
from .ui_plot_navigator import Ui_plot_navigator
from PySide6.QtCharts import QChartView

# create a class for the plot navigator as QFrame  
class PlotNavigator(QFrame):
    #init the class with Ui_plot_navigator
    def __init__(self, main_chartView, second_chartView = None, parent = None):
        super().__init__(parent)
        self.ui = Ui_plot_navigator()
        self.ui.setupUi(self)
        self.main_chartView = main_chartView
        self.second_chartView = second_chartView
        self.original_plot_area = None
        #init signal and slot  
        self.initSignalSlot()
    
    # init signal and slot
    def initSignalSlot(self):
        # set pan_view_button to checkable
        self.ui.pan_view_button.setCheckable(True)
        # click the pan_button to pan the chart
        self.ui.pan_view_button.clicked.connect(self.panChart)

        # click the home_button to reset the chart
        self.ui.origin_view_button.clicked.connect(self.resetChart)

    # reset the chart
    def resetChart(self):
        # reset the plot area
        self.main_chartView.chart().zoomReset()
        # if the second chart view is not None
        if self.second_chartView != None:
            # reset the plot area
            self.second_chartView.chart().zoomReset()

    # pan the chart
    def panChart(self):
        # check if the pan_view_button is checked
        if not self.ui.pan_view_button.isChecked():
            # change the cursor to arrow
            self.main_chartView.setCursor(QtCore.Qt.ArrowCursor)
            # set the rubber band to NoRubberBand
            self.main_chartView.setRubberBand(QChartView.NoRubberBand)
            # set the drag mode to NoDrag
            self.main_chartView.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            # if the second chart view is not None
            if self.second_chartView != None:
                # set the cursor to open hand
                self.second_chartView.setCursor(QtCore.Qt.ArrowCursor)
                # set the rubber band to NoRubberBand
                self.second_chartView.setRubberBand(QtWidgets.QChartView.NoRubberBand)
                # set the drag mode to NoDrag
                self.second_chartView.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        else:
            self.ui.pan_view_button.setDown(True)
            # set the rubber band to RectangleRubberBand
            self.main_chartView.setRubberBand(QChartView.RectangleRubberBand)
            # set the drag mode to ScrollHandDrag
            self.main_chartView.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            # if the second chart view is not None
            if self.second_chartView != None:
                # set the rubber band to RectangleRubberBand
                self.second_chartView.setRubberBand(QtWidgets.QChartView.RectangleRubberBand)
                # set the drag mode to ScrollHandDrag
                self.second_chartView.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
                # change the cursor to arrow
                self.second_chartView.setCursor(QtCore.Qt.ArrowCursor)



