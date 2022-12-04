import os
import sys
import resources
from functools import partial

from PyQt5 import QtCore
from PyQt5.QtGui import QIcon

from UI.UI_InitTAWidget import Ui_InitTAWidget
from UI.UI_LogWidget import Ui_LogWidget
from FrontEnd.ClockWidget import ClockWidget
from FrontEnd.CountSetDialog import CountSetDialog
from FrontEnd.CopyRight import CopyRight
from FrontEnd.StatisticsWidget import StatisticsWidget
from Log.my_logger import LoggerHandler
from PyQt5.QtCore import (QTimer, QSettings, QPoint, QVariant, pyqtSignal, Qt, QSize)
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QMessageBox, QSystemTrayIcon, QMenu, QAction, QInputDialog, \
    QLineEdit, QPushButton, QWidget, QListWidgetItem
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlQueryModel

WORKING = 1
RELAXING = 0


#  系统托盘类
class TrayIcon(QSystemTrayIcon):
    quit_signal = pyqtSignal(int)
    hide_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(TrayIcon, self).__init__(parent)
        self._logger_init()
        self._show_menu()
        self._other()

    def _logger_init(self):
        # 初始化日志器参数
        self.logger = LoggerHandler(
            name=__name__
        )
        self.logger.debug('Logger初始化')

    def _show_menu(self):
        # 设计托盘的菜单，这里我实现了一个二级菜单
        self.menu = QMenu()
        self.quitAction = QAction("退出", self, triggered=self.quit)
        self.menu.addAction(self.quitAction)
        self.setContextMenu(self.menu)

    def _other(self):
        # 添加信号与槽函数的绑定
        self.activated.connect(self.icon_clicked)

    def icon_clicked(self, reason):
        # 鼠标点击icon传递的信号会带有一个整形的值，1是表示单击右键，2是双击，3是单击左键，4是用鼠标中键点击
        if reason == 2 or reason == 3:
            self.hide_signal.emit()

    def quit(self):
        self.quit_signal.emit(0)


class LogWidget(QWidget, Ui_LogWidget):
    def __init__(self, log_time, log_msg, log_level, parent=None):
        super(LogWidget, self).__init__(parent)
        self.setupUi(self)
        self.log_msg.setText(log_msg)
        self.log_level.setText(log_level)
        self.log_time.setText(log_time)


class InitTAWidget(Ui_InitTAWidget, QMainWindow):

    statistics_widget = None
    copy_right = None
    clock_widget = None
    count_set_dialog = None
    ti = None

    timer = None
    timer_copy_right = None
    setting_manager = None

    # 状态变量
    is_timing = False  # 计时状态变量
    duration = 0  # 计时持续时间

    # 自定义信号
    count_down_terminate_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.count_set_dialog = CountSetDialog()
        self.setupUi(self)
        self._load_folder()
        self._logger_init()
        self._init_ui()
        self._init_settings()
        self._init_DB()
        self._init_model_views()
        self._copy_right_init()
        self._tray_icon_init()
        self._clock_widget_init()
        self._count_set_widget_init()
        self._statistics_widget_init()
        self._init_mode()
        self._init_listView_log()

    def _init_ui(self):
        # 初始化信号与槽的绑定，界面大小等参数的设置，数据库的的加载等
        self.btn_mode = QPushButton()
        self.toolBar.addWidget(self.btn_mode)
        self.toolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.btn_stop_timing.setDisabled(True)
        self.btn_start_timing.setDisabled(False)

        self._timer_init()
        self._lcd_init()
        self.action_statistics.triggered.connect(self.action_statistics_triggered)
        self.btn_start_timing.clicked.connect(self.btn_start_timing_clicked)
        self.btn_stop_timing.clicked.connect(self.btn_stop_timing_clicked)
        self.btn_new_task.clicked.connect(self.btn_new_task_clicked)
        self.btn_rm_task.clicked.connect(self.btn_rm_task_clicked)
        self.btn_mode.clicked.connect(self.btn_mode_clicked)
        self.count_down_terminate_signal.connect(self.count_down_terminate_signal_triggered)

    def _init_settings(self):
        self.setting_manager = QSettings('ShawWalt', 'TimeArranger')
        self.move(
            self.setting_manager.value('MainWindow/win_pos', QVariant(self._get_central_pos()))
        )

        self.btn_mode.setText(
            self.setting_manager.value('MainWindow/mode', '工作模式')
        )

    def _save_settings(self):
        self.setting_manager.setValue('MainWindow/mode', self.btn_mode.text())
        self.setting_manager.setValue('MainWindow/win_pos', QVariant(QPoint(self.x(), self.y())))

    def _open_DB(self):
        self.conn = QSqlDatabase.addDatabase("QSQLITE")
        self._load_folder()
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

    def _init_mode(self):
        if self.btn_mode.text() == '工作模式':
            self.mode = WORKING
            self.lcdNumber.setStyleSheet('border: 1px solid green; color: green; background: silver;')
            self.clock_widget.is_relaxing = False
        else:
            self.mode = RELAXING
            self.clock_widget.setMouseTracking(True)
            self.btn_new_task.setDisabled(True)
            self.btn_rm_task.setDisabled(True)
            self.lcdNumber.setStyleSheet('border: 1px solid blue; color: blue; background: silver;')
            self.clock_widget.is_relaxing = True
            self.listView.setDisabled(True)

    def _init_DB(self):
        self._open_DB()
        query = QSqlQuery()
        if self._table_exists(self.conn, "BasicUserData") is False:
            query.prepare(
                '''
                CREATE TABLE BasicUserData
                (
                    start_time DATETIME NOT NULL DEFAULT current_timestamp PRIMARY KEY,
                    terminate_time DATETIME NOT NULL DEFAULT current_timestamp,
                    task VARCHAR(255),
                    duration INTEGER NOT NULL 
                )
                '''
            )  # 默认开始时间和结束时间相等，知道计时结束后更新结束时间，如果遇到中断则视为未完成
            if query.exec() is False:
                self.logger.debug('BasicUserData未创建')
                print(query.lastError().text())
            else:
                self.logger.debug('BasicUserData已创建')
        self._close_DB()

    def _table_exists(self, conn, name) -> bool:
        nlist = conn.tables()
        if name in nlist:
            return True
        else:
            return False

    def _tray_icon_init(self):
        self.ti = TrayIcon(self)
        self.ti.setIcon(QIcon(':/icon/tray_icon.jpg'))
        self.ti.quit_signal.connect(self.quit)
        self.ti.hide_signal.connect(self.switch_between_show_n_hide)
        self.ti.show()
        self.logger.debug('托盘图标初始化')

    def _count_set_widget_init(self):
        self.count_set_dialog = CountSetDialog()
        self.count_set_dialog.count_down_set_signal.connect(self.count_down_set_signal_triggered)
        self.count_set_dialog.task_to_be_complete_selected_signal.connect(self.task_to_be_complete_selected_triggered)
        self.logger.debug('计时设置面板初始化')

    def _copy_right_init(self):
        if self.copy_right is None:
            self.copy_right = CopyRight()
        self.copy_right.show()
        self.timer_copy_right.start(3000)
        self.logger.debug('加载版权页')

    def _copy_right_close(self):
        self.copy_right.close()
        self.timer_copy_right.stop()
        self.activateWindow()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.showNormal()
        self.logger.debug('版权页关闭 ,显示主界面')

    def _clock_widget_init(self):
        self.clock_widget = ClockWidget()
        self.clock_widget.label.setText('工作时间剩余:00:00:00')
        self.logger.debug('计时小控件初始化')

    def _statistics_widget_init(self):
        self.statistics_widget = StatisticsWidget()
        self.logger.debug('数据分析界面初始化')

    def _logger_init(self):
        # 初始化日志器参数
        self.logger = LoggerHandler(
            name=__name__
        )
        self.logger.set_file_handler(
            file=self.folder,
            logger_level='INFO',
            fmt='%(asctime)s %(levelname)s %(message)s'
        )
        self.logger.debug('Logger初始化')

    def _lcd_init(self):
        self.lcdNumber.setDigitCount(8)
        self.lcdNumber.display('00:00:00')
        self.logger.debug('LCD初始化')

    def _init_model_views(self):
        self._open_DB()
        self.model_task = QSqlQueryModel()
        self.model_task.setQuery('SELECT task FROM ToDoList')
        self.listView.setModel(self.model_task)
        self.listView.setModelColumn(1)
        self.listView.setCurrentIndex(self.listView.model().index(0, 0))
        self.count_set_dialog.init_model_views()
        self.logger.debug('ModelView加载')
        self._close_DB()

    def _timer_init(self):
        self.timer = QTimer()
        self.timer_copy_right = QTimer()
        self.timer.timeout.connect(self.timer_count_down)
        self.timer_copy_right.timeout.connect(self._copy_right_close)
        self.logger.debug('QTimer初始化')

    def _get_central_pos(self) -> QPoint:
        # 获取屏幕中心坐标
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        return QPoint(int((screen.width() - size.width()) / 2), int((screen.height() - size.height()) / 2))

    def action_statistics_triggered(self):
        if self.statistics_widget is None:
            self.statistics_widget = StatisticsWidget()
        self.statistics_widget.show()
        self.logger.debug('打开数据分析面板')

    def btn_start_timing_clicked(self):
        # 绑定计时函数，一旦按下Ok，配置界面关闭，
        if self.mode == WORKING:
            self.count_set_dialog.show()
            self.logger.debug('打开计时设置面板,工作模式')
        else:
            self.count_set_dialog.show()
            self.count_set_dialog.listView_task.setDisabled(True)
            self.logger.debug('打开计时设置面板,休息模式')

    def btn_stop_timing_clicked(self):
        self.logger.debug('停止计时按钮按下')
        msg = QMessageBox()
        if self.mode == WORKING:
            msg.setText('还在计时中')
            msg.setInformativeText('规定的工作时长还未达到，确定放弃自律了吗？')
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        else:
            msg.setText('还在计时中')
            msg.setInformativeText('再休息一下吧，恢复精力也是工作的一部分')
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        ret = msg.exec()
        # 工作模式，删除被中断的任务记录
        if self.mode == WORKING:
            self._open_DB()
            query = QSqlQuery()
            query.prepare('Delete From BasicUserData WHERE task = :task')
            task = self.model_task.data(
                self.listView.currentIndex()
            )
            if task is None:
                if self.mode == WORKING:
                    task = 'None'
                else:
                    task = 'Relaxing'
            query.bindValue(':task', task)
            if query.exec():
                self.logger.debug('任务记录删除成功')
            else:
                self.logger.debug(query.lastError().text())

        if ret == QMessageBox.Ok:
            self.is_timing = False
            self.btn_stop_timing.setDisabled(True)
            self.btn_start_timing.setDisabled(False)
            if self.mode == WORKING:
                self.listView.setDisabled(False)
                self.btn_new_task.setDisabled(False)
                self.btn_rm_task.setDisabled(False)
            self.timer.stop()
            self.lcdNumber.display('00:00:00')
            self.clock_widget.label.setText('工作时间剩余00:00:00')
            self.clock_widget.close()

    def task_to_be_complete_selected_triggered(self, i):
        self.listView.setCurrentIndex(self.listView.model().index(i, 0))
        self.listView.setDisabled(True)

    def count_down_set_signal_triggered(self):
        # 从注册表加载计时时间
        i = self.listView.currentIndex()
        task = self.model_task.data(i)
        if task is None:
            if self.mode == WORKING:
                task = 'None'
            else:
                task = 'Relaxing'
        self._open_DB()
        query = QSqlQuery()
        query.prepare(
            '''
            INSERT INTO BasicUserData (task, duration)
            VALUES (:task, :duration) 
            '''
        )  # 执行完成本次插入后两个时间戳是相同的
        if self.mode == WORKING:
            self.is_timing = True
            self.btn_start_timing.setDisabled(True)
            self.btn_stop_timing.setDisabled(False)
            self.btn_rm_task.setDisabled(True)
            self.btn_new_task.setDisabled(True)
            self.duration = self.setting_manager.value('MainWindow/WorkingPeriod', 300)
            self.duration = int(self.duration)  # 切记注册表存的是字符串，要转回原类型
            h, m, s = self._int2time(self.duration)
            time_fmt = "%02d:%02d:%02d"%(h, m, s)
            self.lcdNumber.display(
                time_fmt
            )
            self.clock_widget.label.setText('工作时间剩余:' + time_fmt)
            self.timer.start(1000)
            self.logger.info('开始执行任务:%s' % task)
        else:
            self.is_timing = True
            self.btn_start_timing.setDisabled(True)
            self.btn_stop_timing.setDisabled(False)
            self.btn_rm_task.setDisabled(True)
            self.btn_new_task.setDisabled(True)
            self.duration = self.setting_manager.value('MainWindow/WorkingPeriod', 300)
            self.duration = int(self.duration)  # 切记注册表存的是字符串，要转回原类型
            h, m, s = self._int2time(self.duration)
            time_fmt = "%02d:%02d:%02d" % (h, m, s)
            self.lcdNumber.display(
                time_fmt
            )
            self.clock_widget.label.setText('休息时间剩余:' + time_fmt)
            self.logger.info('开始休息')
            self.timer.start(1000)
            self.logger.debug('开始计时(休息时间)')

        query.bindValue(':task', task)
        query.bindValue(':duration', self.duration)
        if query.exec():
            self.logger.debug('BasicUserData插入已执行')
        else:
            self.logger.debug(query.lastError().text())
        self._close_DB()
        self.close()

    def count_down_terminate_signal_triggered(self):
        self._open_DB()
        query = QSqlQuery()
        query.prepare(
            '''
                UPDATE BasicUserData SET terminate_time = datetime('now') 
                WHERE task = :task and (start_time in (SELECT max(start_time) FROM BasicUserData)) 
            '''
        )
        i = self.listView.currentIndex()
        task = self.model_task.data(i)
        if task is None:
            if self.mode == WORKING:
                task = 'None'
            else:
                task = 'Relaxing'
        query.bindValue(':task', task)
        if query.exec():
            self.logger.debug('BasicUserData修改值成功')
        else:
            self.logger.debug(query.lastError().text())

        self.logger.debug('计时结束')
        self.showNormal()
        # 提示框
        msg = QMessageBox(self)
        if self.mode == WORKING:
            msg.setText('计时结束')
            i = self.listView.currentIndex()
            selected_task = self.model_task.data(i)
            msg.setInformativeText('任务%s已完成' % selected_task)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.show()
            self.btn_rm_task_clicked()  # 该函数里也打开了一次数据库，并执行了关闭，因此开发时遇到了bug
            self.listView.setDisabled(False)
            self.btn_rm_task.setDisabled(False)
            self.btn_new_task.setDisabled(False)
            self.logger.info('任务%s已完成' % selected_task)
        else:
            msg.setText('计时结束')
            msg.setInformativeText('休息结束了，恢复精力后继续认真完成工作吧')
            msg.setStandardButtons(QMessageBox.Ok)
            msg.show()
            self.logger.info('休息结束')

        self.btn_start_timing.setDisabled(False)
        self.btn_stop_timing.setDisabled(True)
        self.clock_widget.close()
        self.timer.stop()
        self._close_DB()

    def _int2time(self, time):
        h = time / 60 / 60
        m = time % 3600 / 60
        s = time % 60
        return int(h), int(m), int(s)

    def timer_count_down(self):
        self.duration = self.duration - 1
        h, m, s = self._int2time(self.duration)
        time_fmt = "%02d:%02d:%02d" % (h, m, s)
        self.lcdNumber.display(time_fmt)
        if self.mode == WORKING:
            self.clock_widget.label.setText('工作时间剩余:' + time_fmt)
        else:
            self.clock_widget.label.setText('休息时间剩余:' + time_fmt)
        self.logger.debug('剩余时间%d', self.duration)
        if self.duration == 0:
            self.is_timing = False  # 更新标志，计时结束
            self.count_down_terminate_signal.emit()

    def btn_new_task_clicked(self):
        self.logger.debug('新建任务')
        self._open_DB()
        query = QSqlQuery()
        query.prepare(
            '''
            INSERT INTO ToDoList (
                is_finished,
                task
            ) 
            VALUES (:is_finished, :task)
            '''
        )
        text, ok_pressed = QInputDialog.getText(self, '又有什么新的代办了吗', "任务名称", QLineEdit.Normal, "")
        if ok_pressed and text != '':
            query.bindValue(":is_finished", 0)
            query.bindValue(":task", text)
            if query.exec() is True:
                self.logger.debug('任务%s已创建', text)
                self.logger.info('创建了新任务%s', text)
            else:
                self.logger.debug(query.lastError().text())
        self._init_model_views()
        self._close_DB()

    def btn_rm_task_clicked(self):
        i = self.listView.currentIndex()
        self._open_DB()
        query = QSqlQuery()
        query.prepare('''
            DELETE FROM ToDoList WHERE id = :id
        ''')
        query.bindValue(':id', i.row()+1)
        if query.exec() is True:
            self.logger.debug('删除成功%d', i.row()+1)
            i = self.listView.currentIndex()
            task = self.model_task.data(i)
            self.logger.info('将任务%s移出任务清单', task)
            last_query = self.model_task.query().executedQuery()
            self.model_task.setQuery(last_query)
        else:
            self.logger.debug('删除失败')

        query = QSqlQuery()
        query.prepare(
            '''
                UPDATE ToDoList SET id = id - 1 WHERE id > :id
            ''')
        query.bindValue(':id', i.row() + 1)
        if query.exec() is True:
            self.logger.debug('id更新完成')
        else:
            self.logger.debug('更新失败%s', query.lastError().text())

        query = QSqlQuery()
        query.prepare(
            '''
                UPDATE sqlite_sequence SET seq = seq - 1  WHERE name = "ToDoList"
            '''
        )
        if query.exec() is True:
            self.logger.debug('ToDoList_seq更新完成')
        else:
            self.logger.debug('更新失败%s', query.lastError().text())
        self._init_model_views()
        self._close_DB()

    def btn_mode_clicked(self):
        if self.btn_mode.text() == '工作模式':
            self.btn_mode.setText('休息模式')
            self.mode = RELAXING
            self.switch_to_relaxing()
        else:
            self.btn_mode.setText('工作模式')
            self.mode = WORKING
            self.switch_to_working()

    def switch_to_relaxing(self):
        self.listView.setDisabled(True)
        self.btn_rm_task.setDisabled(True)
        self.btn_new_task.setDisabled(True)
        self.lcdNumber.setStyleSheet("border: 1px solid blue; color: blue; background: silver;")

    def switch_to_working(self):
        self.listView.setDisabled(False)
        self.count_set_dialog.listView_task.setEnabled(True)
        self.btn_rm_task.setEnabled(True)
        self.btn_new_task.setEnabled(True)
        self.clock_widget.setMouseTracking(False)
        self.lcdNumber.setStyleSheet("border: 1px solid green; color: green; background: silver;")

    def switch_between_show_n_hide(self):
        #  用于主界面和计时小窗口显示状态切换
        if self.isVisible() is True:
            self.hide()
            if self.is_timing is False:
                return
            self.clock_widget.show()
        else:
            self.activateWindow()
            # setWindowState()：根据Flags值设置窗口的状态,多个 WindowFlags之间用 | 连接
            # windowState()正常状态， WindowMinimized最小化， WindowActive活动状态
            # 窗口取消最小化并设置为活动状态
            self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
            self.showNormal()
            if self.is_timing is False:
                return
            self.clock_widget.hide()

    def _init_listView_log(self):
        self._init_log_list()  # 初始化日志列表
        self._check_n_remove_log()  # 检查日志数量并且删除时间过早的日志
        self.listWidget_log.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listWidget_log.customContextMenuRequested.connect(self._customize_context_menu) # 设置右键菜单栏，加载日志名称，绑定菜单栏触发事件
        self._load_log_widget()  # 加载日志控件

    def _init_log_list(self):
        list_directory = os.listdir(self.folder)
        self.log_list = []
        for directory in list_directory:
            de_path = self.folder + '//' + directory
            if os.path.isfile(de_path):
                if de_path.endswith('.log'):
                    self.log_list.append(de_path)
        self.log_list.sort(key=None, reverse=True)
        self.logger.debug('加载日志列表')

    def _check_n_remove_log(self):
        # 删除过早的日志文件
        if len(self.log_list) > 20:
            for i in self.log_list[20:len(self.log_list)]:
                self.log_list.remove(i)
                os.remove(i)

    def _customize_context_menu(self, position):
        # 设置右键菜单栏，加载日志名称，绑定菜单栏触发事件
        pop_menu = QMenu()
        for log_path in self.log_list:
            action = QAction(os.path.basename(log_path), self)
            action.triggered.connect(partial(self._refresh_list_view_log, log_path))
            pop_menu.addAction(action)
        pop_menu.exec(self.listWidget_log.mapToGlobal(position))

    def _refresh_list_view_log(self, log_path):
        self.listWidget_log.clear()
        path = log_path
        with open(path) as f:
            data_list = f.readlines()
            if data_list:
                for line in data_list:
                    str_list = line.split(' ')
                    w = LogWidget(str_list[0]+' '+str_list[1], str_list[3], str_list[2])
                    item = QListWidgetItem()
                    item.setSizeHint(QSize(200, 80))
                    self.listWidget_log.addItem(item)
                    self.listWidget_log.setItemWidget(item, w)

    def _load_log_widget(self):
        # 加载日志控件, 默认加载列表第一位日志
        with open(self.log_list[0]) as f:
            data_list = f.readlines()
            if data_list:
                for line in data_list:
                    str_list = line.split(' ')
                    w = LogWidget(str_list[0] +' '+ str_list[1], str_list[3], str_list[2])
                    item = QListWidgetItem()
                    item.setSizeHint(QSize(200, 80))
                    self.listWidget_log.addItem(item)
                    self.listWidget_log.setItemWidget(item, w)

    def quit(self):
        if self.is_timing:  # 检测到还在计时，弹窗确认退出
            msg = QMessageBox()
            if self.mode == WORKING:
                msg.setText('还在计时中')
                msg.setInformativeText('规定的工作时长还未达到，确定放弃自律了吗？')
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            else:
                msg.setText('还在计时中')
                msg.setInformativeText('再休息一下吧，恢复精力也是工作的一部分')
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            ret = msg.exec()
            if ret == QMessageBox.Ok:
                self.clock_widget.save_settings()
                self._save_settings()
                if self.mode == WORKING:
                    i = self.listView.currentIndex()
                    task = self.model_task.data(i)
                    if task is None:
                        if self.mode == WORKING:
                            task = 'None'
                        else:
                            task = 'Relaxing'
                    self.logger.info('在进行%s时中途放弃,要养成自律的好习惯!!!' % task)
                    # 工作模式，删除被中断的任务记录
                    self._open_DB()
                    query = QSqlQuery()
                    query.prepare('Delete From BasicUserData WHERE task = :task')
                    query.bindValue(':task', task)
                    if query.exec():
                        self.logger.debug('任务记录删除成功')
                    else:
                        self.logger.debug(query.lastError().text())
                else:
                    task = '休息'
                    query = QSqlQuery()
                    query.prepare('Delete From BasicUserData WHERE task = :task')
                    query.bindValue(':task', task)
                    self.logger.info('工作很重要,但也要注意眼睛和身体!!!')
                sys.exit(0)
        else:
            msg = QMessageBox()
            msg.setText('离开TimeArranger')
            msg.setInformativeText('确认离开TimeArranger吗？')
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            ret = msg.exec()
            if ret == QMessageBox.Ok:
                self.clock_widget.save_settings()
                self._save_settings()
                self.logger.info('TimeArranger正常退出')
                sys.exit(0)

    def closeEvent(self, event):
        event.ignore()
        if self.is_timing is True:
            self.clock_widget.show()
        self.hide()
