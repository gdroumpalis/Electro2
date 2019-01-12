from PyQt5.QtWidgets import QDialog
from UI.settings import Ui_Settings
from Utilities.GlobalUtilities import *

class SettingUI(QDialog):

    def __init__(self,maindlg):
        super().__init__()
        self.ui = Ui_Settings()
        self.ui.setupUi(self)
        self.maindlg = maindlg

