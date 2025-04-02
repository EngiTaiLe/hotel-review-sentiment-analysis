import sys

from PyQt6.QtWidgets import QApplication, QMainWindow
from UI.AdminEx import AdminEx

app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

f = AdminEx()
f.setupUi(QMainWindow())

f.show()
sys.exit(app.exec())

