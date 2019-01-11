from enum import Enum

from PySide2.QtWidgets import QAction, QPushButton, QAbstractButton


def connect(signal, method):
    signal.connect(method)

def ShowDialog(dialog):
    dialog.exec_()
    dialog.show()

