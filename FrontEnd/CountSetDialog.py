import os
import sys

from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlQueryModel

from UI.UI_CountSetDialog import Ui_CountSetDialog
from Log.my_logger import LoggerHandler
from PyQt5.QtWidgets import QDialog, QDesktopWidget, QMessageBox
from PyQt5.QtCore import QSettings, QPoint, pyqtSignal, Qt


class CountSetDialog(Ui_CountSetDialog, QDialog):
    # 自定义信号
    count_down_set_signal = pyqtSignal()
    task_to_be_complete_selected_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self._load_folder()
        self._logger_init()
        self._init_ui()
        self._init_DB()
        self._init_settings()

    def _init_ui(self):
        self.move(
            self._get_central_pos()
        )
        self.btn_ok.clicked.connect(self.btn_ok_clicked)
        self.btn_cancel.clicked.connect(self.btn_cancel_clicked)
        self.spinBox_h.setRange(0, 59)
        self.spinBox_m.setRange(0, 59)
        self.spinBox_s.setRange(0, 59)
        self.init_model_views()
        self.logger.info('TimeArranger启动')

    def _init_settings(self):
        self.setting_manager = QSettings('ShawWalt', 'TimeArranger')
        b = self.setting_manager.value('MainWindow/WorkingPeriod', 900)
        self._set_spin_boxs(int(b))
        self.logger.debug('设置初始化')

    def _save_settings(self):
        count_time = self._get_time_from_spinbox()
        self.setting_manager.setValue('MainWindow/WorkingPeriod', str(count_time))
        self.logger.debug('保存新设置')

    def init_model_views(self):
        self._open_DB()
        self.model1 = QSqlQueryModel()
        self.model1.setQuery('SELECT task FROM ToDoList')
        self.listView_task.setModel(self.model1)
        self.listView_task.setCurrentIndex(
            self.listView_task.model().index(0,0)
        )
        self.listView_task.setModelColumn(1)
        self.logger.debug('ModelView加载')
        self._close_DB()

    def _open_DB(self):
        # 测试数据库功能
        self.conn = QSqlDatabase.addDatabase("QSQLITE")
        self.db_path = self.folder + '//time_arranger.sqlite'
        self.conn.setDatabaseName(self.db_path)
        if not self.conn.open():
            QMessageBox.critical(
                None,
                "TimeArranger - 错误!",
                "数据库连接错误: %s" % self.conn.lastError().databaseText(),
            )
            sys.exit(1)
        self.logger.debug('开启数据库访问')

    def _close_DB(self):
        self.conn.close()
        self.logger.debug('关闭数据库访问')

    def _load_folder(self):
        self.folder = os.environ['AppData'] + '\\TimeArranger'
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

    def _init_DB(self):
        # 创建或连接已有数据库
        self._open_DB()
        # 查找数据表
        query = QSqlQuery()
        if self._table_exists(self.conn, "ToDoList") is False:
            query.prepare(
                '''CREATE TABLE ToDoList 
                (
                    "id"  INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
                    "is_finished" INT(1) NOT NULL DEFAULT 0,
                    "task" VARCHAR(255)
                );
                '''
            )
            if query.exec() is False:
                self.logger.debug('ToDo数据表未创建: %s', query.lastError().text())
            else:
                self.logger.debug('ToDoList已创建')
        self._close_DB()

    def _logger_init(self):
        # 初始化日志器参数
        self.logger = LoggerHandler(
            name=__name__
        )
        self.logger.debug('Logger初始化')

    def _get_time_from_spinbox(self):
        h = self.spinBox_h.value()
        m = self.spinBox_m.value()
        s = self.spinBox_s.value()
        return h * 3600 + m * 60 + s

    def _set_spin_boxs(self, time):
        h = time / 60 / 60
        m = time % 3600 / 60
        s = time % 60
        self.spinBox_s.setValue(s)
        self.spinBox_m.setValue(m)
        self.spinBox_h.setValue(h)

    def btn_ok_clicked(self):
        self._save_settings()
        i = self.listView_task.currentIndex().row()
        self.task_to_be_complete_selected_signal.emit(i)
        self.count_down_set_signal.emit()
        self.logger.debug('保存按钮按下')
        self.close()

    def btn_cancel_clicked(self):
        self.logger.debug('取消按钮按下')
        self.close()

    def _get_central_pos(self) -> QPoint:
        # 获取屏幕中心坐标
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        return QPoint(int((screen.width() - size.width()) / 2), int((screen.height() - size.height()) / 2))

    def _table_exists(self, conn, name) -> bool:
        nlist = conn.tables()
        if name in nlist:
            return True
        else:
            return False
