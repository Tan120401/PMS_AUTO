# Form implementation generated from reading ui file 'Pms_ui.ui'
#
# Created by: PyQt6 UI code generator 6.8.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(540, 750)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        font.setBold(True)
        MainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.uninstallBtn = QtWidgets.QPushButton(parent=self.centralwidget)
        self.uninstallBtn.setGeometry(QtCore.QRect(40, 50, 101, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        self.uninstallBtn.setFont(font)
        self.uninstallBtn.setObjectName("uninstallBtn")
        self.installBtn = QtWidgets.QPushButton(parent=self.centralwidget)
        self.installBtn.setGeometry(QtCore.QRect(210, 50, 121, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        self.installBtn.setFont(font)
        self.installBtn.setObjectName("installBtn")
        self.stopBtn = QtWidgets.QPushButton(parent=self.centralwidget)
        self.stopBtn.setGeometry(QtCore.QRect(400, 50, 101, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        self.stopBtn.setFont(font)
        self.stopBtn.setObjectName("stopBtn")
        self.tableResult = QtWidgets.QTableView(parent=self.centralwidget)
        self.tableResult.setGeometry(QtCore.QRect(40, 140, 461, 581))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(False)
        self.tableResult.setFont(font)
        self.tableResult.setObjectName("tableResult")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "System Power Management Uninstall/ Install App"))
        self.uninstallBtn.setText(_translate("MainWindow", "UNINSTALL"))
        self.installBtn.setText(_translate("MainWindow", "INSTALL"))
        self.stopBtn.setText(_translate("MainWindow", "STOP"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
