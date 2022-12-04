from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QSettings, QPoint
from UI.UI_ClockWidget import Ui_ClockWidget
from PyQt5.QtWidgets import QWidget, QApplication, QDesktopWidget
from Log.my_logger import LoggerHandler


class ClockWidget(Ui_ClockWidget, QWidget):

    e_pos = None  # 记录鼠标事件发生位置
    w_pos = None  # 记录鼠标事件发生时窗口起始位置
    is_moving = False  # 记录窗口运动状态
    is_relaxing = False

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self._logger_init()
        self._init_settings()
        self._init_ui()

    def _init_ui(self):
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint)
        self.move(
            self.setting_manager.value('MainWindow/clk_pos', self._get_central_pos())
        )

    def _init_settings(self):
        self.setting_manager = QSettings('ShawWalt', 'TimeArranger')
        self.logger.debug('设置初始化')

    def save_settings(self):
        self.setting_manager.setValue('MainWindow/clk_pos', self.pos())

    def _logger_init(self):
        self.logger = LoggerHandler(
            name=__name__
        )
        self.logger.debug('Logger初始化')

    def _get_central_pos(self) -> QPoint:
        # 获取屏幕中心坐标
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        return QPoint(int((screen.width() - size.width()) / 2), int((screen.height() - size.height()) / 2))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_moving = True
            self.e_pos = event.globalPos()
            self.w_pos = self.frameGeometry().topLeft()

    def mouseReleaseEvent(self, event):
        self.is_moving = False

    def mouseMoveEvent(self, event):
        if self.is_moving:
            r_pos = event.globalPos() - self.e_pos  # 鼠标相对原来移动的位置
            self.move(self.w_pos + r_pos)

