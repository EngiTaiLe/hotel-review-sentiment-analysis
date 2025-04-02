from PyQt6.QtWidgets import QMessageBox, QMainWindow
from PyQt6 import QtGui
from UI.Register import Ui_MainWindow
from PyQt6.QtGui import QPixmap
from Connectors.Connector import Connector

class RegisterEx(Ui_MainWindow):
    def __init__(self):
        self.connector = Connector()

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow

        # Set images
        self.lblFirst.setPixmap(QPixmap("/Users/macbook/Documents/Uni/NĂM_3/HK6/KTLT/Project/images/ic_person.png"))
        self.lblLast.setPixmap(QPixmap("/Users/macbook/Documents/Uni/NĂM_3/HK6/KTLT/Project/images/ic_person.png"))
        self.lblUser.setPixmap(QPixmap("/Users/macbook/Documents/Uni/NĂM_3/HK6/KTLT/Project/images/ic_person.png"))
        self.lblPass.setPixmap(QPixmap("/Users/macbook/Documents/Uni/NĂM_3/HK6/KTLT/Project/images/ic_lock.png"))
        self.lblConfirm.setPixmap(QPixmap("/Users/macbook/Documents/Uni/NĂM_3/HK6/KTLT/Project/images/ic_lock.png"))
        self.lblPhone.setPixmap(QPixmap("/Users/macbook/Documents/Uni/NĂM_3/HK6/KTLT/Project/images/ic_phone.png"))
        self.lblLogo.setPixmap(QPixmap("/Users/macbook/Documents/Uni/NĂM_3/HK6/KTLT/Project/images/ic_agoda.png"))
        self.lblEmail.setPixmap(QPixmap("/Users/macbook/Documents/Uni/NĂM_3/HK6/KTLT/Project/images/ic_email.png"))

        font = QtGui.QFont()
        font.setBold(True)
        self.btnRegis.setFont(font)

        self.btnExit.clicked.connect(self.processExit)
        self.btnLogin.clicked.connect(self.processLogin)
        self.btnForget.clicked.connect(self.processForget)
        self.btnRegis.clicked.connect(self.processRegister)

    def processExit(self):
        self.msg = QMessageBox()
        self.msg.setWindowTitle("Exit Confirmation")
        self.msg.setText("Are your sure you want to exit ?")
        self.msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        buttons = self.msg.exec()
        if buttons == QMessageBox.StandardButton.Yes:
            self.close()

    def processLogin(self):
        from UI.AdminEx import AdminEx
        self.close()
        self.mainUI = AdminEx()
        self.mainUI.setupUi(QMainWindow())
        self.mainUI.show()

    def processForget(self):
        from UI.GetPasswordEx import GetPasswordEx
        self.close()
        self.mainUI = GetPasswordEx()
        self.mainUI.setupUi(QMainWindow())
        self.mainUI.show()

    def connectDatabase(self):
        self.connector.server = "localhost"
        self.connector.port = 3306
        self.connector.database = "KTLT"
        self.connector.username = "root"
        self.connector.password = ""
        self.connector.connect()

    def processRegister(self):
        firstname = self.txtFirst.text()
        lastname = self.txtLast.text()
        username = self.txtUser.text()
        password = self.txtPass.text()
        password2 = self.txtConfirm.text()
        phone = self.txtPhone.text()
        email = self.txtEmail.text()
        if (firstname == '') or (lastname == '') or (username == '') or (password == '') or (password2 == '') or (email == ''):
            msg = QMessageBox()
            msg.setText("You need to fill enough information")
            msg.exec()
        elif len(phone) != 10:
            msg = QMessageBox()
            msg.setText('Phone number need to have exactly 10 digits')
            msg.exec()
        elif email != '':
            self.connectDatabase()
            sql = "SELECT Email FROM USERAPP WHERE Email = '%s'" % email
            self.res = self.connector.queryData(sql)
            if len(self.res) == 1:
                msg = QMessageBox()
                msg.setText("This email is already registered")
                msg.exec()
            elif password != password2:
                msg = QMessageBox()
                msg.setText("Password do not match with confirmation password")
                msg.exec()
            elif password == password2:
                msg = QMessageBox()
                msg.setText("Are you sure all information correct")
                msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                button = msg.exec()
                if button == QMessageBox.StandardButton.Yes:
                    self.connectDatabase()
                    # sql = "SELECT MAX(UserAppID) FROM USERAPP"
                    # result = self.connector.queryData(sql)
                    # adminid = int(result.iloc[0,0]) + 1
                    sql1 = ("INSERT INTO USERAPP(FirstName,LastName,UserName,Password,PhoneNumber,Email) "
                            "VALUES ('%s','%s','%s','%s','%s','%s')") % (firstname,lastname,username,password,phone,email)
                    self.connector.queryData(sql1, fetch=False)
                    self.processLogin()
        else:
            pass

    def show(self):
        self.MainWindow.show()

    def close(self):
        self.MainWindow.close()