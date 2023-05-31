# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'plot_navigatorIAAWER.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QSizePolicy, QWidget)

from .custom_tool_button import CustomToolButton
import plot_navigator_rc

class Ui_plot_navigator(object):
    def setupUi(self, plot_navigator):
        if not plot_navigator.objectName():
            plot_navigator.setObjectName(u"plot_navigator")
        plot_navigator.resize(416, 50)
        plot_navigator.setMinimumSize(QSize(400, 50))
        plot_navigator.setMaximumSize(QSize(800, 50))
        self.horizontalLayout = QHBoxLayout(plot_navigator)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.origin_view_button = CustomToolButton(plot_navigator)
        self.origin_view_button.setObjectName(u"origin_view_button")
        self.origin_view_button.setMaximumSize(QSize(36, 16777215))
        icon = QIcon()
        icon.addFile(u":/navigator/home-60.png", QSize(), QIcon.Normal, QIcon.Off)
        self.origin_view_button.setIcon(icon)
        self.origin_view_button.setIconSize(QSize(24, 24))

        self.horizontalLayout.addWidget(self.origin_view_button)

        self.vertical_marker_button = CustomToolButton(plot_navigator)
        self.vertical_marker_button.setObjectName(u"vertical_marker_button")
        self.vertical_marker_button.setMaximumSize(QSize(36, 16777215))
        icon1 = QIcon()
        icon1.addFile(u":/navigator/vertical-line-60.png", QSize(), QIcon.Normal, QIcon.Off)
        self.vertical_marker_button.setIcon(icon1)
        self.vertical_marker_button.setIconSize(QSize(24, 24))

        self.horizontalLayout.addWidget(self.vertical_marker_button)

        self.measure_button = CustomToolButton(plot_navigator)
        self.measure_button.setObjectName(u"measure_button")
        self.measure_button.setMaximumSize(QSize(36, 16777215))
        icon2 = QIcon()
        icon2.addFile(u":/navigator/ruler-60.png", QSize(), QIcon.Normal, QIcon.Off)
        self.measure_button.setIcon(icon2)
        self.measure_button.setIconSize(QSize(24, 24))

        self.horizontalLayout.addWidget(self.measure_button)

        self.pan_view_button = CustomToolButton(plot_navigator)
        self.pan_view_button.setObjectName(u"pan_view_button")
        self.pan_view_button.setMaximumSize(QSize(36, 16777215))
        icon3 = QIcon()
        icon3.addFile(u":/navigator/drag-60.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pan_view_button.setIcon(icon3)
        self.pan_view_button.setIconSize(QSize(24, 24))

        self.horizontalLayout.addWidget(self.pan_view_button)

        self.zoom_button = CustomToolButton(plot_navigator)
        self.zoom_button.setObjectName(u"zoom_button")
        self.zoom_button.setMaximumSize(QSize(36, 16777215))
        icon4 = QIcon()
        icon4.addFile(u":/navigator/search-60.png", QSize(), QIcon.Normal, QIcon.Off)
        self.zoom_button.setIcon(icon4)
        self.zoom_button.setIconSize(QSize(24, 24))

        self.horizontalLayout.addWidget(self.zoom_button)

        self.series_editor_button = CustomToolButton(plot_navigator)
        self.series_editor_button.setObjectName(u"series_editor_button")
        self.series_editor_button.setMaximumSize(QSize(36, 16777215))
        icon5 = QIcon()
        icon5.addFile(u":/navigator/edit-60.png", QSize(), QIcon.Normal, QIcon.Off)
        self.series_editor_button.setIcon(icon5)
        self.series_editor_button.setIconSize(QSize(24, 24))

        self.horizontalLayout.addWidget(self.series_editor_button)

        self.setting_button = CustomToolButton(plot_navigator)
        self.setting_button.setObjectName(u"setting_button")
        self.setting_button.setMaximumSize(QSize(36, 16777215))
        icon6 = QIcon()
        icon6.addFile(u":/navigator/adjust-60.png", QSize(), QIcon.Normal, QIcon.Off)
        self.setting_button.setIcon(icon6)
        self.setting_button.setIconSize(QSize(24, 24))

        self.horizontalLayout.addWidget(self.setting_button)

        self.save_button = CustomToolButton(plot_navigator)
        self.save_button.setObjectName(u"save_button")
        self.save_button.setMaximumSize(QSize(36, 16777215))
        icon7 = QIcon()
        icon7.addFile(u":/navigator/save-60.png", QSize(), QIcon.Normal, QIcon.Off)
        self.save_button.setIcon(icon7)
        self.save_button.setIconSize(QSize(24, 24))

        self.horizontalLayout.addWidget(self.save_button)

        self.position_label = QLabel(plot_navigator)
        self.position_label.setObjectName(u"position_label")

        self.horizontalLayout.addWidget(self.position_label)

        self.msg_label = QLabel(plot_navigator)
        self.msg_label.setObjectName(u"msg_label")

        self.horizontalLayout.addWidget(self.msg_label)


        self.retranslateUi(plot_navigator)

        QMetaObject.connectSlotsByName(plot_navigator)
    # setupUi

    def retranslateUi(self, plot_navigator):
        plot_navigator.setWindowTitle(QCoreApplication.translate("plot_navigator", u"Frame", None))
        self.origin_view_button.setText(QCoreApplication.translate("plot_navigator", u"...", None))
        self.vertical_marker_button.setText(QCoreApplication.translate("plot_navigator", u"...", None))
        self.measure_button.setText(QCoreApplication.translate("plot_navigator", u"...", None))
        self.series_editor_button.setText(QCoreApplication.translate("plot_navigator", u"...", None))
        self.position_label.setText("")
        self.msg_label.setText("")
    # retranslateUi

