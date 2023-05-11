from PySide6.QtWidgets import QApplication, QMainWindow, QToolButton, QMenu, QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QMouseEvent

class CustomToolButton(QToolButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(False)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            # Check if the click is in the right-bottom area of the button
            if event.position().x() > self.width() * 0.55 and event.position().y() > self.height() * 0.55:
                self.showMenu()
            else:
                # Toggle the checkable state
                self.setChecked(not self.isChecked())
                self.clicked.emit()

