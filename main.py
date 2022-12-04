import sys

from PyQt5.QtWidgets import QApplication
from FrontEnd.InitTAWidget import InitTAWidget


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = InitTAWidget()
    sys.exit(app.exec())