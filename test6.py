from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QKeySequence,QShortcut,QAction
from PySide6.QtCore import Qt  

app = QApplication([])

# Create a QMainWindow
window = QMainWindow()

# Create a QAction
action = QAction("My Action", window)

# Define the action's triggered slot
def on_action_triggered():
    print("Action triggered!")

# Connect the QAction's triggered signal to the slot
action.triggered.connect(on_action_triggered)

# Create a QShortcut for the "p+p" shortcut
shortcut = QShortcut(QKeySequence("ctrl+shift+p"), window)
# Connect the QShortcut's activated signal to the QAction's trigger slot
shortcut.activated.connect(action.trigger)

# Add the QAction to the QMainWindow's menu bar or toolbar
window.addAction(action)

window.show()

app.exec()
from PySide6.QtWidgets import QApplication, QMainWindow, QAction, QShortcut
from PySide6.QtGui import QKeySequence

app = QApplication([])

# Create a QMainWindow
window = QMainWindow()

# Create a QAction
action = QAction("My Action", window)

# Define the action's triggered slot
def on_action_triggered():
    print("Action triggered!")

# Connect the QAction's triggered signal to the slot
action.triggered.connect(on_action_triggered)

# Create a QShortcut for the "p+p" shortcut
shortcut = QShortcut(QKeySequence("p+p"), window)
# Connect the QShortcut's activated signal to the QAction's trigger slot
shortcut.activated.connect(action.trigger)

# Add the QAction to the QMainWindow's menu bar or toolbar
window.addAction(action)

window.show()

app.exec()
