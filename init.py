import sys
import pathlib
from PySide2.QtWidgets import QApplication

from Src.maindialog import MainUI

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainUI(str(pathlib.Path(__file__).parent))
    ex.show()
    sys.exit(app.exec_())
