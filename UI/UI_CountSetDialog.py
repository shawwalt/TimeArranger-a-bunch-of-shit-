# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CountSetDialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_CountSetDialog(object):
    def setupUi(self, CountSetDialog):
        CountSetDialog.setObjectName("CountSetDialog")
        CountSetDialog.resize(408, 492)
        self.gridLayout_2 = QtWidgets.QGridLayout(CountSetDialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.groupBox = QtWidgets.QGroupBox(CountSetDialog)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.spinBox_h = QtWidgets.QSpinBox(self.groupBox)
        self.spinBox_h.setObjectName("spinBox_h")
        self.horizontalLayout_2.addWidget(self.spinBox_h)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.spinBox_m = QtWidgets.QSpinBox(self.groupBox)
        self.spinBox_m.setObjectName("spinBox_m")
        self.horizontalLayout_2.addWidget(self.spinBox_m)
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_2.addWidget(self.label_3)
        self.spinBox_s = QtWidgets.QSpinBox(self.groupBox)
        self.spinBox_s.setObjectName("spinBox_s")
        self.horizontalLayout_2.addWidget(self.spinBox_s)
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_2.addWidget(self.label_4)
        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 2)
        self.listView_task = QtWidgets.QListView(self.groupBox)
        self.listView_task.setObjectName("listView_task")
        self.gridLayout.addWidget(self.listView_task, 0, 0, 1, 2)
        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 2)
        spacerItem1 = QtWidgets.QSpacerItem(181, 28, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem1, 1, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btn_ok = QtWidgets.QPushButton(CountSetDialog)
        self.btn_ok.setObjectName("btn_ok")
        self.horizontalLayout.addWidget(self.btn_ok)
        self.btn_cancel = QtWidgets.QPushButton(CountSetDialog)
        self.btn_cancel.setObjectName("btn_cancel")
        self.horizontalLayout.addWidget(self.btn_cancel)
        self.gridLayout_2.addLayout(self.horizontalLayout, 1, 1, 1, 1)

        self.retranslateUi(CountSetDialog)
        QtCore.QMetaObject.connectSlotsByName(CountSetDialog)

    def retranslateUi(self, CountSetDialog):
        _translate = QtCore.QCoreApplication.translate
        CountSetDialog.setWindowTitle(_translate("CountSetDialog", "设置你的定时计划"))
        self.groupBox.setTitle(_translate("CountSetDialog", "要完成的任务"))
        self.label.setText(_translate("CountSetDialog", "工作时长："))
        self.label_2.setText(_translate("CountSetDialog", "时"))
        self.label_3.setText(_translate("CountSetDialog", "分"))
        self.label_4.setText(_translate("CountSetDialog", "秒"))
        self.btn_ok.setText(_translate("CountSetDialog", "确定"))
        self.btn_cancel.setText(_translate("CountSetDialog", "取消"))
