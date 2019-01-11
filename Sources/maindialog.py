from pickle import FALSE

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QListWidgetItem, QMessageBox, QFileDialog
import UI.mainui
from Utilities.GlobalUtilities import *
from Sources.settingsdialog import SettingUI
from subprocess import check_call, call, Popen
import os
import uuid
import serial


class RendererOperationsType(Enum):
    LivePlotting = 1
    Sampling = 2
    Handling = 3
    OfflineRendering = 4


class HandlerIndex(Enum):
    Shell = 0
    Electro = 1


class Operator(Enum):
    Greater = 0
    Lesser = 1


class ElectroAction(Enum):
    PrintMessage = 0
    Terminate = 1


filename2 = ""
filename = ""

class MainUI(QMainWindow):
    RunsOnRaspberry = False

    def __init__(self, rasp, initfilepath):
        """

        :type runsonraspberry: bool
        """
        super().__init__()
        self.initfilepath = initfilepath
        self.monitorthread = None
        self.ui = UI.mainui.Ui_MainWindow()
        MainUI.RunsOnRaspberry = rasp
        self.ui.setupUi(self)
        self.initializeMainWindowSize()
        self.initializeelectro()
        self.connectuicomponetstosignal()
        self.attachkeyboardshortcuts()
        self.initializewidgets()

    def initializeMainWindowSize(self):
        if not MainUI.RunsOnRaspberry:
            self.resize(QSize(1600, 900))

    def initializewidgets(self):
        self.initializeliveplottingtab()
        self.initializesamplingtab()
        self.initializehandlertab()

    def initializehandlertab(self):
        self.stopmonitorthread()
        self.ui.printedmessage.clear()
        self.ui.electroactions.clear()
        self.ui.handleractiontype.clear()
        self.ui.handleractiontype.addItem("Shell Script", HandlerIndex.Shell.value)
        self.ui.handleractiontype.addItem("Electro Action", HandlerIndex.Electro.value)
        self.ui.electroactions.addItem("Print Message", ElectroAction.PrintMessage.value)
        self.ui.electroactions.addItem("Terminate Connection", ElectroAction.Terminate.value)
        self.ui.electroactions.setVisible(False)
        self.ui.handleractiontype.setCurrentIndex(HandlerIndex.Shell.value)
        self.ui.temperaturespinbox.setValue(0)
        self.ui.operatorcombo.setCurrentIndex(0)
        self.ui.operatorcombo.clear()
        self.ui.operatorcombo.addItem(">", Operator.Greater.value)
        self.ui.operatorcombo.addItem("<", Operator.Lesser.value)
        self.ui.temperaturespinbox.setValue(50)
        self.ui.monitoringlabel.setVisible(False)

    def initializesamplingtab(self):
        self.ui.customnamecheckbox_2.setChecked(False)
        self.ui.filename2.setEnabled(False)
        self.ui.filepathtoolbutton.setEnabled(False)
        self.ui.filepathlineedit_2.clear()
        self.ui.fromspinbox.setValue(0)
        self.ui.tospinbox.setValue(200)
        self.ui.filename2.clear()
        self.ui.autoopenfilecheckbox.setChecked(False)

    def initializeliveplottingtab(self):
        self.ui.filecheckbox.setChecked(False)
        self.ui.loggingcheckbox.setChecked(False)
        self.ui.customnamecheckbox.setEnabled(False)
        self.ui.filename.clear()
        self.ui.customnamecheckbox.setChecked(False)
        self.ui.liveplottingcheckbox.setChecked(True)
        self.ui.filename.setEnabled(False)
        self.ui.filepathlineedit.setEnabled(False)
        self.ui.filepathlineedit.clear()

    def connectuicomponetstosignal(self):
        connect(self.ui.actionClose.triggered, self.closeapplication)
        connect(self.ui.actionopen_settings.triggered, self.opensettingsdialog)
        connect(self.ui.actionRefresh_Devices.triggered, self.initializeelectro)
        connect(self.ui.actionClear_Device_List.triggered, self.fillcombowithnone)
        connect(self.ui.filepathtoolbutton.clicked, self.selectfilepath)
        connect(self.ui.filepathtoolbutton_2.clicked, self.selecteddevice2)
        connect(self.ui.customnamecheckbox.clicked, self.setcustomfilenameenabled)
        connect(self.ui.customnamecheckbox_2.clicked, self.setcustomfilenameenabled2)
        connect(self.ui.actionStart_Plotting.triggered, self.startmainproc)
        connect(self.ui.filecheckbox.clicked, self.setfilepathenabled)
        connect(self.ui.actionRestore_Tab.triggered, self.restoretaboptions)
        connect(self.ui.actionRestore_All.triggered, self.restorealloptions)
        connect(self.ui.actionOpen_Plot_File.triggered, self.offlinerenderopenedplotfile)
        connect(self.ui.handleractiontype.currentIndexChanged, self.handlerindexchanged)
        connect(self.ui.stopmonitorbutton.clicked, self.stopmonitorthread)

    def handlerindexchanged(self):
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

    def attachkeyboardshortcuts(self):
        self.ui.actionClose.setShortcut("ctrl+q")
        self.ui.actionopen_settings.setShortcut("ctrl+p")
        self.ui.actionRefresh_Devices.setShortcut("ctrl+shift+r")

    def closeapplication(self):
        self.close()

    def opensettingsdialog(self):
        settingsdialog = SettingUI(maindlg=self)
        ShowDialog(settingsdialog)

    def initializeelectro(self):
        check_call("dmesg | grep tty|grep USB|rev|awk '{print $1}'|rev > devices.txt", shell=True)
        with open("devices.txt", "r") as f:
            devices = f.readlines()
        if len(devices) > 0:
            self.clearcombo()
            for dev in devices:
                self.deviceaddtocombo(dev)
        else:
            self.fillcombowithnone()

    def deviceaddtocombo(self, dev):
        self.ui.selecteddevicecombobox.addItem("/dev/" + dev.replace("\n", ""))

    def fillcombowithnone(self):
        self.clearcombo()
        self.ui.selecteddevicecombobox.addItem("None")

    def clearcombo(self):
        self.ui.selecteddevicecombobox.clear()

    def selectfilepath(self):
        self.ui.filepathlineedit.setText(str(QFileDialog.getExistingDirectory(self, "Select Save path")))

    def selecteddevice2(self):
        self.ui.filepathlineedit_2.setText(str(QFileDialog.getExistingDirectory(self, "Select Save path")))

    def setcustomfilenameenabled2(self):
        self.ui.filename2.setEnabled(self.ui.customnamecheckbox_2.isChecked())

    def setcustomfilenameenabled(self):
        self.ui.filename.setEnabled(self.ui.customnamecheckbox.isChecked() & self.ui.filecheckbox.isChecked())

    def setfilepathenabled(self):
        self.ui.filepathlineedit.setEnabled(self.ui.filecheckbox.isChecked())
        self.ui.filepathtoolbutton.setEnabled(self.ui.filecheckbox.isChecked())
        self.ui.customnamecheckbox.setEnabled(self.ui.filecheckbox.isChecked())
        self.ui.filename.setEnabled(self.ui.filecheckbox.isChecked() and self.ui.customnamecheckbox.isChecked())

    def startmainproc(self):
        if self.ui.selecteddevicecombobox.findText("None"):
            if self.ui.monitoringlabel.isVisible():
                return
            selectedtab = self.ui.tabWidget.currentWidget()
            if selectedtab is self.ui.liveplottingtab:
                self.startliveplotting()
            elif selectedtab is self.ui.samplingtab:
                self.startsampling()
            elif selectedtab is self.ui.handlerstab:
                self.startmonitoring()
            else:
                print("unknown tab selected")
        else:
            self.showmessagebox("There is no proper device selected")

    def startliveplotting(self):
        if self.ui.liveplottingcheckbox.isChecked() or self.ui.loggingcheckbox.isChecked() or self.ui.filecheckbox.isChecked():
            print(__file__)
            Popen([self.getpythonversion(), os.path.join(self.initfilepath, "Renderer/MRenderer.py"),
                   str(RendererOperationsType.LivePlotting.value), self.ui.selecteddevicecombobox.currentText(),
                   self.ui.speedspinbox.text(), self.getcompbinedfilename(), "None",
                   str(self.ui.loggingcheckbox.isChecked()), str(self.ui.filecheckbox.isChecked()), "None"])

    def startsampling(self):
        print(__file__)
        check_call([self.getpythonversion(), os.path.join(self.initfilepath, "Renderer/MRenderer.py"),
                    str(RendererOperationsType.Sampling.value), self.ui.selecteddevicecombobox.currentText(),
                    self.ui.speedspinbox.text(), self.getcompbinedfilename2(), self.ui.tospinbox.text(),
                    "None", "True", str(self.ui.autoopenfilecheckbox.isChecked())])

    def startmonitoring(self):
        ser = serial.Serial(self.ui.selecteddevicecombobox.currentText(), self.ui.speedspinbox.text(), timeout=0.15)
        self.ui.monitoringlabel.setVisible(True)
        try:
            from Renderer.MRenderer import RenderingThreadLooper
            monitorthread = RenderingThreadLooper(lambda: self.executemonitoring(ser, thread=self.monitorthread,
                                                                                 action=self.ui.electroactions.currentIndex(),
                                                                                 handleroperation=self.ui.handleractiontype.currentIndex(),
                                                                                 operator=self.ui.operatorcombo.currentIndex(),
                                                                                 threshold=self.ui.temperaturespinbox.value(),
                                                                                 message=self.ui.printedmessage.text(),
                                                                                 shell=self.ui.shellaction.text())
                                                                                , name="Monitoring Thread" ,
                                                    onfinishexecution=lambda: self.ui.monitoringlabel.setVisible(False) )
            self.monitorthread = monitorthread
            monitorthread.run()

        finally:
            pass  # ser.close()

    def stopmonitorthread(self):
        self.ui.monitoringlabel.setVisible(False)
        if self.monitorthread is not None:
            self.monitorthread.finishexecution()

    def executemonitoring(self, ser, thread, action, handleroperation ,operator, threshold, message="", shell=""):
        try:
            value = float(ser.readline())

            if operator == Operator.Greater.value:
                if value > threshold:
                    self.executioncase(action=action, handleroperation=handleroperation ,thread=thread, message=message, shell=shell)

            if operator == Operator.Lesser.value:
                if value < threshold:
                    self.executioncase(action= action,handleroperation=handleroperation ,thread=thread, message=message, shell=shell)

            print(float(ser.readline()))
        except:
            pass

    def executioncase(self, action, handleroperation, thread, message="", shell=""):
        if handleroperation == HandlerIndex.Shell.value:
            print("entered "+shell)
            call(shell , shell=True)
            thread.finishexecution()
        elif action == ElectroAction.PrintMessage.value:
            print(message)
            thread.finishexecution()
        elif action == ElectroAction.Terminate.value:
            thread.finishexecution()

    def getpythonversion(self) -> str:
        if MainUI.RunsOnRaspberry:
            return "python3"
        else:
            return "python35"

    def showmessagebox(self, message):
        msg = QMessageBox()
        msg.setText(message)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()

    def restorealloptions(self):
        self.initializewidgets()

    def restoretaboptions(self):
        selectedtab = self.ui.tabWidget.currentWidget()
        if selectedtab is self.ui.liveplottingtab:
            self.initializeliveplottingtab()
        elif selectedtab is self.ui.samplingtab:
            self.initializesamplingtab()
        elif selectedtab is self.ui.handlerstab:
            self.initializehandlertab()
        else:
            print("unknown tab selected")

    def getcompbinedfilename(self):
        global filename
        if self.ui.customnamecheckbox.isChecked():
            filename = os.path.join(self.ui.filepathlineedit.text(), self.ui.filename.text())
            return filename
        else:
            filename = os.path.join(self.ui.filepathlineedit.text(), "liveplottinglogging{0}.txt".format(uuid.uuid4()))
            return filename

    def getcompbinedfilename2(self):
        global filename2
        if self.ui.customnamecheckbox_2.isChecked():
            filename2 = os.path.join(self.ui.filepathlineedit_2.text(), self.ui.filename2.text())
            return filename2
        else:
            filename2 = os.path.join(self.ui.filepathlineedit_2.text(), "sampling{0}.txt".format(uuid.uuid4()))
            return filename2

    def offlinerenderopenedplotfile(self):
        file, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileNames()", "",
                                              "All Files (*)")
        if file:
            print(file)
            check_call([self.getpythonversion(), os.path.join(self.initfilepath, "Renderer/MRenderer.py"),
                        str(RendererOperationsType.OfflineRendering.value),
                        self.ui.selecteddevicecombobox.currentText(),
                        self.ui.speedspinbox.text(), file, "None",
                        "None", "True", "None"])
