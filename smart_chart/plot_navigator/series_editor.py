from PySide6.QtWidgets import (QSizePolicy,QSpacerItem,QDialog, QCheckBox,QPushButton, 
                               QVBoxLayout, QDialogButtonBox, QWidget, QScrollArea, 
                               QGridLayout, QLabel, QHBoxLayout)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor

class SeriesEditor(QDialog):
    def __init__(self, parent=None, data_label="Series"):
        super().__init__(parent)
        self.data_label = data_label
        self.setWindowTitle(f"{self.data_label} Editor")
        self.resize(400, 300)
        self.setModal(True)
        self.initUI()

    def initUI(self):
        self.vertical_layout = QVBoxLayout()
        self.setLayout(self.vertical_layout)
        self.vertical_layout.addWidget(QLabel(f"Select {self.data_label} to show:"))
        # Add scroll area for checkboxes
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.vertical_layout.addWidget(self.scroll_area)
        
        self.scroll_widget = QWidget()
        self.scroll_area.setWidget(self.scroll_widget)
        
        self.scroll_layout = QVBoxLayout()
        self.scroll_widget.setLayout(self.scroll_layout)

        # Checkboxes
        self.checkboxes = {}
        
        for series in self.parent().main_chart_view.series_dict.values():
            # Create a horizontal layout for each checkbox and its legend
            hbox_layout = QHBoxLayout()
            
            checkbox = QCheckBox(series.name())
            checkbox.setChecked(series.isVisible())
            self.checkboxes[series.id] = checkbox
            
            # Create a label for the legend. Replace 'series.legend' with actual legend text or image
            legend_label = QLabel()
            legend_label.setStyleSheet("background-color: " + series.pen().color().name())
            legend_label.setFixedSize(20, 20)
            
            hbox_layout.addWidget(checkbox)
            hbox_layout.addWidget(legend_label)
            
            self.scroll_layout.addLayout(hbox_layout)
        # add vertical spacer to bottom of scroll area to push checkboxes to top
        self.scroll_layout.addStretch(1)

        # add a button to output the selected series to csv file
        self.export_button = QPushButton("Export to CSV")
        # add the button to the layout
        self.vertical_layout.addWidget(self.export_button)
        # send the list of ids of series to show to the parent
        self.export_button.clicked.connect(lambda: self.parent().saveSeriesToCSV(self.get_series_to_show()))
        
        # Dialog buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.vertical_layout.addWidget(self.button_box)

    def get_series_to_show(self):
        series_to_show = []
        for id, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                series_to_show.append(id)
        return series_to_show
