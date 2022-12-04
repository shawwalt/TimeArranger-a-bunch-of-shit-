from UI.UI_StatisticsWidget import Ui_StatisticsWidget
from PyQt5.QtWidgets import QWidget


class StatisticsWidget(Ui_StatisticsWidget, QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self._init_ui()

    def _init_ui(self):
        pass