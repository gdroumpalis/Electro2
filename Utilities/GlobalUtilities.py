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


def release_resources(serial_connection, file, thread_loopers):
    print("Releasing resources")
    if file is not None:
        file.close()
    serial_connection.close()
    for looper in thread_loopers:
        looper.finish_execution()
    del thread_loopers[:]
    print("Resources released")
