from __future__ import annotations
from PySide6.QtCharts import QChartView, QChart, QLineSeries, QValueAxis,QScatterSeries
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QPolygonF, QPolygon
from PySide6.QtCore import QPointF, QRectF, Qt, QLineF, QSizeF, QRect
from PySide6.QtWidgets import QGraphicsTextItem,QGraphicsSimpleTextItem
import math

class Measure:
    # Measure is a base class that defines what a measure in the QChartView is
    # there are different types of measures, such as horizontal measure, vertical measure, 
    # and point-to-point measure, etc

    def __init__(self):
        self.left_point = None
        self.right_point = None

    def setReferencePoints(self,point1:QPointF,point2:QPointF):
        if point1 is None or point2 is None:
            return
        elif point1 == point2:
            return
        else:
            # if point1 is left of point2, then point1 is the left point
            self.left_point = point1 if point1.x() < point2.x() else point2
            self.right_point = point1 if point1.x() > point2.x() else point2

    # calculate the horizontal distance between two points
    def calculateHorizontalDistance(self):
        return abs(self.left_point.x() - self.right_point.x())
    
    # calculate the vertical distance between two points
    def calculateVerticalDistance(self):
        return abs(self.left_point.y() - self.right_point.y())
    
    # calculate the distance between two points in QPointF
    def calculateDistance(self):
        diff_vector= self.left_point - self.right_point
        return math.sqrt(diff_vector.x()**2 + diff_vector.y()**2)
    
class MeasureMarker(QLineSeries):
    isinstance_count = 0
    id_pool = set()
    # MeasureMarker is a QLineSeries that is used to draw the measure line
    # it is a child class of QLineSeries
    def __init__(self, chart_view:QChartView,measure:Measure):
        super().__init__()
        self.chart_view = chart_view
        self.setupID()
        self.setName(f"MeasureMarker{self.id}")
        self.measure = measure
        pen = QPen()
        pen.setWidth(1)
        pen.setColor(Qt.black)
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setDashPattern([1,4])
        self.setPen(pen)
        # change line type to dash line
        self.point1 = None
        self.point2 = None
        self.point1_marker = None
        self.point2_marker = None
        self.valm1 = None
        self.valm2 = None
        self.halm1 = None
        self.halm2 = None
        self.text_item = None

        # add count
        MeasureMarker.isinstance_count += 1
        
    def setupID(self):
        # assign an id and try from 1,2,3,4,5... until an id is not in the id_pool
        id = 1
        while True:
            if id not in MeasureMarker.id_pool:
                MeasureMarker.id_pool.add(id)
                break
            id = id + 1
        self.id = id
    
    def checkCompleteStatus(self):
        if self.measure.left_point != None and self.measure.right_point != None:
            return True
        elif self.point1 != None and self.point2 != None:
            return True
        else:
            return False
        
    def setPoint(self, point:QPointF):
       # whichever point is set first is point1, else point2
        if self.point1 is None:
            self.point1 = point
            self.point1_marker = PointMarker(self.chart_view,point.x(),point.y())
            if self.point1 is not None and self.point2 is not None:
                self.measure.setReferencePoints(self.point1, self.point2)
                self.clearPoint()
                return True
            else:
                return False
        elif self.point2 is None:
            self.point2 = point
            self.point2_marker = PointMarker(self.chart_view,point.x(),point.y())
            if self.point1 is not None and self.point2 is not None:
                self.measure.setReferencePoints(self.point1, self.point2)
                self.clearPoint()
                return True
            else:
                return False
        
    def clearPoint(self):
        self.point1 = None
        self.point2 = None
        if self.point1_marker != None:
            self.point1_marker.clearMarker()
            self.point1_marker = None
        if self.point2_marker != None:
            self.point2_marker.clearMarker()
            self.point2_marker = None

    # find the intersection point of point1's vertical line and point2's horizontal line, and draw the measure line
    # depends on which point has a larger y value, the intersection point is either point1's vertical line and point2's horizontal line
    # or point2's vertical line and point1's horizontal line
    def drawVerticalMeasureLine(self):
        if self.measure.left_point is None or self.measure.right_point is None:
            return
        else:
            self.point1_marker = PointMarker(self.chart_view,self.measure.left_point.x(),self.measure.left_point.y())
            self.point2_marker = PointMarker(self.chart_view,self.measure.right_point.x(),self.measure.right_point.y())
            if self.measure.left_point.y() > self.measure.right_point.y():  
                self.measure_line = QLineF(self.measure.left_point.x(), self.measure.left_point.y(), self.measure.left_point.x(), self.measure.right_point.y())
            else:
                self.measure_line = QLineF(self.measure.right_point.x(), self.measure.right_point.y(), self.measure.right_point.x(), self.measure.left_point.y())
            self.clear()
            self.append(self.measure_line.p1())
            self.append(self.measure_line.p2())

            if self.measure.left_point.y() > self.measure.right_point.y():  
            # add horizontal aux line marker
                self.halm1 = HorizontalAuxLineMarker(self.chart_view, self.measure.left_point.y(),self.measure_line.p1().x()*0.8,self.measure.right_point.x())
                self.halm2 = HorizontalAuxLineMarker(self.chart_view, self.measure.right_point.y(),self.measure_line.p2().x()*0.8,self.measure.right_point.x())
            else:
                         # add horizontal aux line marker
                self.halm1 = HorizontalAuxLineMarker(self.chart_view, self.measure.left_point.y(),self.measure_line.p1().x()*1.2,self.measure.left_point.x())
                self.halm2 = HorizontalAuxLineMarker(self.chart_view, self.measure.right_point.y(),self.measure_line.p2().x()*1.2,self.measure.left_point.x())
            # add text item above the marker
            self.text_item = QGraphicsTextItem()
            # set the position of the text item to the middle of the measure line
            viewport_pos = self._convertPointFromChartViewtoViewPort(QPointF(self.measure_line.center().x(), self.measure_line.p2().y()))
            self.text_item.setPos(viewport_pos)
            self.text_item.setPlainText(f"Vertical Dis:{self.measure.calculateVerticalDistance():.3f}")
            self.chart_view.scene().addItem(self.text_item)

    # drawHorizontalMeasureLine is similar to drawVerticalMeasureLine
    def drawHorizontalMeasureLine(self):
        if self.measure.left_point is None or self.measure.right_point is None:
            return
        else:
            self.point1_marker = PointMarker(self.chart_view,self.measure.left_point.x(),self.measure.left_point.y())
            self.point2_marker = PointMarker(self.chart_view,self.measure.right_point.x(),self.measure.right_point.y())
            if self.measure.left_point.y() > self.measure.right_point.y():  
                self.measure_line = QLineF(self.measure.left_point.x(), self.measure.left_point.y(), self.measure.right_point.x(), self.measure.left_point.y())
            else:
                self.measure_line = QLineF(self.measure.left_point.x(), self.measure.right_point.y(), self.measure.right_point.x(), self.measure.right_point.y())
            self.clear()
            self.append(self.measure_line.p1())
            self.append(self.measure_line.p2())

            self.valm1 = VerticalAuxLineMarker(self.chart_view, self.measure.left_point.x(),self.measure_line.p1().y())
            self.valm2 = VerticalAuxLineMarker(self.chart_view, self.measure.right_point.x(),self.measure_line.p1().y())
            
            # add text item above the marker
            self.text_item = QGraphicsTextItem()
            # set the position of the text item to the middle of the measure line
            viewport_pos = self._convertPointFromChartViewtoViewPort(QPointF(self.measure_line.p2().x(), self.measure_line.center().y()))
            self.text_item.setPos(viewport_pos)
            self.text_item.setPlainText(f"Horizontal Dis:{self.measure.calculateHorizontalDistance():.3f}")
            self.chart_view.scene().addItem(self.text_item)

    # drawPointToPointMeasureLine is similar to drawVerticalMeasureLine
    def drawPointToPointMeasureLine(self):
        if self.measure.left_point is None or self.measure.right_point is None:
            return
        else:
            self.point1_marker = PointMarker(self.chart_view,self.measure.left_point.x(),self.measure.left_point.y())
            self.point2_marker = PointMarker(self.chart_view,self.measure.right_point.x(),self.measure.right_point.y())
            self.measure_line = QLineF(self.measure.left_point, self.measure.right_point)
            self.clear()
            self.append(self.measure_line.p1())
            self.append(self.measure_line.p2())

            # add text item above the marker
            self.text_item = QGraphicsTextItem()
            # set the position of the text item to the middle of the measure line
            viewport_pos = self._convertPointFromChartViewtoViewPort(QPointF(self.measure_line.center().x(), self.measure_line.center().y()))
            self.text_item.setPos(viewport_pos)
            self.text_item.setPlainText(f"Point to Point Dis:{self.measure.calculateDistance():.3f}")
            self.chart_view.scene().addItem(self.text_item)

    def changeType(self, type):
        self.clearMeasureLine()
        if type == "vertical":
            self.drawVerticalMeasureLine()
        elif type == "horizontal":
            self.drawHorizontalMeasureLine()
        elif type == "p2p":
            self.drawPointToPointMeasureLine()
        return 

    def clearMeasureLine(self):
        self.clear()
        self.measure_line = None
        if self.text_item is not None:
            self.chart_view.scene().removeItem(self.text_item)
        self.text_item = None
        aux_line_marker = [self.valm1, self.valm2, self.halm1, self.halm2]
        for marker in aux_line_marker:
            if marker is not None:
                marker.clearMarker()
                marker.__class__.isinstance_count -= 1
                marker.__class__.id_pool.remove(marker.id)
                del marker
        self.valm1, self.valm2, self.halm1, self.halm2 = None,None,None,None

        point_marker = [self.point1_marker,self.point2_marker]
        for marker in point_marker:
            if marker is not None:
                marker.clearMarker()
                marker.__class__.isinstance_count -= 1
                marker.__class__.id_pool.remove(marker.id)
                del marker
        self.point1_marker,self.point2_marker = None,None

    def _convertPointFromChartViewtoViewPort(self, point:QPointF):
        point = self.chart_view.chart().mapToPosition(point)
        point_in_scene = self.chart_view.mapToScene(point.toPoint())
        point_viewport_position = self.chart_view.mapFromScene(point_in_scene)
        return point_viewport_position


# horizontal auxiliary line marker class
class HorizontalAuxLineMarker(QLineSeries):
    isinstance_count = 0
    id_pool = set()
    def __init__(self, chart_view:QChartView, y_value:float, x1_value:float=None,x2_value:float=None):
        super().__init__()
        self.chart_view = chart_view
        HorizontalAuxLineMarker.isinstance_count += 1
        self.y_value = y_value
        self.x1_value = x1_value
        self.x2_value = x2_value
        self.setupID()
        self.setName(f"HorizontalAuxLineMarker_{self.id}")
        self.chart_view.aux_line_dict[self.id] = self
        pen = QPen()
        pen.setWidth(1)
        pen.setColor(Qt.black)
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setDashPattern([1,4])
        self.setPen(pen)
        # add the horizontal line with y_value across the current x range of chart
        if self.x1_value != None and self.x2_value != None:
            self.append(QPointF(self.x1_value, self.y_value))
            self.append(QPointF(self.x2_value, self.y_value))
        else:
            self.append(QPointF(self.chart_view.chart().axisX().min(), self.y_value))
            self.append(QPointF(self.chart_view.chart().axisX().max(), self.y_value))
        self.chart_view.addSeriestoXY(self, self.chart_view.x_axis, self.chart_view.y_axis)
        self.show()
    def setupID(self):
        # assign an id and try from 1,2,3,4,5... until an id is not in the id_pool
        id = 1
        while True:
            if id not in HorizontalAuxLineMarker.id_pool:
                HorizontalAuxLineMarker.id_pool.add(id)
                break
            id = id + 1
        self.id = id
        
    def clearMarker(self):
        self.chart_view.chart().removeSeries(self)
        return True
    
    def getInterpolatedALM(self, x_value:float):
        # get the interpolated y value from the ALM
        # return None if the x_value is out of range
        if x_value < self.chart_view.chart().axisX().min() or x_value > self.chart_view.chart().axisX().max():
            return None
        else:
            return self.interpolated(x_value)

# vertical auxiliary line marker class
class VerticalAuxLineMarker(QLineSeries):
    isinstance_count = 0
    id_pool = set()
    def __init__(self, chart_view:QChartView, x_value:float, y_value:float=None):
        super().__init__()
        self.chart_view = chart_view
        VerticalAuxLineMarker.isinstance_count += 1
        self.x_value = x_value
        self.y_value = y_value
        self.setupID()
        self.setName(f"VerticalAuxLineMarker_{self.id}")
        pen = QPen()
        pen.setWidth(1)
        pen.setColor(Qt.black)
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setDashPattern([1,4])
        self.setPen(pen)
        # add the vertical line with x_value across the current y range of chart
        if self.y_value!=None:
            self.append(QPointF(self.x_value, self.y_value*1.2))
            self.append(QPointF(self.x_value, self.y_value*0.8))
        else:
            self.append(QPointF(self.x_value, self.chart_view.x_axis.min()))
            self.append(QPointF(self.x_value, self.chart_view.y_axis.max()))
        self.chart_view.addSeriestoXY(self, self.chart_view.x_axis, self.chart_view.y_axis)
        self.show()
        
    def setupID(self):
        # assign an id and try from 1,2,3,4,5... until an id is not in the id_pool
        id = 1
        while True:
            if id not in VerticalAuxLineMarker.id_pool:
                VerticalAuxLineMarker.id_pool.add(id)
                break
            id = id + 1
        self.id = id
    
    def clearMarker(self):
        self.chart_view.chart().removeSeries(self)
        return True
    

class PointMarker(QScatterSeries):
    isinstance_count = 0
    id_pool = set()
    def __init__(self, chart_view:QChartView, x_value:float, y_value:float):
        super().__init__()
        self.chart_view = chart_view
        PointMarker.isinstance_count += 1
        self.x_value = x_value
        self.y_value = y_value
        self.setupID()
        self.setName(f"PointMarker_{self.id}")
        self.setMarkerSize(10)
        self.setMarkerShape(QScatterSeries.MarkerShape.MarkerShapeCircle)
        self.setBrush(QBrush(Qt.red))
        self.append(QPointF(self.x_value, self.y_value))
        self.chart_view.addSeriestoXY(self, self.chart_view.x_axis, self.chart_view.y_axis)

        # add point coordinate text label
        self.point_coordinate_label = QGraphicsSimpleTextItem(f"({self.x_value:.3f},{self.y_value:.3f})")
        view_point_pos = self._convertPointFromChartViewtoViewPort(QPointF(self.x_value, self.y_value))
        self.point_coordinate_label.setPos(view_point_pos.x(), view_point_pos.y())
        self.point_coordinate_label.setBrush(QBrush(Qt.red))
        self.chart_view.scene().addItem(self.point_coordinate_label)
        self.show()
        
    def setupID(self):
        # assign an id and try from 1,2,3,4,5... until an id is not in the id_pool
        id = 1
        while True:
            if id not in PointMarker.id_pool:
                PointMarker.id_pool.add(id)
                break
            id = id + 1
        self.id = id
    
    def clearMarker(self):
        self.chart_view.chart().removeSeries(self)
        self.chart_view.scene().removeItem(self.point_coordinate_label)
        self.point_coordinate_label = None
        return True
    
    def _convertPointFromChartViewtoViewPort(self, point:QPointF):
        point = self.chart_view.chart().mapToPosition(point)
        point_in_scene = self.chart_view.mapToScene(point.toPoint())
        point_viewport_position = self.chart_view.mapFromScene(point_in_scene)
        return point_viewport_position