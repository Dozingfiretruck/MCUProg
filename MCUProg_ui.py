# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MCUProg.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
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
from PySide6.QtWidgets import (QApplication, QComboBox, QLabel, QLineEdit,
    QMainWindow, QProgressBar, QPushButton, QSizePolicy,
    QStatusBar, QWidget)

from MCUProg_custom import QComboBox2

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(480, 320)
        MainWindow.setCursor(QCursor(Qt.ArrowCursor))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.file_selection_button = QPushButton(self.centralwidget)
        self.file_selection_button.setObjectName(u"file_selection_button")
        self.file_selection_button.setGeometry(QRect(360, 100, 81, 23))
        self.file_lineEdit = QLineEdit(self.centralwidget)
        self.file_lineEdit.setObjectName(u"file_lineEdit")
        self.file_lineEdit.setGeometry(QRect(80, 100, 261, 21))
        self.flash_button = QPushButton(self.centralwidget)
        self.flash_button.setObjectName(u"flash_button")
        self.flash_button.setGeometry(QRect(364, 140, 71, 23))
        self.usb_comboBox = QComboBox2(self.centralwidget)
        self.usb_comboBox.setObjectName(u"usb_comboBox")
        self.usb_comboBox.setGeometry(QRect(80, 60, 261, 22))
        self.usb_connect_button = QPushButton(self.centralwidget)
        self.usb_connect_button.setObjectName(u"usb_connect_button")
        self.usb_connect_button.setGeometry(QRect(360, 60, 81, 23))
        self.targets_comboBox = QComboBox(self.centralwidget)
        self.targets_comboBox.setObjectName(u"targets_comboBox")
        self.targets_comboBox.setGeometry(QRect(80, 20, 161, 22))
        self.target_label = QLabel(self.centralwidget)
        self.target_label.setObjectName(u"target_label")
        self.target_label.setGeometry(QRect(20, 20, 53, 15))
        self.downloard_label = QLabel(self.centralwidget)
        self.downloard_label.setObjectName(u"downloard_label")
        self.downloard_label.setGeometry(QRect(20, 60, 53, 15))
        self.file_label = QLabel(self.centralwidget)
        self.file_label.setObjectName(u"file_label")
        self.file_label.setGeometry(QRect(20, 100, 53, 15))
        self.speed_comboBox = QComboBox(self.centralwidget)
        self.speed_comboBox.setObjectName(u"speed_comboBox")
        self.speed_comboBox.setGeometry(QRect(320, 20, 111, 22))
        self.speed_label = QLabel(self.centralwidget)
        self.speed_label.setObjectName(u"speed_label")
        self.speed_label.setGeometry(QRect(260, 20, 53, 15))
        self.flash_progressBar = QProgressBar(self.centralwidget)
        self.flash_progressBar.setObjectName(u"flash_progressBar")
        self.flash_progressBar.setGeometry(QRect(20, 140, 331, 23))
        self.flash_progressBar.setValue(0)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.file_selection_button.setText(QCoreApplication.translate("MainWindow", u"\u9009\u62e9\u4e0b\u8f7d\u56fa\u4ef6", None))
        self.flash_button.setText(QCoreApplication.translate("MainWindow", u"\u70e7\u5f55", None))
        self.usb_connect_button.setText(QCoreApplication.translate("MainWindow", u"\u8fde\u63a5", None))
        self.target_label.setText(QCoreApplication.translate("MainWindow", u"\u76ee\u6807\u82af\u7247", None))
        self.downloard_label.setText(QCoreApplication.translate("MainWindow", u"\u4e0b\u8f7d\u5668", None))
        self.file_label.setText(QCoreApplication.translate("MainWindow", u"\u4e0b\u8f7d\u56fa\u4ef6", None))
        self.speed_label.setText(QCoreApplication.translate("MainWindow", u"\u4e0b\u8f7d\u901f\u5ea6", None))
    # retranslateUi

