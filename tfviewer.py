#import QFrame 
from PySide6.QtWidgets import QFrame
# import QApplication and sys
from PySide6.QtWidgets import QApplication
import sys
# import Grid Layout
from PySide6.QtWidgets import QGridLayout
# import QChart and QChartView
from PySide6.QtCharts import QChart, QChartView
# import QLineSeries
from PySide6.QtCharts import QLineSeries
# import QPen
from PySide6.QtGui import QPen
# import QValueAxis
from PySide6.QtCharts import QValueAxis 
# import QPainter
from PySide6.QtGui import QPainter
# import Qt
from PySide6.QtCore import Qt

# define QFrame Class to display the Frequency Response Data
class TFViewer(QFrame):
    #initialize the class
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        # generate data for the chart
        data = self.generateData()
        # add data to the chart
        self.addData(data)
        # update the style of the chart
        self.updateStyle()
        # make points draggable in the chart
        self.makeDraggable()
    #init UI of TFViewer
    def initUI(self):
        # add a grid layout
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        # Use QChart and QChartView to display the data
        self.chart = QChart()
        self.chartView = QChartView(self.chart)
        self.chartView.setRenderHint(QPainter.Antialiasing)
        self.grid.addWidget(self.chartView, 0, 0)
        # set the title of the chart
        self.chart.setTitle("Frequency Response")
        # set the x and y axis
        self.axisX = QValueAxis()
        self.axisX.setRange(0, 100)
        self.axisX.setTickCount(11)
        self.axisX.setLabelFormat("%.2f")
        self.axisX.setTitleText("Frequency (Hz)")
        self.chart.addAxis(self.axisX, Qt.AlignBottom)
        self.axisY = QValueAxis()
        self.axisY.setRange(-100, 100)
        self.axisY.setTickCount(11)
        self.axisY.setLabelFormat("%.2f")
        self.axisY.setTitleText("Amplitude (dB)")
        self.chart.addAxis(self.axisY, Qt.AlignLeft)
        # set the legend
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)
        # set the series
        self.series = QLineSeries()
        self.series.setName("Frequency Response")
        self.chart.addSeries(self.series)
        self.series.attachAxis(self.axisX)
        self.series.attachAxis(self.axisY)
        # set the pen
        self.pen = QPen()
        self.pen.setWidth(2)
        self.pen.setColor(Qt.black)
        self.series.setPen(self.pen)
        # set the grid
        self.chart.createDefaultAxes()
        self.chart.axes(Qt.Horizontal)[0].setGridLineVisible(True)
        self.chart.axes(Qt.Vertical)[0].setGridLineVisible(True)
        self.chartView.setChart(self.chart)
        self.chartView.setRenderHint(QPainter.Antialiasing)
        # set the size of the window
        self.resize(800, 600)
        self.setWindowTitle("Frequency Response Viewer")
        self.show()
    
    # add sample data to the chart
    def addData(self, data):
        self.series.clear()
        for i in range(len(data)):
            self.series.append(i, data[i])
        self.chartView.setChart(self.chart)
        self.chartView.setRenderHint(QPainter.Antialiasing)
        self.show()

    #generate the sample data for the chart
    def generateData(self):
        data = []
        for i in range(100):
            data.append(i)
        return data
  
    # update the style of the chart
    def updateStyle(self):
        self.series.setPointsVisible(True)
        self.series.setColor(Qt.red)
        # update series in the chart
        self.chartView.setChart(self.chart)
        self.chartView.setRenderHint(QPainter.Antialiasing)
        self.show()

    # enable the mode so that points can be draggable using mouse in the chart
    def makeDraggable(self):
        self.series.setPointsVisible(True)
        self.series.setPointLabelsVisible(True)
        self.series.setPointLabelsFormat("(@xPoint, @yPoint)")
        self.series.setPointLabelsColor(Qt.black)
        self.series.setPointLabelsFont(self.font())
        # update series in the chart
        self.chartView.setChart(self.chart)
        self.chartView.setRenderHint(QPainter.Antialiasing)
        self.show()

# main function
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TFViewer()
    sys.exit(app.exec())

