# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/terminux/Documents/Projects/Electro/Resources/settings.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Settings(object):
    def setupUi(self, Settings):
        Settings.setObjectName("Settings")
        Settings.setWindowModality(QtCore.Qt.WindowModal)
        Settings.resize(452, 388)
        self.verticalLayout = QtWidgets.QVBoxLayout(Settings)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox_2 = QtWidgets.QGroupBox(Settings)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.formLayout_2 = QtWidgets.QFormLayout()
        self.formLayout_2.setObjectName("formLayout_2")
        self.label_3 = QtWidgets.QLabel(self.groupBox_2)
        self.label_3.setObjectName("label_3")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.plottinguicheckbox = QtWidgets.QCheckBox(self.groupBox_2)
        self.plottinguicheckbox.setText("")
        self.plottinguicheckbox.setObjectName("plottinguicheckbox")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.plottinguicheckbox)
        self.verticalLayout_3.addLayout(self.formLayout_2)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.buttonBox = QtWidgets.QDialogButtonBox(Settings)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Settings)
        self.buttonBox.accepted.connect(Settings.accept)
        self.buttonBox.rejected.connect(Settings.reject)
        QtCore.QMetaObject.connectSlotsByName(Settings)

    def retranslateUi(self, Settings):
        _translate = QtCore.QCoreApplication.translate
        Settings.setWindowTitle(_translate("Settings", "Settings"))
        self.groupBox_2.setTitle(_translate("Settings", "General"))
        self.label_3.setText(_translate("Settings", "Show Plotting UI"))

