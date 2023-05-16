import matplotlib.pyplot as plt
import numpy as np
from PySide6.QtWidgets import QVBoxLayout,QWidget
# create a main window widget
from PySide6.QtWidgets import QMainWindow,QApplication,QGridLayout,QPushButton,QDialog,QLineEdit
from smart_chart.plot_navigator.ui_chart_options import Ui_chart_options
# create the main window and run it
import sys
app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)
window = QMainWindow()
window.setWindowTitle("Smart Chart")
window.resize(800, 600)
# Add the custom frame to the main window
custom_frame = QWidget()
layout = QGridLayout(custom_frame)
layout.addWidget(QLineEdit(),0,0,1,1)
custom_frame.setLayout(layout)
window.setCentralWidget(custom_frame)   
# Diag = QDialog()
# ui = Ui_chart_options()
# ui.setupUi(Diag)
# Diag.show()
window.show()
app.exec()
