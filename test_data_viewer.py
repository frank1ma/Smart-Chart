from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QWidget
import numpy as np

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Frequency Response Viewer")
        self.table = QTableWidget()
        self.button = QPushButton("Update")
        self.revert_button = QPushButton("Revert")
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(self.button)
        layout.addWidget(self.revert_button)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.data = np.array([[10, 1+2j], [20, 2+3j], [30, 3+4j], [30, 3+4j], [30, 3+4j], [30, 3+4j], [30, 3+4j], [30, 3+4j], [30, 3+4j], [30, 3+4j], [30, 3+4j], [30, 3+4j], [30, 3+4j]])
        self.original_data = self.data.copy() 
        self.update_data(self.data)
        self.button.clicked.connect(self.on_button_clicked)
        self.revert_button.clicked.connect(self.on_revert_button_clicked)
    def update_data(self, data):
        num_rows, num_cols = data.shape
        self.table.setRowCount(num_rows)
        self.table.setColumnCount(num_cols)
        self.table.setHorizontalHeaderLabels(["Frequency", "Response"])
        for i in range(num_rows):
            frequency_item = QTableWidgetItem(f"{data[i,0]:.2f}")
            response_item = QTableWidgetItem(f"{data[i,1].real:.2f}+{data[i,1].imag:.2f}j")
            self.table.setItem(i, 0, frequency_item)
            self.table.setItem(i, 1, response_item)

    def on_button_clicked(self):
        for i in range(self.table.rowCount()):
            frequency_item = self.table.item(i, 0)
            response_item = self.table.item(i, 1)
            frequency = float(frequency_item.text())
            response_str = response_item.text()
            response = complex(response_str)
            self.data[i, 0] = frequency
            self.data[i, 1] = response

    def on_revert_button_clicked(self):
        self.update_data(self.original_data)
        self.data = self.original_data.copy()

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
