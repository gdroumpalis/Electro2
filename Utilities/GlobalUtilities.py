from PySide2.QtWidgets import QAction, QPushButton, QAbstractButton,QMessageBox

def make_connection(signal, method):
    signal.connect(method)

def show_dialog(dialog):
    dialog.exec_()
    dialog.show()

def show_message(message):
    msg = QMessageBox()
    msg.setText(message)
    msg.setIcon(QMessageBox.Information)
    msg.exec_()
