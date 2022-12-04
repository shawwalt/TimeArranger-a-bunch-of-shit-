from UI.UI_CopyRight import Ui_CopyRight
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QDesktopWidget
from PyQt5.QtCore import QPoint
from PyQt5 import Qt


class CopyRight(Ui_CopyRight, QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self._init_ui()

    def _init_ui(self):
        self.setWindowFlags(Qt.Qt.CustomizeWindowHint)
        self.move(self._get_central_pos())

    def _get_central_pos(self) -> QPoint:
        # 获取屏幕中心坐标
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        return QPoint(int((screen.width() - size.width()) / 2), int((screen.height() - size.height()) / 2))