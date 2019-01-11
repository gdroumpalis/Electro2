from enum import Enum

from PyQt5.QtWidgets import QAction, QPushButton, QAbstractButton


def connect(signal, method):
    signal.connect(method)

def ShowDialog(dialog):
    dialog.exec_()
    dialog.show()

