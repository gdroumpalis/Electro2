import sys
import pathlib
from PyQt5.QtWidgets import QApplication

from Sources.maindialog import MainUI

def getinitarguments() -> bool:
    if len(sys.argv) > 1 and "rasp" in sys.argv:
        return True
    else:
        return False

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainUI(getinitarguments(), str(pathlib.Path(__file__).parent))
    ex.show()
    sys.exit(app.exec_())
