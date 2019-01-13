from PySide2.QtCore import QSize
from PySide2.QtWidgets import QWidget, QApplication, QMainWindow, QListWidgetItem, QMessageBox, QFileDialog
import UI.mainui
from Utilities.GlobalUtilities import *
from subprocess import check_call, call, Popen
import os
import uuid
import serial
from Utilities.Enums import *

filename2 = ""
filename = ""


class MainUI(QMainWindow):

    def __init__(self,  initfilepath):

        super().__init__()
        self.initfilepath = initfilepath
        self.monitorthread = None
        self.ui = UI.mainui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.initialize_electro()
        self.make_connections()
        self.attach_keyboard_shortcuts()
        self.initialize_widgets()

    def initialize_widgets(self):
        self.initialize_liveplot_tab()
        self.initialize_sampling_tab()
        self.initialize_handling_tab()

    def initialize_handling_tab(self):
        self.stop_monitoring_thread()
        self.ui.printedmessage.clear()
        self.ui.electroactions.clear()
        self.ui.handleractiontype.clear()
        self.ui.handleractiontype.addItem(
            "Shell Script", HandlerIndex.Shell.value)
        self.ui.handleractiontype.addItem(
            "Electro Action", HandlerIndex.Electro.value)
        self.ui.electroactions.addItem(
            "Print Message", ElectroAction.PrintMessage.value)
        self.ui.electroactions.addItem(
            "Terminate Connection", ElectroAction.Terminate.value)
        self.ui.electroactions.setVisible(False)
        self.ui.handleractiontype.setCurrentIndex(HandlerIndex.Shell.value)
        self.ui.temperaturespinbox.setValue(0)
        self.ui.operatorcombo.setCurrentIndex(0)
        self.ui.operatorcombo.clear()
        self.ui.operatorcombo.addItem(">", Operator.Greater.value)
        self.ui.operatorcombo.addItem("<", Operator.Lesser.value)
        self.ui.temperaturespinbox.setValue(50)
        self.ui.monitoringlabel.setVisible(False)

    def initialize_sampling_tab(self):
        self.ui.customnamecheckbox_2.setChecked(False)
        self.ui.filename2.setEnabled(False)
        self.ui.filepathtoolbutton.setEnabled(False)
        self.ui.filepathlineedit_2.clear()
        self.ui.fromspinbox.setValue(0)
        self.ui.tospinbox.setValue(200)
        self.ui.filename2.clear()
        self.ui.autoopenfilecheckbox.setChecked(False)

    def initialize_liveplot_tab(self):
        self.ui.filecheckbox.setChecked(False)
        self.ui.loggingcheckbox.setChecked(False)
        self.ui.customnamecheckbox.setEnabled(False)
        self.ui.filename.clear()
        self.ui.customnamecheckbox.setChecked(False)
        self.ui.liveplottingcheckbox.setChecked(True)
        self.ui.filename.setEnabled(False)
        self.ui.filepathlineedit.setEnabled(False)
        self.ui.filepathlineedit.clear()

    def make_connections(self):
        make_connection(self.ui.actionClose.triggered, self.close_application)
        #connect(self.ui.actionopen_settings.triggered, self.opensettingsdialog)
        make_connection(self.ui.actionRefresh_Devices.triggered, self.initialize_electro)
        make_connection(self.ui.actionClear_Device_List.triggered,
                self.fill_combo_with_none)
        make_connection(self.ui.filepathtoolbutton.clicked, self.select_file_path)
        make_connection(self.ui.filepathtoolbutton_2.clicked, self.select_file_path2)
        make_connection(self.ui.customnamecheckbox.clicked,
                self.custom_file_name_enabled)
        make_connection(self.ui.customnamecheckbox_2.clicked,
                self.custom_file_name_enabled2)
        make_connection(self.ui.actionStart_Plotting.triggered, self.start_main_procedure)
        make_connection(self.ui.filecheckbox.clicked, self.file_path_enabled)
        make_connection(self.ui.actionRestore_Tab.triggered, self.restore_tab_options)
        make_connection(self.ui.actionRestore_All.triggered, self.restore_all_options)
        make_connection(self.ui.actionOpen_Plot_File.triggered,
                self.render_plot_file)
        make_connection(self.ui.handleractiontype.currentIndexChanged,
                self.handler_index_changed)
        make_connection(self.ui.stopmonitorbutton.clicked, self.stop_monitoring_thread)

    def handler_index_changed(self):
        if self.ui.handleractiontype.currentIndex() == HandlerIndex.Shell.value:
            self.ui.electroactions.setVisible(False)
            self.ui.shellaction.setVisible(True)
            self.ui.printedmessage.setVisible(False)
        elif self.ui.handleractiontype.currentIndex() == HandlerIndex.Electro.value:
            self.ui.electroactions.setVisible(True)
            self.ui.shellaction.setVisible(False)
            self.ui.printedmessage.setVisible(True)
        else:
            pass

    def attach_keyboard_shortcuts(self):
        self.ui.actionClose.setShortcut("ctrl+q")
        self.ui.actionopen_settings.setShortcut("ctrl+p")
        self.ui.actionRefresh_Devices.setShortcut("ctrl+shift+r")

    def close_application(self):
        self.close()

#    def opensettingsdialog(self):
#        settingsdialog = SettingUI(maindlg=self)
#        ShowDialog(settingsdialog)

    def initialize_electro(self):
        check_call(
            "dmesg | grep tty|grep USB|rev|awk '{print $1}'|rev > devices.txt", shell=True)
        with open("devices.txt", "r") as f:
            devices = f.readlines()
        if len(devices) > 0:
            self.clear_combo()
            for dev in devices:
                self.add_device_to_combo(dev)
        else:
            self.fill_combo_with_none()

    def add_device_to_combo(self, dev):
        self.ui.selecteddevicecombobox.addItem("/dev/" + dev.replace("\n", ""))

    def fill_combo_with_none(self):
        self.clear_combo()
        self.ui.selecteddevicecombobox.addItem("None")

    def clear_combo(self):
        self.ui.selecteddevicecombobox.clear()

    def select_file_path(self):
        self.ui.filepathlineedit.setText(
            str(QFileDialog.getExistingDirectory(self, "Select Save path")))

    def select_file_path2(self):
        self.ui.filepathlineedit_2.setText(
            str(QFileDialog.getExistingDirectory(self, "Select Save path")))

    def custom_file_name_enabled2(self):
        self.ui.filename2.setEnabled(self.ui.customnamecheckbox_2.isChecked())

    def custom_file_name_enabled(self):
        self.ui.filename.setEnabled(
            self.ui.customnamecheckbox.isChecked() & self.ui.filecheckbox.isChecked())

    def file_path_enabled(self):
        self.ui.filepathlineedit.setEnabled(self.ui.filecheckbox.isChecked())
        self.ui.filepathtoolbutton.setEnabled(self.ui.filecheckbox.isChecked())
        self.ui.customnamecheckbox.setEnabled(self.ui.filecheckbox.isChecked())
        self.ui.filename.setEnabled(
            self.ui.filecheckbox.isChecked() and self.ui.customnamecheckbox.isChecked())

    def start_main_procedure(self):
        if self.ui.selecteddevicecombobox.findText("None"):
            if self.ui.monitoringlabel.isVisible():
                return
            selectedtab = self.ui.tabWidget.currentWidget()
            if selectedtab is self.ui.liveplottingtab:
                self.start_liveplotting()
            elif selectedtab is self.ui.samplingtab:
                self.start_sampling()
            elif selectedtab is self.ui.handlerstab:
                self.start_monitoring()
            else:
                print("unknown tab selected")
        else:
            show_message("There is no proper device selected")

    def start_liveplotting(self):
        if self.ui.liveplottingcheckbox.isChecked() or self.ui.loggingcheckbox.isChecked() or self.ui.filecheckbox.isChecked():
            print(__file__)
            Popen([self.get_python_version(), os.path.join(self.initfilepath, "MRenderer.py"),
                   str(RendererOperationsType.LivePlotting.value), self.ui.selecteddevicecombobox.currentText(),
                   self.ui.speedspinbox.text(), self.get_combined_file_name(), "None",
                   str(self.ui.loggingcheckbox.isChecked()), str(self.ui.filecheckbox.isChecked()), "None"])

    def start_sampling(self):
        print(__file__)
        check_call([self.get_python_version(), os.path.join(self.initfilepath, "MRenderer.py"),
                    str(RendererOperationsType.Sampling.value), self.ui.selecteddevicecombobox.currentText(),
                    self.ui.speedspinbox.text(), self.get_combined_file_name2(), self.ui.tospinbox.text(),
                    "None", "True", str(self.ui.autoopenfilecheckbox.isChecked())])

    def start_monitoring(self):
        ser = serial.Serial(self.ui.selecteddevicecombobox.currentText(
        ), self.ui.speedspinbox.text(), timeout=0.15)
        self.ui.monitoringlabel.setVisible(True)
        try:
            from Src.electro_threading import ThreadLooper
            monitorthread = ThreadLooper(lambda: self.execute_monitoring(ser, thread=self.monitorthread,
                                                                                 action=self.ui.electroactions.currentIndex(),
                                                                                 handleroperation=self.ui.handleractiontype.currentIndex(),
                                                                                 operator=self.ui.operatorcombo.currentIndex(),
                                                                                 threshold=self.ui.temperaturespinbox.value(),
                                                                                 message=self.ui.printedmessage.text(),
                                                                                 shell=self.ui.shellaction.text()), name="Monitoring Thread",
                                                  onfinishexecution=lambda: self.ui.monitoringlabel.setVisible(False))
            self.monitorthread = monitorthread
            monitorthread.run()

        finally:
            pass  # ser.close()

    def stop_monitoring_thread(self):
        self.ui.monitoringlabel.setVisible(False)
        if self.monitorthread is not None:
            self.monitorthread.finish_execution()

    def execute_monitoring(self, ser, thread, action, handleroperation, operator, threshold, message="", shell=""):
        try:
            value = float(ser.readline())

            if operator == Operator.Greater.value:
                if value > threshold:
                    self.execution_by_case(action=action, handleroperation=handleroperation,
                                       thread=thread, message=message, shell=shell)

            if operator == Operator.Lesser.value:
                if value < threshold:
                    self.execution_by_case(action=action, handleroperation=handleroperation,
                                       thread=thread, message=message, shell=shell)

            print(float(ser.readline()))
        except:
            pass

    def execution_by_case(self, action, handleroperation, thread, message="", shell=""):
        if handleroperation == HandlerIndex.Shell.value:
            print("entered "+shell)
            call(shell, shell=True)
            thread.finish_execution()
        elif action == ElectroAction.PrintMessage.value:
            print(message)
            thread.finish_execution()
        elif action == ElectroAction.Terminate.value:
            thread.finish_execution()

    def get_python_version(self) -> str:
        return "python3"

    def restore_all_options(self):
        self.initialize_widgets()

    def restore_tab_options(self):
        selectedtab = self.ui.tabWidget.currentWidget()
        if selectedtab is self.ui.liveplottingtab:
            self.initialize_liveplot_tab()
        elif selectedtab is self.ui.samplingtab:
            self.initialize_sampling_tab()
        elif selectedtab is self.ui.handlerstab:
            self.initialize_handling_tab()
        else:
            print("unknown tab selected")

    def get_combined_file_name(self):
        global filename
        if self.ui.customnamecheckbox.isChecked():
            filename = os.path.join(
                self.ui.filepathlineedit.text(), self.ui.filename.text())
            return filename
        else:
            filename = os.path.join(self.ui.filepathlineedit.text(
            ), "liveplottinglogging{0}.txt".format(uuid.uuid4()))
            return filename

    def get_combined_file_name2(self):
        global filename2
        if self.ui.customnamecheckbox_2.isChecked():
            filename2 = os.path.join(
                self.ui.filepathlineedit_2.text(), self.ui.filename2.text())
            return filename2
        else:
            filename2 = os.path.join(
                self.ui.filepathlineedit_2.text(), "sampling{0}.txt".format(uuid.uuid4()))
            return filename2

    def render_plot_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileNames()", "",
                                              "All Files (*)")
        if file:
            check_call([self.get_python_version(), os.path.join(self.initfilepath, "MRenderer.py"),
                        str(RendererOperationsType.OfflineRendering.value),
                        self.ui.selecteddevicecombobox.currentText(),
                        self.ui.speedspinbox.text(), file, "None",
                        "None", "True", "None"])
