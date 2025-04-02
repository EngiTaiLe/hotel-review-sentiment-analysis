from IPython.external.qt_for_kernel import QtGui

from UI.Admin import Ui_MainWindow
from Connectors.Connector import Connector
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QMessageBox, QMainWindow
from PyQt6.QtCore import Qt
from PyQt6 import QtWidgets

class AdminEx(Ui_MainWindow):
    def __init__(self):
        self.connector = Connector()

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow


        # Set images
        self.lblLogo.setPixmap(QPixmap("/Users/macbook/Documents/Uni/NĂM_3/HK6/KTLT/Project/images/ic_agoda.png"))
        self.lblPass.setPixmap(QPixmap("/Users/macbook/Documents/Uni/NĂM_3/HK6/KTLT/Project/images/ic_lock.png"))
        self.lblUsrName.setPixmap(QPixmap("/Users/macbook/Documents/Uni/NĂM_3/HK6/KTLT/Project/images/ic_person.png"))

        font = QtGui.QFont()
        font.setBold(True)
        self.btnLogin.setFont(font)

        self.btnExit.clicked.connect(self.processExit)
        self.btnRegis.clicked.connect(self.processRegister)
        self.btnForget.clicked.connect(self.processForget)
        self.btnLogin.clicked.connect(self.processLogin)
        self.ckbShow.stateChanged.connect(self.processChecked)

    def connectDatabase(self):
        self.connector.server = "localhost"
        self.connector.port = 3306
        self.connector.database = "KTLT"
        self.connector.username = "root"
        self.connector.password = ""
        self.connector.connect()

    def processLogin(self):
        self.connectDatabase()
        username = self.txtUsrName.text()
        password = self.txtPass.text()
        if (username == '') or (password == ''):
            msg = QMessageBox()
            msg.setText("You need to fill enough information")
            msg.exec()
        else:
            sql = "SELECT username, password FROM USERAPP WHERE username = '%s'"%username
            df = self.connector.queryData(sql)
            emp = True
            if df.empty:
                sql = "SELECT email, password FROM USERAPP WHERE email = '%s'" %username
                df = self.connector.queryData(sql)
                if df.empty:
                    msg = QMessageBox()
                    msg.setText("Incorrect Username or Email")
                    msg.exec()
                    emp = False
            if emp:
                if df.iloc[0]['password'] == password:
                    self.MainWindow.close()
                    self.processMain()
                else:
                    msg = QMessageBox()
                    msg.setText("Incorrect Password")
                    msg.exec()

    def processMain(self):
        from UI.MainWindowEx import MainWindowEx
        self.mainUI = MainWindowEx()
        self.mainUI.setupUi(QMainWindow())
        self.mainUI.show()

    def processChecked(self,value):
        state=Qt.CheckState(value)
        if state==Qt.CheckState.Checked:
            self.txtPass.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
        elif state==Qt.CheckState.Unchecked:
            self.txtPass.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

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

    def processForget(self):
        from UI.GetPasswordEx import GetPasswordEx
        self.close()
        self.mainUI = GetPasswordEx()
        self.mainUI.setupUi(QMainWindow())
        self.mainUI.show()

    def show(self):
        self.MainWindow.show()

    def close(self):
        self.MainWindow.close()