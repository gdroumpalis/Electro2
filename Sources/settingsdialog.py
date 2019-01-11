from PyQt5.QtWidgets import QDialog
from UI.settings import Ui_Settings
from Utilities.GlobalUtilities import *

class SettingUI(QDialog):

    def __init__(self,maindlg):
        super().__init__()
        self.ui = Ui_Settings()
        self.ui.setupUi(self)
        self.maindlg = maindlg
        # self.initializedevicesfromfile()
        # connect(self.ui.usbdevicesdropdown.currentTextChanged , self.updateselecteddevice )

    # def initializedevicesfromfile(self):
    #     for device in self.maindlg.devices:
    #         self.ui.usbdevicesdropdown.addItem(device)
    #
    # def updateselecteddevice(self):
    #     self.maindlg.selecteddevice = self.ui.usbdevicesdropdown.currentText()