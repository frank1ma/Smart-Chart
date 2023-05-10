from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication,QMainWindow,QVBoxLayout,QListWidget,QFrame
from PySide6.QtCharts import QChart, QChartView,QLineSeries
from PySide6.QtCore import QObject, QEvent

class Navigator(QFrame):
    def __init__(self, chart_view, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chart_view = chart_view
        self.chart_view.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.chart_view:
            if event.type() == QEvent.Type.MouseButtonPress:
                print("good")
                return True
            if event.type()==QEvent.Type.MouseButtonRelease:
                print("release")
                return True
        return super().eventFilter(obj, event)

    def mousePressEvent(self, event):
        print("Navigator mousePressEvent")
        # Add your implementation here


if __name__ == "__main__":
    app = QApplication([])

    # add a main window
    window = QMainWindow()
    # add layout to the main window
    layout = QVBoxLayout()

    chart = QChart()
    chart.setTitle("My Chart")
    series = QLineSeries()
    series.append(0, 6)
    series.append(2, 4)
    chart.addSeries(series)
    chart_view = QChartView(chart,window)
    # Create the Navigator instance and pass the QChartView instance to it
    navigator = Navigator(chart_view)
    # add QChartView to the layout
    layout.addWidget(chart_view)
    # add layout to the main window
    window.setLayout(layout)
    window.show()
    app.exec()
