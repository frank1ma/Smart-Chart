import pandas as pd
from PySide6.QtWidgets import QFrame,QMenu,QGraphicsView,QFileDialog,QInputDialog,QDialog,QDialogButtonBox
from .ui_plot_navigator import Ui_plot_navigator
from .ui_chart_options import Ui_chart_options
from .series_editor import SeriesEditor
from .measure import PointMarker
from PySide6.QtCharts import QChartView,QLineSeries,QValueAxis,QAbstractAxis,QLogValueAxis
from PySide6.QtCore import Qt,QTimer, QPointF, QSize, QRectF
from PySide6.QtGui import QAction,QPixmap, QPainter, QPdfWriter,QPageSize,QShortcut,QKeySequence
from PySide6.QtSvg import QSvgGenerator

# create a class for the plot navigator as QFrame  
class PlotNavigator(QFrame):
    #init the class with Ui_plot_navigator
    def __init__(self, main_chart_view:QChartView, parent = None):
        super().__init__(parent)
        self.main_chart_view = main_chart_view
        self.chart_options = {}
        self.ui = Ui_plot_navigator()
        self.ui.setupUi(self)
        self._initPopMenu()
        self._initSignalSlot()
        

       
        
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

        #click the setting button to set the chart title
        self.ui.series_editor_button.clicked.connect(self.showSeriesEditor)

        #click the setting_button to set the chart title
        self.ui.setting_button.clicked.connect(self.showOptionsDialog)

        #click the measure_button to measure the distance between two points
        self.ui.measure_button.setCheckable(True)
        self.ui.measure_button.clicked.connect(self.enableMeasure)

        #click the zoom_in_button to zoom in the chart
        self.ui.zoom_button.setCheckable(True)
        self.ui.zoom_button.clicked.connect(self.enableZoomInChart)

        #click the save_button to save the chart to svg, png, pdf, jpg,eps
        self.ui.save_button.clicked.connect(self.saveChart)

        # #check / uncheck the pan_view_button pop menu
        self.pan_pop_menu.actions()[0].triggered.connect(lambda: self.togglePanChart("x"))
        self.pan_pop_menu.actions()[1].triggered.connect(lambda: self.togglePanChart("y"))
        self.pan_pop_menu.actions()[2].triggered.connect(lambda: self.togglePanChart("both"))

    def _initPopMenu(self):
        self._initVerticalMarkerButtonPopMenu()
        self._initOriginViewButtonPopMenu()
        self._initMeasureButtonPopMenu()
        self._initPanButtonPopMenu()

    # init popmenu of the vertical marker button
    def _initVerticalMarkerButtonPopMenu(self):
        # create a pop menu
        self.vertical_marker_pop_menu = QMenu(self)
        self.vertical_marker_pop_menu.setStyleSheet("QMenu::item:disabled {color: gray;}")
        # add actions to the pop menu
        add_action = QAction("Add Vertical New Line Marker",self)
        limit_range_action = QAction("Set Range to Series",self)
        add_auxiliary_v_action = QAction("Add Vertical Auxiliary Line Marker",self)
        add_auxiliary_h_action = QAction("Add Horizontal Auxiliary Line Marker",self)
        delete_action = QAction("Delete All Auxiliary Line Markers",self)
        # create a action for the pop menu
        self.vertical_marker_pop_menu.addAction(add_action)
        self.vertical_marker_pop_menu.addAction(limit_range_action)
        self.vertical_marker_pop_menu.addSeparator()
        self.vertical_marker_pop_menu.addAction(add_auxiliary_v_action)
        self.vertical_marker_pop_menu.addAction(add_auxiliary_h_action)
        self.vertical_marker_pop_menu.addSeparator()
        self.vertical_marker_pop_menu.addAction(delete_action)
        # set the pop menu to the vertical marker button
        self.ui.vertical_marker_button.setMenu(self.vertical_marker_pop_menu)

        # set limit_range_action to checkable
        limit_range_action.setCheckable(True)
        # connect the action to the slot
        add_action.triggered.connect(self.addVerticalLineMarker)
        limit_range_action.triggered.connect(self._limitRangeToSeries)
        add_auxiliary_v_action.triggered.connect(lambda: self.addAuxiliaryLineMarker("vertical"))
        add_auxiliary_h_action.triggered.connect(lambda: self.addAuxiliaryLineMarker("horizontal"))
        delete_action.triggered.connect(self.deleteAllAuxiliaryLineMarkers)

        # grey out limit range action
        limit_range_action.setEnabled(False)
 
    # init popmenu of the measure button
    def _initMeasureButtonPopMenu(self):
        # create a pop menu
        self.measure_pop_menu = QMenu(self)

        # add actions to the pop menu
        add_vm_action = QAction("Add Vertical Measure",self)
        add_hm_action = QAction("Add Horizontal Measure",self)
        add_p2p_action = QAction("Add Point-to-Point", self)
        # add actions to delete last measure
        delete_last_mm_action = QAction("Delete Last Measure",self)
        delete_all_mm_action = QAction("Delete All Measure",self)

        # create a action for the pop menu
        self.measure_pop_menu.addAction(add_vm_action)
        self.measure_pop_menu.addAction(add_hm_action)
        self.measure_pop_menu.addAction(add_p2p_action)
        self.measure_pop_menu.addSeparator()
        self.measure_pop_menu.addAction(delete_last_mm_action)
        self.measure_pop_menu.addAction(delete_all_mm_action)
        # set the pop menu to the measure button
        self.ui.measure_button.setMenu(self.measure_pop_menu)

        # connect the action to the slot
        add_vm_action.triggered.connect(lambda: self.selectMeasure("vertical"))
        add_hm_action.triggered.connect(lambda: self.selectMeasure("horizontal"))
        add_p2p_action.triggered.connect(lambda: self.selectMeasure("p2p"))
        delete_last_mm_action.triggered.connect(self.main_chart_view.deleteLastMeasure)
        delete_all_mm_action.triggered.connect(self.main_chart_view.deleteAllMeasure)

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

    def _initPanButtonPopMenu(self):
        # create a pop menu
        self.pan_pop_menu = QMenu(self)
        # add pan x direction only action
        pan_x_action = QAction("Pan X Direction Only",self)
        # add pan y direction only action
        pan_y_action = QAction("Pan Y Direction Only",self)
        # add pan x and y direction action
        pan_xy_action = QAction("Pan X and Y Direction",self)
        # create a action for the pop menu
        self.pan_pop_menu.addAction(pan_x_action)
        self.pan_pop_menu.addAction(pan_y_action)
        self.pan_pop_menu.addAction(pan_xy_action)
        # set pan x direction only action to checkable
        pan_x_action.setCheckable(True)
        pan_y_action.setCheckable(True)
        pan_xy_action.setCheckable(True)
        # set the pop menu to the pan_view_button
        self.ui.pan_view_button.setMenu(self.pan_pop_menu)

        # connect the action to the slot
        pan_x_action.triggered.connect(self.enablePanChart)
        pan_y_action.triggered.connect(self.enablePanChart)
        pan_xy_action.triggered.connect(self.enablePanChart)

    # show default vertical marker
    def showVerticalMarker(self):
        if self.ui.vertical_marker_button.isChecked():
            if len(self.main_chart_view.vertical_marker_dict)==0:
                new_vlm = self.addVerticalLineMarker()
                if new_vlm is None:
                    self.ui.vertical_marker_button.setChecked(False)
                    return
            self.main_chart_view.updateAllVLM()
            # enable the actions
            self.vertical_marker_pop_menu.actions()[1].setEnabled(True) # limit range action
        else:
            if len(self.main_chart_view.vertical_marker_dict)==0:
                return
            else:
                for vlm in self.main_chart_view.vertical_marker_dict.values():
                    vlm.setVisible(False)
                    vlm.vlm_circle.setVisible(False)
                    vlm.text_item.setPlainText("")
            # disable the actions
            self.vertical_marker_pop_menu.actions()[1].setEnabled(False) # limit range action

    #show the series editor to allow user to choose which series to show by using checkboxes
    def showSeriesEditor(self):
        # create a series editor as SeriesEditor which includes checkboxes for each series
        self.series_editor = SeriesEditor(self,data_label="Plant")
        # if return is ok, then update the visbiility of the series using self.main_chart_view.updateSeriesVisibility()
        if self.series_editor.exec() == QDialog.Accepted:
            self.main_chart_view.updateSeriesVisibility(self.series_editor.get_series_to_show())
    
    #show the setting dialog to allow user to set the chart title
    def showOptionsDialog(self):
        # create a setting dialog as QDialog
        self.options_dialog = QDialog(self)
        # create a ui for the setting dialog
        self.options_dialog.ui = Ui_chart_options()
        # setup the ui for the setting dialog
        self.options_dialog.ui.setupUi(self.options_dialog)
        # register the standard buttons
        self.options_dialog.ui.buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Apply | QDialogButtonBox.Cancel)
        # connect the buttons to the slots
        self.options_dialog.ui.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.options_dialog.accept)
        self.options_dialog.ui.buttonBox.button(QDialogButtonBox.Apply).clicked.connect(self.applyChartOptions)
        self.options_dialog.ui.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.options_dialog.reject)
        self.options_dialog.ui.horizontalScrollBar_x.valueChanged.connect(lambda: self.options_dialog.ui.label_pan_x.setText(f"Pan X Sensitivity: {str(self.options_dialog.ui.horizontalScrollBar_x.value())}"))
        self.options_dialog.ui.horizontalScrollBar_y.valueChanged.connect(lambda: self.options_dialog.ui.label_pan_y.setText(f"Pan Y Sensitivity: {str(self.options_dialog.ui.horizontalScrollBar_y.value())}"))
        
        # self.options_dialog.ui.button_ok.clicked.connect(self.options_dialog.accept)
        # self.options_dialog.ui.button_apply.clicked.connect(self.applyChartOptions)
        # self.options_dialog.ui.button_cancel.clicked.connect(self.options_dialog.reject)

        # load the chart information to the setting dialog
        self.updateOptionsDict()
        self.updateChartOptionsForm(self.options_dialog)
        val = self.options_dialog.exec()
        if  val == QDialog.Accepted:
            if self.applyChartOptions():
            # update the msg_label "Chart Title Updated" and clear it after 3 seconds
                self.showLabelMsg("Chart Options Updated")
            else:
                #self.showLabelMsg("Chart Options Update Failed")
                pass



    # reset the chart
    def resetChart(self):
        # reset the plot area
        self.main_chart_view.chart().zoomReset()
        # reset the axis
        self.main_chart_view.chart().axisX().setRange(self.main_chart_view.default_x_range[0], self.main_chart_view.default_x_range[1])
        self.main_chart_view.chart().axisY().setRange(self.main_chart_view.default_y_range[0], self.main_chart_view.default_y_range[1])
        
        if self.main_chart_view.sub_chart!=None:
            self.main_chart_view.updateSubChart()
            pass
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
                self.showLabelMsg("Save Chart Error", 3000)
            else:
                self.showLabelMsg("Chart Saved", 3000)
    
    def saveSeriesToCSV(self, id_list: list):
        if len(id_list) == 0:
            self.showLabelMsg("No Series Selected", 3000)
            return
        # set the default file name in Qfiledialog
        file_dialog = QFileDialog(self)
        file_dialog.setDefaultSuffix("csv")
        # set the default file name to the main_chart_view.chart_title
        default_name = (self.main_chart_view.chart().title())
        default_directory = "./" 
        # get the file path
        file_path, _ = file_dialog.getSaveFileName(self, "Save the chart to", default_directory+default_name, 
            "CSV files (*.csv)")
        if file_path:
            try:
                self._saveSeriesToCSV(id_list, file_path)
            except:
                self.showLabelMsg("Save Series Error", 3000)
            else:
                self.showLabelMsg("Series Saved", 3000)

    def togglePanChart(self,direction):
        if direction == "x":
            if not self.pan_pop_menu.actions()[0].isChecked():
                self.pan_pop_menu.actions()[0].setChecked(False)
            else:
                self.pan_pop_menu.actions()[0].setChecked(True)
                self.pan_pop_menu.actions()[1].setChecked(False)
                self.pan_pop_menu.actions()[2].setChecked(False)
                self.main_chart_view.pan_direction = "x"
                
        elif direction == "y":
            if not self.pan_pop_menu.actions()[1].isChecked():
                #print("y1")
                self.pan_pop_menu.actions()[1].setChecked(False)
            else:
                #print("y2")
                self.pan_pop_menu.actions()[0].setChecked(False)
                self.pan_pop_menu.actions()[1].setChecked(True)
                self.pan_pop_menu.actions()[2].setChecked(False)
                self.main_chart_view.pan_direction = "y"
        elif direction == "both":
            if not self.pan_pop_menu.actions()[2].isChecked():
                self.pan_pop_menu.actions()[2].setChecked(False)
            else:
                self.pan_pop_menu.actions()[0].setChecked(False)
                self.pan_pop_menu.actions()[1].setChecked(False)
                self.pan_pop_menu.actions()[2].setChecked(True)
                self.main_chart_view.pan_direction = "both"
        
    # pan the chart
    def enablePanChart(self):
        if self.ui.pan_view_button.isChecked():
            self.main_chart_view.setRubberBand(QChartView.NoRubberBand)
            self.main_chart_view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            if self.pan_pop_menu.actions()[0].isChecked():
                self.main_chart_view.pan_direction = "x"
            elif self.pan_pop_menu.actions()[1].isChecked():
                self.main_chart_view.pan_direction = "y"
            else:
                self.main_chart_view.pan_direction = "both"
            if self.ui.zoom_button.isChecked():  # if zoom button is checked, uncheck it
                self.ui.zoom_button.setChecked(False)
        else:
            self.main_chart_view.setDragMode(QGraphicsView.DragMode.NoDrag)

    # enable the measure mode
    def enableMeasure(self):
        if self.ui.measure_button.isChecked():
            self.main_chart_view.setRubberBand(QChartView.NoRubberBand)
            self.main_chart_view.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.main_chart_view.new_measure_request = True
            # show label msg that measure mode is enabled
            self.showLabelMsg("Measure Mode On")
            if self.ui.zoom_button.isChecked():
                self.ui.zoom_button.setChecked(False)
            elif self.ui.pan_view_button.isChecked():
                self.ui.pan_view_button.setChecked(False)
        else:
            self.main_chart_view.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.main_chart_view.new_measure_request = False
            # show label msg that measure mode is disabled
            self.showLabelMsg("Measure Mode Off")
            if self.main_chart_view.point_marker!=None:
                self.main_chart_view.point_marker.setVisible(False)
    
    def selectMeasure(self,type:str):
        self.main_chart_view.current_measure_type = type
        self.ui.measure_button.setChecked(True)
        self.enableMeasure()

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
        self.showLabelMsg("Default View Set and Updated")

    # set the default range to original view from original x and y range, 
    def restoreOriginView(self):
        self.main_chart_view.default_x_range = self.main_chart_view.original_x_range
        self.main_chart_view.default_y_range = self.main_chart_view.original_y_range
        self.resetChart()
        if self.main_chart_view.sub_chart!=None:
            self.main_chart_view.sub_chart.navigator.restoreOriginView()
            self.main_chart_view.updateSubChart()
        if self.ui.vertical_marker_button.isChecked():
            self._setAllVerticalLineMarkerLastXPos()
        # update the msg_label "Orignal View restored" and clear it after 3 seconds
        self.showLabelMsg("Orignal View restored")

    # add a vertical line marker to the chart
    def addVerticalLineMarker(self):
        # if no series in the chart, return None
        if len(self.main_chart_view.series_dict)==0:
            self.showLabelMsg("No Series in the Chart. Please Series first.", 3000)
            return None
        if len(self.main_chart_view.series_dict)>1:
            # pop up a dialog to ask for which series to add the vertical line marker, add color of series to each item
            series_name, ok = QInputDialog.getItem(self, "Select Series", "Series:", 
                                                [f"{series.label} ({str(series.id)})" for 
                                                    series in self.main_chart_view.series_dict.values()], 0, False)
            if ok:
                # extract series.id from series_name
                series_id = int(series_name.split("(")[-1].split(")")[0])
                # get the series from series_id
                series = self.main_chart_view.series_dict[series_id]
            else:
                return None
        else:
            series = list(self.main_chart_view.series_dict.values())[0]
        vertical_line_marker = self.main_chart_view.addVerticalLineMarker(series,self.main_chart_view.chart().axisX().min()*1.2)
        vertical_line_marker.updateVLM(vertical_line_marker.last_vertical_line_x_pos)
        # if vertical_marker_button is not checked, check it
        if not self.ui.vertical_marker_button.isChecked():
            self.ui.vertical_marker_button.setChecked(True)
        return vertical_line_marker

        
    def addAuxiliaryLineMarker(self,line_type:str):
        # pop up a dialog to input the position of the auxiliary line marker according to line_type
        # if it's a horizontal line, ask for y position, if it's a vertical line, ask for x position
        if line_type=="horizontal":
            pos, ok = QInputDialog.getDouble(self, "Input Position", "Y Position:",
                                              self.main_chart_view.chart().axisY().min()*1.5,decimals=4)
            if ok:
                self.main_chart_view.addAuxiliaryLineMarker(line_type,pos)
        elif line_type=="vertical":
            pos, ok = QInputDialog.getDouble(self, "Input Position", "X Position:",
                                              self.main_chart_view.chart().axisX().min()*1.5,decimals=4)
            if ok:
                self.main_chart_view.addAuxiliaryLineMarker(line_type,pos)
    
    # apply the chart setting
    def applyChartOptions(self):
        # load the content of the dialog to the dictionary self.chart_options
        try:
            self.chart_options["chart_title"] = self.options_dialog.ui.lineEdit_title.text()
            self.chart_options["x_axis_min"] = float(self.options_dialog.ui.lineEdit_x_min.text())
            self.chart_options["x_axis_max"] = float(self.options_dialog.ui.lineEdit_x_max.text())
            self.chart_options["y_axis_min"] = float(self.options_dialog.ui.lineEdit_y_min.text())
            self.chart_options["y_axis_max"] = float(self.options_dialog.ui.lineEdit_y_max.text())
            self.chart_options["x_axis_label"] = self.options_dialog.ui.lineEdit_x_label.text()
            self.chart_options["y_axis_label"] = self.options_dialog.ui.lineEdit_y_label.text()
            # load the pan sensitivity to the dictionary self.chart_options
            self.chart_options["pan_sensitivity_x"] = self.options_dialog.ui.horizontalScrollBar_x.value()/20.0
            self.chart_options["pan_sensitivity_y"] = self.options_dialog.ui.horizontalScrollBar_y.value()/20.0
            # load the subchart_sync_x_axis
            self.chart_options["subchart_sync_x_axis"] = self.options_dialog.ui.checkBox_subchart_sync_x_axis.isChecked()
            # load the subchart_sync_y_axis
            self.chart_options["subchart_sync_y_axis"] = self.options_dialog.ui.checkBox_subchart_sync_y_axis.isChecked()
            # load the marker size
            self.chart_options["point_marker_size"] = self.options_dialog.ui.spinBox_point_maker_size.value()
            # load x,y scale
            self.chart_options["x_axis_type"] = self.options_dialog.ui.comboBox_x_scale.currentIndex()
            self.chart_options["y_axis_type"] = self.options_dialog.ui.comboBox_y_scale.currentIndex()

        except ValueError:
            self.showLabelMsg("Invalid Input", 5000)
            return False
        except Exception as e:
            self.showLabelMsg(str(e), 5000)
            return False
        
        if self.chart_options["x_axis_min"] >= self.chart_options["x_axis_max"]:
            self.showLabelMsg("Error! xMin >= xMax", 5000)
            return False
        if self.chart_options["y_axis_min"] >= self.chart_options["y_axis_max"]:
            self.showLabelMsg("Error! yMin >= yMax", 5000)
            return False
        try:
            # set the chart title
            self.main_chart_view.chart().setTitle(self.chart_options["chart_title"])
            # set the x axis range
            self.main_chart_view.chart().axisX().setRange(self.chart_options["x_axis_min"], self.chart_options["x_axis_max"])
            # set the y axis range
            self.main_chart_view.chart().axisY().setRange(self.chart_options["y_axis_min"], self.chart_options["y_axis_max"])
            # set the x axis label
            self.main_chart_view.chart().axisX().setTitleText(self.chart_options["x_axis_label"])
            # set the y axis label
            self.main_chart_view.chart().axisY().setTitleText(self.chart_options["y_axis_label"])
            # set the pan sensitivity
            self.main_chart_view.pan_x_sensitivity = self.chart_options["pan_sensitivity_x"]
            self.main_chart_view.pan_y_sensitivity = self.chart_options["pan_sensitivity_y"]
            # set the subchart_sync_x_axis
            self.main_chart_view.subchart_sync_x_axis = self.chart_options["subchart_sync_x_axis"]
            # set the subchart_sync_y_axis
            self.main_chart_view.subchart_sync_y_axis = self.chart_options["subchart_sync_y_axis"]
            # set the point marker size
            PointMarker.marker_size = self.chart_options["point_marker_size"]

            # set the x,y scale
            if self.chart_options["x_axis_type"] == 0:
                x_axis_type = QAbstractAxis.AxisType.AxisTypeValue
            elif self.chart_options["x_axis_type"] == 1:
                x_axis_type = QAbstractAxis.AxisType.AxisTypeLogValue
            if self.chart_options["y_axis_type"] == 0:
                y_axis_type = QAbstractAxis.AxisType.AxisTypeValue
            elif self.chart_options["y_axis_type"] == 1:
                y_axis_type = QAbstractAxis.AxisType.AxisTypeLogValue

            self.main_chart_view.changeAxesType(x_axis_type, y_axis_type)
 
        except Exception as e:
            self.showLabelMsg(str(e), 5000)
            return False
        # update the chart
        self.main_chart_view.chart().update()


        
    def deleteAllAuxiliaryLineMarkers(self):
        self.main_chart_view.deleteAllAuxiliaryLineMarkers()
        return True
    # remove a series from the chart
    def removeSeries(self):
        # pop up a dialog to ask for which series to remove, add color of series to each item
        series_name, ok = QInputDialog.getItem(self, "Select Series", "Series:", 
                                               [f"{series.label} ({str(series.id)})" for 
                                                series in self.main_chart_view.series_dict.values()], 0, False)
        if ok:
            # extract series.id from series_name
            series_id = int(series_name.split("(")[-1].split(")")[0])
            # get the series from series_id
            series = self.main_chart_view.series_dict[series_id]
            # remove the series from the chart
            self.main_chart_view.removeSeries(series)
            # update the msg_label "Series Removed" and clear it after 3 seconds
            self.showLabelMsg("Series Removed")
        else:
            pass

    
    def updateOptionsDict(self):
        # load the chart title to the dictionary self.chart_options
        self.chart_options["chart_title"] = self.main_chart_view.chart().title()
        # load the x axis min and max to the dictionary self.chart_options
        self.chart_options["x_axis_min"] = self.main_chart_view.chart().axisX().min()
        self.chart_options["x_axis_max"] = self.main_chart_view.chart().axisX().max()
        # load the y axis min and max to the dictionary self.chart_options
        self.chart_options["y_axis_min"] = self.main_chart_view.chart().axisY().min()
        self.chart_options["y_axis_max"] = self.main_chart_view.chart().axisY().max()
        # load the x axis label to the dictionary self.chart_options
        self.chart_options["x_axis_label"] = self.main_chart_view.chart().axisX().titleText()
        # load the y axis label to the dictionary self.chart_options
        self.chart_options["y_axis_label"] = self.main_chart_view.chart().axisY().titleText()

        # load the pan sensitivity to the dictionary self.chart_options
        self.chart_options["pan_sensitivity_x"] = int(self.main_chart_view.pan_x_sensitivity*20)
        self.chart_options["pan_sensitivity_y"] = int(self.main_chart_view.pan_y_sensitivity*20)

        # load the subchart_sync_x_axis
        self.chart_options["subchart_sync_x_axis"] = self.main_chart_view.subchart_sync_x_axis
        
        # load the subchart_sync_y_axis
        self.chart_options["subchart_sync_y_axis"] = self.main_chart_view.subchart_sync_y_axis

        # load the point marker size
        self.chart_options["point_marker_size"] = PointMarker.marker_size

        # load the type of axis of x and y
        self.chart_options["x_axis_type"] = self.main_chart_view.chart().axisX().type()
        self.chart_options["y_axis_type"] = self.main_chart_view.chart().axisY().type()

    # update the self.options_dialog with the content in self.chart_options
    def updateChartOptionsForm(self,diag:QDialog):
        diag.ui.lineEdit_title.setText(self.chart_options["chart_title"])
        diag.ui.lineEdit_x_min.setText(str(self.chart_options["x_axis_min"]))
        diag.ui.lineEdit_x_max.setText(str(self.chart_options["x_axis_max"]))
        diag.ui.lineEdit_y_min.setText(str(self.chart_options["y_axis_min"]))
        diag.ui.lineEdit_y_max.setText(str(self.chart_options["y_axis_max"]))
        diag.ui.lineEdit_x_label.setText(self.chart_options["x_axis_label"])
        diag.ui.lineEdit_y_label.setText(self.chart_options["y_axis_label"])
        # update the slider value acccording to the pan sensitivity
        diag.ui.horizontalScrollBar_x.setValue(self.chart_options["pan_sensitivity_x"])
        diag.ui.horizontalScrollBar_y.setValue(self.chart_options["pan_sensitivity_y"])
        diag.ui.label_pan_x.setText(f"Pan X Sensitivity: {self.chart_options['pan_sensitivity_x']}")
        diag.ui.label_pan_y.setText(f"Pan Y Sensitivity: {self.chart_options['pan_sensitivity_y']}")
        diag.ui.spinBox_point_maker_size.setValue(self.chart_options["point_marker_size"])
        if self.chart_options["subchart_sync_x_axis"] == True:
            diag.ui.checkBox_subchart_sync_x_axis.setChecked(True)
        else:
            diag.ui.checkBox_subchart_sync_x_axis.setChecked(False)
        if self.chart_options["subchart_sync_y_axis"] == True:
            diag.ui.checkBox_subchart_sync_y_axis.setChecked(True)
        else:
            diag.ui.checkBox_subchart_sync_y_axis.setChecked(False)
        # update the type of axis of x and y
        if self.chart_options["x_axis_type"] == QAbstractAxis.AxisType.AxisTypeLogValue:
            diag.ui.comboBox_x_scale.setCurrentIndex(1)
        elif self.chart_options["x_axis_type"] == QAbstractAxis.AxisType.AxisTypeValue:
            diag.ui.comboBox_x_scale.setCurrentIndex(0)
        
        if self.chart_options["y_axis_type"] == QAbstractAxis.AxisType.AxisTypeLogValue:
            diag.ui.comboBox_y_scale.setCurrentIndex(1)
        elif self.chart_options["y_axis_type"] == QAbstractAxis.AxisType.AxisTypeValue:
            diag.ui.comboBox_y_scale.setCurrentIndex(0)

    def _limitRangeToSeries(self):
        # limit the range of the vertical line marker to the range of series
        self.main_chart_view.markerLimitRangeToSeries = not self.main_chart_view.markerLimitRangeToSeries

    def _setAllVerticalLineMarkerLastXPos(self):
        # set all vlm in self.main_chart_view.vertical_line_series to the last x pos of the vertical line marker
        for vlm in self.main_chart_view.vertical_marker_dict.values():
            self._setVerticalLineMarkerLastXPos(vlm)
            #self.main_chart_view.update_vertical_line(vlm,vlm.last_vertical_line_x_pos)
            self.main_chart_view.updateAllVLM()

    def _setVerticalLineMarkerLastXPos(self,vertical_line_marker:QLineSeries):
        # if (vertical_line_marker.last_vertical_line_x_pos < self.main_chart_view.chart().axisX().min()
        #     or vertical_line_marker.last_vertical_line_x_pos > self.main_chart_view.chart().axisX().max()):
        #     vertical_line_marker.last_vertical_line_x_pos = (self.main_chart_view.chart().axisX().min() + 
        #                                                     self.main_chart_view.chart().axisX().max())/2
        vertical_line_marker.last_vertical_line_x_pos = self.main_chart_view.chart().axisX().min() + \
                                                        vertical_line_marker.last_vertical_line_x_percent * \
                                                         (self.main_chart_view.chart().axisX().max() - 
                                                        self.main_chart_view.chart().axisX().min())

    def showLabelMsg(self,message,time=3000):
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
        
    # save the series with given id to csv file using pandas
    def _saveSeriesToCSV(self, id_list, file_path):
        # if id_list is empty, return None
        if len(id_list) == 0:
            return None
        # create an empty dataframe
        df = pd.DataFrame()
        # for each id in id_list, get the series from self.main_chart_view.series_dict
        for id in id_list:
            series = self.main_chart_view.series_dict[id]       
            points = series.pointsVector()
            # get the x and y data from pointsvector
            x_data = [point.x() for point in points]
            y_data = [point.y() for point in points]
            # create a dataframe with the x and y data
            df_temp = pd.DataFrame({f"{series.label} index":range(1,len(x_data)+1),"x":x_data,"y":y_data})
            # concat the dataframe to df
            df = pd.concat([df,df_temp],axis=1)

        # save the dataframe to csv file
        df.to_csv(file_path)
        # update the msg_label "Series Saved" and clear it after 3 seconds
        self.showLabelMsg("Series Saved")


        
       
    
