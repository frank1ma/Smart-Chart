from PySide6.QtWidgets import QFrame,QMenu,QGraphicsView,QFileDialog
from .ui_plot_navigator import Ui_plot_navigator
from PySide6.QtCharts import QChartView,QLineSeries
from PySide6.QtCore import Qt,QTimer, QPointF, QSize, QRectF
from PySide6.QtGui import QAction,QPixmap, QPainter, QPdfWriter,QPageSize
from PySide6.QtSvg import QSvgGenerator

# create a class for the plot navigator as QFrame  
class PlotNavigator(QFrame):
    #init the class with Ui_plot_navigator
    def __init__(self, main_chart_view:QChartView, parent = None):
        super().__init__(parent)
        self.ui = Ui_plot_navigator()
        self.ui.setupUi(self)
        self._initSignalSlot()
        self._initPopMenu()
        self.main_chart_view = main_chart_view
        
    # init signal and slot
    def _initSignalSlot(self):
        # set pan_view_button to checkable
        # connect the button to the slot
        self.ui.pan_view_button.setCheckable(True)
        self.ui.pan_view_button.clicked.connect(self.enablePanChart)

        self.ui.vertical_marker_button.setCheckable(True)
        self.ui.vertical_marker_button.clicked.connect(self.showVerticalMarker)

        #click the home_button to reset the chart
        self.ui.origin_view_button.clicked.connect(self.resetChart)

        #click the zoom_in_button to zoom in the chart
        self.ui.zoom_button.setCheckable(True)
        self.ui.zoom_button.clicked.connect(self.enableZoomInChart)

        #click the save_button to save the chart to svg, png, pdf, jpg,eps
        self.ui.save_button.clicked.connect(self.saveChart)

    def _initPopMenu(self):
        self._initVerticalMarkerButtonPopMenu()
        self._initOriginViewButtonPopMenu()

    # init popmenu of the vertical marker button
    def _initVerticalMarkerButtonPopMenu(self):
        # create a pop menu
        self.vertical_marker_pop_menu = QMenu(self)
        # add actions to the pop menu
        add_action = QAction("Add Vertical New Line Marker",self)
        delete_action = QAction("Delete Vertical Line Marker",self)
        limit_range_action = QAction("Set Range to Series",self)
        # create a action for the pop menu
        self.vertical_marker_pop_menu.addAction(add_action)
        self.vertical_marker_pop_menu.addAction(delete_action)
        self.vertical_marker_pop_menu.addAction(limit_range_action)
        # set the pop menu to the vertical marker button
        self.ui.vertical_marker_button.setMenu(self.vertical_marker_pop_menu)

        # set limit_range_action to checkable
        limit_range_action.setCheckable(True)
        # connect the action to the slot
        add_action.triggered.connect(self.addVerticalLineMarker)
        #delete_action.triggered.connect(self.deleteVerticalMarker)
        limit_range_action.triggered.connect(self._limitRangeToSeries)

    #init popmenu of the original view button
    def _initOriginViewButtonPopMenu(self):
        # create a pop menu
        self.origin_view_pop_menu = QMenu(self)
        # add actions to the pop menu
        set_action = QAction("Set Defualt View",self)
        restore_action = QAction("Restore the Original View",self)
        # create a action for the pop menu
        self.origin_view_pop_menu.addAction(set_action)
        self.origin_view_pop_menu.addAction(restore_action)
        # set the pop menu to the vertical marker button
        self.ui.origin_view_button.setMenu(self.origin_view_pop_menu)

        # connect the action to the slot
        set_action.triggered.connect(self.setDefualtView)
        restore_action.triggered.connect(self.restoreOriginView)

    # show default vertical marker
    def showVerticalMarker(self):
        if self.ui.vertical_marker_button.isChecked():
            if len(self.main_chart_view.vertical_marker_dict)==0:
                new_vlm = self.addVerticalLineMarker()
            for vlm in self.main_chart_view.vertical_marker_dict.values():
                vlm.setVisible(True)
                vlm.vlm_circle.setVisible(True)
                self._setVerticalLineMarkerLastXPos(vlm)
                self.main_chart_view.update_vertical_line(vlm,vlm.last_vertical_line_x_pos)
        else:
            if len(self.main_chart_view.vertical_marker_dict)==0:
                return
            else:
                for vlm in self.main_chart_view.vertical_marker_dict.values():
                    vlm.setVisible(False)
                    vlm.vlm_circle.setVisible(False)
                    vlm.text_item.setPlainText("")

    # reset the chart
    def resetChart(self):
        # reset the plot area
        self.main_chart_view.chart().zoomReset()
        # reset the axis
        self.main_chart_view.chart().axisX().setRange(self.main_chart_view.default_x_range[0], self.main_chart_view.default_x_range[1])
        self.main_chart_view.chart().axisY().setRange(self.main_chart_view.default_y_range[0], self.main_chart_view.default_y_range[1])

        if self.ui.vertical_marker_button.isChecked():
            self._setAllVerticalLineMarkerLastXPos()
    
    # save the chart to svg, png, pdf, jpg,eps
    def saveChart(self):
        # set the default file name in Qfiledialog
        file_dialog = QFileDialog(self)
        file_dialog.setDefaultSuffix("jpg")
        # set the default file name to the main_chart_view.chart_title
        default_name = (self.main_chart_view.chart().title())
        default_directory = "./" 
        # get the file path
        file_path, _ = file_dialog.getSaveFileName(self, "Save the chart to", default_directory+default_name, 
            "JPG files (*.jpg);;PNG files (*.png);;PDF files (*.pdf);;SVG files (*.svg)")
        if file_path:
            #get file type from the file_path
            file_type = file_path.split(".")[-1]
            try:
                if file_type == "jpg" or file_type =="png":
                    # save the chart in the chartview to the file_path
                    self.main_chart_view.grab().save(file_path)
                    
                else:
                    # save the chart in the chartview to the file_path
                    self._saveChart(self.main_chart_view, file_path,file_type)
            except:
                self._showLabelMsg("Save Chart Error", 3000)
            else:
                self._showLabelMsg("Chart Saved", 3000)

    # pan the chart
    def enablePanChart(self):
        if self.ui.pan_view_button.isChecked():
            self.main_chart_view.setRubberBand(QChartView.NoRubberBand)
            self.main_chart_view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            if self.ui.zoom_button.isChecked():  # if zoom button is checked, uncheck it
                self.ui.zoom_button.setChecked(False)
        else:
            self.main_chart_view.setDragMode(QGraphicsView.DragMode.NoDrag)
    # set rubberband to zoom in the chart
    def enableZoomInChart(self):
        if self.ui.zoom_button.isChecked():
            if self.ui.pan_view_button.isChecked(): # if pan button is checked, uncheck it
                self.ui.pan_view_button.setChecked(False)
        else:
            self.main_chart_view.setRubberBand(QChartView.NoRubberBand)
            self.main_chart_view.setDragMode(QGraphicsView.DragMode.NoDrag)

    def setDefualtView(self):
        # set the default range of x and y axis to the current range of axes
        self.main_chart_view.default_x_range = [self.main_chart_view.chart().axisX().min(), self.main_chart_view.chart().axisX().max()]
        self.main_chart_view.default_y_range = [self.main_chart_view.chart().axisY().min(), self.main_chart_view.chart().axisY().max()]
        self.resetChart()
        if self.ui.vertical_marker_button.isChecked():
            self._setAllVerticalLineMarkerLastXPos()
        self._showLabelMsg("Default View Set and Updated")

    # set the default range to original view from original x and y range, 
    def restoreOriginView(self):
        self.main_chart_view.default_x_range = self.main_chart_view.original_x_range
        self.main_chart_view.default_y_range = self.main_chart_view.original_y_range
        self.resetChart()
        if self.ui.vertical_marker_button.isChecked():
            self._setAllVerticalLineMarkerLastXPos()
        # update the msg_label "Orignal View restored" and clear it after 3 seconds
        self._showLabelMsg("Orignal View restored")

    # add a vertical line marker to the chart
    def addVerticalLineMarker(self):
        vertical_line_marker = self.main_chart_view.addVerticalLineMarker(self.main_chart_view.chart().axisX().min()*1.1)
        #selfMarker.(vertical_line_marker)
        return vertical_line_marker

    def _limitRangeToSeries(self):
        # limit the range of the vertical line marker to the range of series
        self.main_chart_view.markerLimitRangeToSeries = not self.main_chart_view.markerLimitRangeToSeries

    def _setAllVerticalLineMarkerLastXPos(self):
        # set all vlm in self.main_chart_view.vertical_line_series to the last x pos of the vertical line marker
        for vlm in self.main_chart_view.vertical_marker_dict.values():
            self._setVerticalLineMarkerLastXPos(vlm)
            self.main_chart_view.update_vertical_line(vlm,vlm.last_vertical_line_x_pos)

    def _setVerticalLineMarkerLastXPos(self,vertical_line_marker:QLineSeries):
        # if (vertical_line_marker.last_vertical_line_x_pos < self.main_chart_view.chart().axisX().min()
        #     or vertical_line_marker.last_vertical_line_x_pos > self.main_chart_view.chart().axisX().max()):
        #     vertical_line_marker.last_vertical_line_x_pos = (self.main_chart_view.chart().axisX().min() + 
        #                                                     self.main_chart_view.chart().axisX().max())/2
        vertical_line_marker.last_vertical_line_x_pos = self.main_chart_view.chart().axisX().min() + \
                                                        vertical_line_marker.last_vertical_line_x_percent * \
                                                         (self.main_chart_view.chart().axisX().max() - 
                                                        self.main_chart_view.chart().axisX().min())

    def _showLabelMsg(self,message,time=3000):
        # if message label is not empty, wait for 3 seconds and show message
        if self.ui.msg_label.text() != "":
            QTimer.singleShot(time, lambda: self.ui.msg_label.clear())
        self.ui.msg_label.setText(message)
        QTimer.singleShot(time, lambda: self.ui.msg_label.clear())
        # set the message label font color to navy blue
        self.ui.msg_label.setStyleSheet("color: navy")

    def _saveChart(self,chart_view, file_path, file_format):
        if file_format.lower() == "pdf":
            pdf_writer = QPdfWriter(file_path)
            pdf_writer.setPageSize(QPageSize.A4)
            painter = QPainter(pdf_writer)
            chart_view.render(painter)
            painter.end()
        elif file_format.lower() == "svg":
            svg_generator = QSvgGenerator()
            svg_generator.setFileName(file_path)
            svg_generator.setSize(QSize(chart_view.width(), chart_view.height()))
            svg_generator.setViewBox(QRectF(0, 0, chart_view.width(), chart_view.height()))
            painter = QPainter(svg_generator)
            chart_view.render(painter)
            painter.end()
        else:
            raise ValueError("Unsupported file format")


        
       
    
