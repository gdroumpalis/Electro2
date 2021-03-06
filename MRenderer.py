import sys
from audioop import avg
from numpy import *
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import serial
import datetime
import sys
import os
from Src.electro_threading import  ThreadLooper
from Utilities.Enums import RendererOperationsType
from Utilities.GlobalUtilities import release_resources

if __name__ == '__main__':
    def attach_to_global_thread_pool(looper):
        global thread_loopers
        thread_loopers.append(looper)

    def get_operation_method(argv: int):
        type = int(argv[1])
        if type == 1:
            return RendererOperationsType.LivePlotting
        elif type == 2:
            return RendererOperationsType.Sampling
        elif type == 3:
            return RendererOperationsType.Handling
        elif type == 4:
            return RendererOperationsType.OfflineRendering


    def open_file_with_proper_name():
        if get_file_loggin(sys.argv):
            return open(get_default_filepath(sys.argv), "w+")
        else:
            return None


    def get_device_name(argv):
        return argv[2]


    def get_baudrate(argv):
        if argv[3] == "None":
            return 1200
        else:
            return int(argv[3])


    def get_default_filepath(argv):
        if argv[4] == "None":
            return os.path.join(os.getcwd(), "sampling")
        else:
            return argv[4]


    def get_default_max_step(argv):
        if argv[5] == "None":
            return 200
        else:
            return int(argv[5])


    def get_terminal_logging(argv):
        if argv[6] == "None":
            return False
        else:
            if argv[6] == "True":
                return True
            else:
                return False


    def get_file_loggin(argv):
        if argv[7] == "None":
            return False
        else:
            if argv[7] == "True":
                return True
            else:
                return False


    def get_auto_offline_rendering(argv):
        if argv[8] == "None":
            return False
        else:
            if argv[8] == "True":
                return True
            else:
                return False


    thread_loopers = []
    ser = 0
    RendererOperation = get_operation_method(sys.argv)  # type: RendererOperationsType
    terminal_logging = get_terminal_logging(sys.argv)
    file_logging = get_file_loggin(sys.argv)
    device_name = get_device_name(sys.argv)
    baudrate = get_baudrate(sys.argv)
    filename = get_default_filepath(sys.argv)
    maxstep = get_default_max_step(sys.argv)
    auto_offline_rendering = get_auto_offline_rendering(sys.argv)
    if RendererOperation != RendererOperationsType.OfflineRendering:
        ser = serial.Serial(device_name, baudrate, timeout=0.15)
        opened_file = open_file_with_proper_name()
    print(RendererOperation.name)
    ### START QtApp #####
    if RendererOperation == RendererOperationsType.LivePlotting or auto_offline_rendering or RendererOperation== RendererOperationsType.OfflineRendering:
        app = QtGui.QApplication([])  # you MUST do this once (initialize things)
        win = pg.GraphicsWindow(title="Signal from serial port")  # creates a window
        p = win.addPlot(title="Temp plot")  # creates empty space for the plot in the window
        p2 = win.addPlot(title="Avg Temp Plot")
        curve = p.plot()  # create an empty "plot" (a curve to plot)
        curve2 = p2.plot()

    windowWidth = 500  # width of the window displaying the curve
    Xm = linspace(0, 0, windowWidth)  # create array that will contain the relevant time series
    Am = linspace(0, 0, windowWidth)
    ptr = 1  # set first x position


    # Realtime data plot. Each time this function is called, the data display is updated
    def live_plotting_execution_target(f, logging, file_logging, t):
        global curve, curve2, ptr, Xm, Am, ser
        Xm[:-1] = Xm[1:]  # shift data in the temporal mean 1 sample left
        Am[:-1] = Am[1:]
        value = ser.readline()  # read line (single value) from the serial port
        try:
            Xm[-1] = float(value)  # vector containing the instantaneous values
        except:
            Xm[-1] = 0.0

        if ptr <= 500:
            Am[-1] = sum(Xm) / ptr
        else:
            Am[-1] = sum(Xm) / len(Xm)
        if logging:
            print("current temp:{} , avg temp{}".format(Xm[-1], Am[-1]))

        if file_logging:
            if not f.closed:
                f.write("datetime:{} => current temp:{} , avg temp{}\n".format(datetime.datetime.now(), Xm[-1], Am[-1]))

        ptr += 1  # update x position for displaying the curve
        curve.setData(Xm)  # set the curve with this data
        curve.setPos(ptr, 1)  # set x position in the graph to 0
        curve2.setData(Am)
        curve2.setPos(ptr, 1)
        QtGui.QApplication.processEvents()  # you MUST process the plot now


    def sampling_execution_target(f):
        global ptr, Xm, Am, ser
        Xm[:-1] = Xm[1:]  # shift data in the temporal mean 1 sample left
        Am[:-1] = Am[1:]
        value = ser.readline()  # read line (single value) from the serial port
        try:
            Xm[-1] = float(value)  # vector containing the instantaneous values
        except:
            Xm[-1] = 0.0
        if ptr <= 500:
            Am[-1] = sum(Xm) / ptr
        else:
            Am[-1] = sum(Xm) / len(Xm)
        if not f.closed:
            f.write("{0},{1}\n".format(Xm[-1], Am[-1]))
        ptr += 1  # update x position for displaying the curve


    def handling_execution_target(f):
        global curve, curve2, ptr, Xm, Am
        Xm[:-1] = Xm[1:]  # shift data in the temporal mean 1 sample left
        Am[:-1] = Am[1:]
        value = ser.readline()  # read line (single value) from the serial port
        Xm[-1] = float(value)  # vector containing the instantaneous values
        if ptr <= 500:
            Am[-1] = sum(Xm) / ptr
        else:
            Am[-1] = sum(Xm) / len(Xm)
        print("current temp:{} , avg temp{}".format(Xm[-1], Am[-1]))
        # f.write("datetime:{} => current temp:{} , avg temp{}\n".format(datetime.datetime.now(), Xm[-1], Am[-1]))
        ptr += 1  # update x position for displaying the curve
        curve.setData(Xm)  # set the curve with this data
        curve.setPos(ptr, 1)  # set x position in the graph to 0
        curve2.setData(Am)
        curve2.setPos(ptr, 1)
        QtGui.QApplication.processEvents()  # you MUST process the plot now


    def offline_rendering(filepath):
        global curve, curve2
        print("offline filepath {0}".format(filepath))
        with open(filepath, "r") as offlinerenderingfile:
            lines = offlinerenderingfile.readlines()
        currenttemp = []
        avgtemp = []
        for line in lines:
            print(line)
            currenttemp.append(float(str(line).replace("\\n", "").split(",")[0]))
            avgtemp.append(float(str(line).replace("\\n", "").split(",")[1]))

        print(currenttemp)
        print(avgtemp)
        curve.setData(currenttemp)  # set the curve with this data
        curve2.setData(avgtemp)
        QtGui.QApplication.processEvents()
        print("exiting")
        offlinerenderingfile.close()


    if RendererOperation == RendererOperationsType.LivePlotting:
        renderlooper = ThreadLooper(lambda: live_plotting_execution_target(opened_file, terminal_logging, file_logging, True),
                                             name="Live Plotting Thread")
        renderlooper.run()
        attach_to_global_thread_pool(renderlooper)
        print("Plotting Started")

    elif RendererOperation == RendererOperationsType.Sampling:
        renderlooper = ThreadLooper(lambda: sampling_execution_target(opened_file), timeout=maxstep, name="Sampling Thread")
        attach_to_global_thread_pool(renderlooper)
        renderlooper.run()
        print("Sampling started")
        renderlooper.wait()
        opened_file.close()
        if auto_offline_rendering:
            print("entered")
            offline_rendering(filename)

    elif RendererOperation == RendererOperationsType.OfflineRendering:
        print("entered")
        print(filename)
        offline_rendering(filename)


    elif RendererOperation == RendererOperationsType.Handling: #Not Used
        pass

    else:
        raise Exception("Rendering prosses cannot start")

    if RendererOperation == RendererOperationsType.LivePlotting or auto_offline_rendering or RendererOperation == RendererOperationsType.OfflineRendering:
        print("executing")
        pg.QtGui.QApplication.instance().exec_()
        print("UI Proccess Ended")

    try:
        release_resources(ser , opened_file , thread_loopers)
    except:
        pass
