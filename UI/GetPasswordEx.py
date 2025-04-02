from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.QtGui import QPixmap
from PyQt6 import QtGui
from Connectors.Connector import Connector

from UI.GetPassword import Ui_MainWindow

class GetPasswordEx(Ui_MainWindow):
    def __init__(self):
        self.connector = Connector()

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow

        # Set images
        self.lblLogo.setPixmap(QPixmap("/Users/macbook/Documents/Uni/NĂM_3/HK6/KTLT/Project/images/ic_agoda.png"))
        self.lblPass.setPixmap(QPixmap("/Users/macbook/Documents/Uni/NĂM_3/HK6/KTLT/Project/images/ic_lock.png"))
        self.lblConfirm.setPixmap(QPixmap("/Users/macbook/Documents/Uni/NĂM_3/HK6/KTLT/Project/images/ic_lock.png"))
        self.lblEmail.setPixmap(QPixmap("/Users/macbook/Documents/Uni/NĂM_3/HK6/KTLT/Project/images/ic_email.png"))
        self.lblPhone.setPixmap(QPixmap("/Users/macbook/Documents/Uni/NĂM_3/HK6/KTLT/Project/images/ic_phone.png"))

        font = QtGui.QFont()
        font.setBold(True)
        self.btnSave.setFont(font)
        self.btnChange.setFont(font)

        self.btnLogin.clicked.connect(self.processLogin)
        self.btnRegis.clicked.connect(self.processRegister)
        self.btnExit.clicked.connect(self.processExit)
        self.btnSave.clicked.connect(self.processSave)
        self.btnChange.clicked.connect(self.processChange)

    def connectDatabase(self):
        self.connector.server = "localhost"
        self.connector.port = 3306
        self.connector.database = "KTLT"
        self.connector.username = "root"
        self.connector.password = ""
        self.connector.connect()

    def processChange(self):
        self.email = self.txtEmail.text()
        self.phone = self.txtPhone.text()
        if (self.email == '') or (self.phone == ''):
            msg = QMessageBox()
            msg.setText("You need to fill enough information")
            msg.exec()
        elif len(self.phone) != 10:
            msg = QMessageBox()
            msg.setText('Phone number need to have exactly 10 digits')
            msg.exec()
        else:
            self.connectDatabase()
            sql = "SELECT PhoneNumber, Email FROM USERAPP WHERE phonenumber = '%s' and email = '%s'" %(self.phone, self.email)
            df = self.connector.queryData(sql)
            if df.empty:
                msg = QMessageBox()
                msg.setText("Incorrect Phone or Email")
                msg.exec()
            else:
                self.txtPass.setPlaceholderText("Enter Your New Password")
                self.txtConfirm.setPlaceholderText("Confirm Your New Password")
                self.txtPass.setReadOnly(False)
                self.txtConfirm.setReadOnly(False)

    def processSave(self):
        password = self.txtPass.text()
        password2 = self.txtConfirm.text()
        if (password2 == '') or (password == ''):
            msg = QMessageBox()
            msg.setText("You need to fill enough information")
            msg.exec()
        elif password != password2:
            msg = QMessageBox()
            msg.setText("Password do not match with confirmation password")
            msg.exec()
        elif password == password2:
            self.connectDatabase()
            sql = ("UPDATE USERAPP "
                   "SET password = '%s' where phonenumber = '%s' and email = '%s'") % (password, self.phone, self.email)
            self.connector.queryData(sql, fetch = False)
            self.processLogin()

    def processExit(self):
        self.msg = QMessageBox()
        self.msg.setWindowTitle("Exit Confirmation")
        self.msg.setText("Are your sure you want to exit ?")
        self.msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        buttons = self.msg.exec()
        if buttons == QMessageBox.StandardButton.Yes:
            self.close()

    def processRegister(self):
        from UI.RegisterEx import RegisterEx
        self.close()
        self.mainUI = RegisterEx()
        self.mainUI.setupUi(QMainWindow())
        self.mainUI.show()

    def processLogin(self):
        from UI.AdminEx import AdminEx
        self.close()
        self.mainUI = AdminEx()
        self.mainUI.setupUi(QMainWindow())
        self.mainUI.show()

    def show(self):
        self.MainWindow.show()

    def close(self):
        self.MainWindow.close()
