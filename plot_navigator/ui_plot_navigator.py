# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'plot_navigatorviXRWR.ui'
##
## Created by: Qt User Interface Compiler version 6.5.0
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QPushButton,
    QSizePolicy, QWidget)
from plot_navigator.icon import plot_navigator_rc

class Ui_plot_navigator(object):
    def setupUi(self, plot_navigator):
        if not plot_navigator.objectName():
            plot_navigator.setObjectName(u"plot_navigator")
        plot_navigator.resize(306, 50)
        plot_navigator.setMinimumSize(QSize(306, 50))
        plot_navigator.setMaximumSize(QSize(306, 50))
        self.horizontalLayout = QHBoxLayout(plot_navigator)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.origin_view_button = QPushButton(plot_navigator)
        self.origin_view_button.setObjectName(u"origin_view_button")
        self.origin_view_button.setMaximumSize(QSize(36, 16777215))
        icon = QIcon()
        icon.addFile(u":/navigator/home-60.png", QSize(), QIcon.Normal, QIcon.Off)
        self.origin_view_button.setIcon(icon)
        self.origin_view_button.setIconSize(QSize(24, 24))

        self.horizontalLayout.addWidget(self.origin_view_button)

        self.prev_view_button = QPushButton(plot_navigator)
        self.prev_view_button.setObjectName(u"prev_view_button")
        self.prev_view_button.setMaximumSize(QSize(36, 16777215))
        icon1 = QIcon()
        icon1.addFile(u":/navigator/arrow-left-60.png", QSize(), QIcon.Normal, QIcon.Off)
        self.prev_view_button.setIcon(icon1)
        self.prev_view_button.setIconSize(QSize(24, 24))

        self.horizontalLayout.addWidget(self.prev_view_button)

        self.after_view_button = QPushButton(plot_navigator)
        self.after_view_button.setObjectName(u"after_view_button")
        self.after_view_button.setMaximumSize(QSize(36, 16777215))
        icon2 = QIcon()
        icon2.addFile(u":/navigator/arrow-right-60.png", QSize(), QIcon.Normal, QIcon.Off)
        self.after_view_button.setIcon(icon2)
        self.after_view_button.setIconSize(QSize(24, 24))

        self.horizontalLayout.addWidget(self.after_view_button)

        self.pan_view_button = QPushButton(plot_navigator)
        self.pan_view_button.setObjectName(u"pan_view_button")
        self.pan_view_button.setMaximumSize(QSize(36, 16777215))
        icon3 = QIcon()
        icon3.addFile(u":/navigator/drag-60.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pan_view_button.setIcon(icon3)
        self.pan_view_button.setIconSize(QSize(24, 24))

        self.horizontalLayout.addWidget(self.pan_view_button)

        self.zoom_button = QPushButton(plot_navigator)
        self.zoom_button.setObjectName(u"zoom_button")
        self.zoom_button.setMaximumSize(QSize(36, 16777215))
        icon4 = QIcon()
        icon4.addFile(u":/navigator/search-60.png", QSize(), QIcon.Normal, QIcon.Off)
        self.zoom_button.setIcon(icon4)
        self.zoom_button.setIconSize(QSize(24, 24))

        self.horizontalLayout.addWidget(self.zoom_button)

        self.setting__button = QPushButton(plot_navigator)
        self.setting__button.setObjectName(u"setting__button")
        self.setting__button.setMaximumSize(QSize(36, 16777215))
        icon5 = QIcon()
        icon5.addFile(u":/navigator/adjust-60.png", QSize(), QIcon.Normal, QIcon.Off)
        self.setting__button.setIcon(icon5)
        self.setting__button.setIconSize(QSize(24, 24))

        self.horizontalLayout.addWidget(self.setting__button)

        self.save_button = QPushButton(plot_navigator)
        self.save_button.setObjectName(u"save_button")
        self.save_button.setMaximumSize(QSize(36, 16777215))
        icon6 = QIcon()
        icon6.addFile(u":/navigator/save-60.png", QSize(), QIcon.Normal, QIcon.Off)
        self.save_button.setIcon(icon6)
        self.save_button.setIconSize(QSize(24, 24))

        self.horizontalLayout.addWidget(self.save_button)


        self.retranslateUi(plot_navigator)

        QMetaObject.connectSlotsByName(plot_navigator)
    # setupUi

    def retranslateUi(self, plot_navigator):
        plot_navigator.setWindowTitle(QCoreApplication.translate("plot_navigator", u"Frame", None))
    # retranslateUi

