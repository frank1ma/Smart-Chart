# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'chart_optionsOqjXjY.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QComboBox,
    QDialog, QDialogButtonBox, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QScrollBar,
    QSizePolicy, QSpacerItem, QSpinBox, QTabWidget,
    QWidget)

class Ui_chart_options(object):
    def setupUi(self, chart_options):
        if not chart_options.objectName():
            chart_options.setObjectName(u"chart_options")
        chart_options.resize(546, 409)
        self.gridLayout = QGridLayout(chart_options)
        self.gridLayout.setObjectName(u"gridLayout")
        self.chart_options_tab = QTabWidget(chart_options)
        self.chart_options_tab.setObjectName(u"chart_options_tab")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.gridLayout_3 = QGridLayout(self.tab)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.groupBox_2 = QGroupBox(self.tab)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout_5 = QGridLayout(self.groupBox_2)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.checkBox_subchart_sync_x_axis = QCheckBox(self.groupBox_2)
        self.checkBox_subchart_sync_x_axis.setObjectName(u"checkBox_subchart_sync_x_axis")

        self.gridLayout_5.addWidget(self.checkBox_subchart_sync_x_axis, 0, 0, 1, 1)

        self.checkBox_subchart_sync_y_axis = QCheckBox(self.groupBox_2)
        self.checkBox_subchart_sync_y_axis.setObjectName(u"checkBox_subchart_sync_y_axis")

        self.gridLayout_5.addWidget(self.checkBox_subchart_sync_y_axis, 1, 0, 1, 1)


        self.gridLayout_3.addWidget(self.groupBox_2, 2, 0, 1, 1)

        self.groupBox = QGroupBox(self.tab)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setMaximumSize(QSize(16777215, 100))
        self.gridLayout_4 = QGridLayout(self.groupBox)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_4.addItem(self.verticalSpacer_2, 2, 0, 1, 3)

        self.label_13 = QLabel(self.groupBox)
        self.label_13.setObjectName(u"label_13")

        self.gridLayout_4.addWidget(self.label_13, 1, 0, 1, 1)

        self.label_pan_x = QLabel(self.groupBox)
        self.label_pan_x.setObjectName(u"label_pan_x")

        self.gridLayout_4.addWidget(self.label_pan_x, 0, 1, 1, 1)

        self.pushButton = QPushButton(self.groupBox)
        self.pushButton.setObjectName(u"pushButton")

        self.gridLayout_4.addWidget(self.pushButton, 1, 3, 1, 1)

        self.label_pan_y = QLabel(self.groupBox)
        self.label_pan_y.setObjectName(u"label_pan_y")

        self.gridLayout_4.addWidget(self.label_pan_y, 0, 2, 1, 1)

        self.horizontalScrollBar_x = QScrollBar(self.groupBox)
        self.horizontalScrollBar_x.setObjectName(u"horizontalScrollBar_x")
        self.horizontalScrollBar_x.setMaximum(100)
        self.horizontalScrollBar_x.setPageStep(1)
        self.horizontalScrollBar_x.setOrientation(Qt.Horizontal)

        self.gridLayout_4.addWidget(self.horizontalScrollBar_x, 1, 1, 1, 1)

        self.horizontalScrollBar_y = QScrollBar(self.groupBox)
        self.horizontalScrollBar_y.setObjectName(u"horizontalScrollBar_y")
        self.horizontalScrollBar_y.setMaximum(100)
        self.horizontalScrollBar_y.setPageStep(1)
        self.horizontalScrollBar_y.setOrientation(Qt.Horizontal)

        self.gridLayout_4.addWidget(self.horizontalScrollBar_y, 1, 2, 1, 1)


        self.gridLayout_3.addWidget(self.groupBox, 1, 0, 1, 1)

        self.groupBox_3 = QGroupBox(self.tab)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.gridLayout_6 = QGridLayout(self.groupBox_3)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.spinBox_point_maker_size = QSpinBox(self.groupBox_3)
        self.spinBox_point_maker_size.setObjectName(u"spinBox_point_maker_size")
        self.spinBox_point_maker_size.setMinimum(1)
        self.spinBox_point_maker_size.setMaximum(20)

        self.gridLayout_6.addWidget(self.spinBox_point_maker_size, 0, 2, 1, 1)

        self.label_14 = QLabel(self.groupBox_3)
        self.label_14.setObjectName(u"label_14")

        self.gridLayout_6.addWidget(self.label_14, 0, 1, 1, 1)


        self.gridLayout_3.addWidget(self.groupBox_3, 0, 0, 1, 1)

        self.chart_options_tab.addTab(self.tab, "")
        self.tab_axes = QWidget()
        self.tab_axes.setObjectName(u"tab_axes")
        self.gridLayout_2 = QGridLayout(self.tab_axes)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.lineEdit_y_label = QLineEdit(self.tab_axes)
        self.lineEdit_y_label.setObjectName(u"lineEdit_y_label")

        self.gridLayout_2.addWidget(self.lineEdit_y_label, 9, 1, 1, 1)

        self.comboBox_y_scale = QComboBox(self.tab_axes)
        self.comboBox_y_scale.addItem("")
        self.comboBox_y_scale.addItem("")
        self.comboBox_y_scale.addItem("")
        self.comboBox_y_scale.setObjectName(u"comboBox_y_scale")

        self.gridLayout_2.addWidget(self.comboBox_y_scale, 10, 1, 1, 1)

        self.lineEdit_x_max = QLineEdit(self.tab_axes)
        self.lineEdit_x_max.setObjectName(u"lineEdit_x_max")

        self.gridLayout_2.addWidget(self.lineEdit_x_max, 3, 1, 1, 2)

        self.label_9 = QLabel(self.tab_axes)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setMinimumSize(QSize(200, 0))
        self.label_9.setMaximumSize(QSize(200, 16777215))

        self.gridLayout_2.addWidget(self.label_9, 8, 0, 1, 1)

        self.label_5 = QLabel(self.tab_axes)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMinimumSize(QSize(200, 0))
        self.label_5.setMaximumSize(QSize(200, 16777215))

        self.gridLayout_2.addWidget(self.label_5, 3, 0, 1, 1)

        self.label_7 = QLabel(self.tab_axes)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setMinimumSize(QSize(200, 0))
        self.label_7.setMaximumSize(QSize(200, 16777215))
        self.label_7.setTextFormat(Qt.RichText)

        self.gridLayout_2.addWidget(self.label_7, 6, 0, 1, 1)

        self.lineEdit_y_min = QLineEdit(self.tab_axes)
        self.lineEdit_y_min.setObjectName(u"lineEdit_y_min")

        self.gridLayout_2.addWidget(self.lineEdit_y_min, 7, 1, 1, 1)

        self.lineEdit_x_min = QLineEdit(self.tab_axes)
        self.lineEdit_x_min.setObjectName(u"lineEdit_x_min")

        self.gridLayout_2.addWidget(self.lineEdit_x_min, 2, 1, 1, 2)

        self.lineEdit_title = QLineEdit(self.tab_axes)
        self.lineEdit_title.setObjectName(u"lineEdit_title")
        self.lineEdit_title.setFocusPolicy(Qt.StrongFocus)

        self.gridLayout_2.addWidget(self.lineEdit_title, 0, 1, 1, 2)

        self.label_6 = QLabel(self.tab_axes)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setMinimumSize(QSize(200, 0))
        self.label_6.setMaximumSize(QSize(200, 16777215))

        self.gridLayout_2.addWidget(self.label_6, 2, 0, 1, 1)

        self.lineEdit_y_max = QLineEdit(self.tab_axes)
        self.lineEdit_y_max.setObjectName(u"lineEdit_y_max")

        self.gridLayout_2.addWidget(self.lineEdit_y_max, 8, 1, 1, 1)

        self.label_3 = QLabel(self.tab_axes)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMinimumSize(QSize(200, 0))
        self.label_3.setMaximumSize(QSize(200, 16777215))

        self.gridLayout_2.addWidget(self.label_3, 4, 0, 1, 1)

        self.lineEdit_x_label = QLineEdit(self.tab_axes)
        self.lineEdit_x_label.setObjectName(u"lineEdit_x_label")

        self.gridLayout_2.addWidget(self.lineEdit_x_label, 4, 1, 1, 2)

        self.label_4 = QLabel(self.tab_axes)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setMinimumSize(QSize(200, 0))
        self.label_4.setMaximumSize(QSize(200, 16777215))

        self.gridLayout_2.addWidget(self.label_4, 5, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer, 12, 0, 1, 1)

        self.label_8 = QLabel(self.tab_axes)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setMinimumSize(QSize(200, 0))
        self.label_8.setMaximumSize(QSize(200, 16777215))

        self.gridLayout_2.addWidget(self.label_8, 7, 0, 1, 1)

        self.label_2 = QLabel(self.tab_axes)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(200, 0))
        self.label_2.setMaximumSize(QSize(200, 16777215))
        self.label_2.setStyleSheet(u"")

        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)

        self.comboBox_x_scale = QComboBox(self.tab_axes)
        self.comboBox_x_scale.addItem("")
        self.comboBox_x_scale.addItem("")
        self.comboBox_x_scale.addItem("")
        self.comboBox_x_scale.setObjectName(u"comboBox_x_scale")

        self.gridLayout_2.addWidget(self.comboBox_x_scale, 5, 1, 1, 2)

        self.label_10 = QLabel(self.tab_axes)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setMinimumSize(QSize(200, 0))
        self.label_10.setMaximumSize(QSize(200, 16777215))

        self.gridLayout_2.addWidget(self.label_10, 9, 0, 1, 1)

        self.label_11 = QLabel(self.tab_axes)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setMinimumSize(QSize(200, 0))
        self.label_11.setMaximumSize(QSize(200, 16777215))

        self.gridLayout_2.addWidget(self.label_11, 10, 0, 1, 1)

        self.label = QLabel(self.tab_axes)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(200, 0))
        self.label.setMaximumSize(QSize(200, 16777215))

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.label_12 = QLabel(self.tab_axes)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setMinimumSize(QSize(200, 0))
        self.label_12.setMaximumSize(QSize(200, 16777215))
        self.label_12.setTextFormat(Qt.RichText)

        self.gridLayout_2.addWidget(self.label_12, 11, 0, 1, 1)

        self.checkBox_legend_on = QCheckBox(self.tab_axes)
        self.checkBox_legend_on.setObjectName(u"checkBox_legend_on")

        self.gridLayout_2.addWidget(self.checkBox_legend_on, 11, 1, 1, 1)

        self.chart_options_tab.addTab(self.tab_axes, "")

        self.gridLayout.addWidget(self.chart_options_tab, 0, 0, 2, 2)

        self.buttonBox = QDialogButtonBox(chart_options)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Apply|QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)


        self.retranslateUi(chart_options)
        self.buttonBox.accepted.connect(chart_options.accept)
        self.buttonBox.rejected.connect(chart_options.reject)

        self.chart_options_tab.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(chart_options)
    # setupUi

    def retranslateUi(self, chart_options):
        chart_options.setWindowTitle(QCoreApplication.translate("chart_options", u"Dialog", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("chart_options", u"SubChart", None))
        self.checkBox_subchart_sync_x_axis.setText(QCoreApplication.translate("chart_options", u"Sync X axis to Main Chart", None))
        self.checkBox_subchart_sync_y_axis.setText(QCoreApplication.translate("chart_options", u"Sync Y axis to Main Chart", None))
        self.groupBox.setTitle(QCoreApplication.translate("chart_options", u"Pan", None))
        self.label_13.setText(QCoreApplication.translate("chart_options", u"Pan Sensitivity", None))
        self.label_pan_x.setText(QCoreApplication.translate("chart_options", u"X:", None))
        self.pushButton.setText(QCoreApplication.translate("chart_options", u"Reset", None))
        self.label_pan_y.setText(QCoreApplication.translate("chart_options", u"Y:", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("chart_options", u"General", None))
        self.label_14.setText(QCoreApplication.translate("chart_options", u"Intersection Point Marker Size", None))
        self.chart_options_tab.setTabText(self.chart_options_tab.indexOf(self.tab), QCoreApplication.translate("chart_options", u"Global setting", None))
        self.comboBox_y_scale.setItemText(0, QCoreApplication.translate("chart_options", u"linear", None))
        self.comboBox_y_scale.setItemText(1, QCoreApplication.translate("chart_options", u"log", None))
        self.comboBox_y_scale.setItemText(2, QCoreApplication.translate("chart_options", u"symlog", None))

        self.label_9.setText(QCoreApplication.translate("chart_options", u"Max", None))
        self.label_5.setText(QCoreApplication.translate("chart_options", u"Max", None))
        self.label_7.setText(QCoreApplication.translate("chart_options", u"<html><head/><body><p><span style=\" font-weight:700;\">Y-Axis</span></p></body></html>", None))
        self.label_6.setText(QCoreApplication.translate("chart_options", u"Min", None))
        self.label_3.setText(QCoreApplication.translate("chart_options", u"Label", None))
        self.label_4.setText(QCoreApplication.translate("chart_options", u"Scale", None))
        self.label_8.setText(QCoreApplication.translate("chart_options", u"Min", None))
        self.label_2.setText(QCoreApplication.translate("chart_options", u"<html><head/><body><p><span style=\" font-weight:700;\">X-Axis</span></p></body></html>", None))
        self.comboBox_x_scale.setItemText(0, QCoreApplication.translate("chart_options", u"linear", None))
        self.comboBox_x_scale.setItemText(1, QCoreApplication.translate("chart_options", u"log", None))
        self.comboBox_x_scale.setItemText(2, QCoreApplication.translate("chart_options", u"symlog", None))

        self.label_10.setText(QCoreApplication.translate("chart_options", u"Label", None))
        self.label_11.setText(QCoreApplication.translate("chart_options", u"Scale", None))
        self.label.setText(QCoreApplication.translate("chart_options", u"Title", None))
        self.label_12.setText(QCoreApplication.translate("chart_options", u"<html><head/><body><p><span style=\" font-weight:700;\">Legend</span></p></body></html>", None))
        self.checkBox_legend_on.setText(QCoreApplication.translate("chart_options", u"on", None))
        self.chart_options_tab.setTabText(self.chart_options_tab.indexOf(self.tab_axes), QCoreApplication.translate("chart_options", u"Axes setting", None))
    # retranslateUi

