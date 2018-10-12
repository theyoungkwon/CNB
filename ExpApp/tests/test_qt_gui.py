from ExpApp.API.OBCIConnector import OBCIConnector
from ExpApp.Utils.constants import CHANNELS_NUMBER, GRAPH_PROPORTION

import sys
from PyQt5 import QtGui, QtWidgets
from PyQt5 import QtCore
import numpy as np
import matplotlib

matplotlib.use("Qt4Agg")
from matplotlib.figure import Figure
from matplotlib.animation import TimedAnimation
from matplotlib.lines import Line2D
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import threading


class CustomMainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(CustomMainWindow, self).__init__()

        # Define the geometry of the main window
        self.setGeometry(300, 300, 800, 400)
        self.setWindowTitle("ExpApp")

        # Create FRAME_A
        self.LAYOUT_A = QtWidgets.QGridLayout()
        self.FRAME_A = QtWidgets.QFrame(self)
        self.FRAME_A.setStyleSheet("QWidget { background-color: %s }" % QtGui.QColor(210, 210, 235, 255).name())
        self.FRAME_A.setLayout(self.LAYOUT_A)
        self.setCentralWidget(self.FRAME_A)

        # Place the matplotlib figure
        self.myFig = CustomFigCanvas()
        self.LAYOUT_A.addWidget(self.myFig, *(0, 1))

        # Add the callbackfunc to ..
        myDataLoop = threading.Thread(name='myDataLoop', target=dataSendLoop, daemon=True,
                                      args=(self.addData_callbackFunc,))
        myDataLoop.start()

        self.show()

    def addData_callbackFunc(self, value):
        self.myFig.addData(value)


class CustomFigCanvas(FigureCanvas, TimedAnimation):

    def __init__(self):

        self.addedData = []

        self.subplots = []
        self.lines = []
        self.line_heads = []
        self.line_tails = []

        print(matplotlib.__version__)

        # The data
        self.xlim = 200
        self.n = np.linspace(0, self.xlim - 1, self.xlim)
        a = []
        b = []
        a.append(2.0)
        a.append(4.0)
        a.append(2.0)
        b.append(4.0)
        b.append(3.0)
        b.append(4.0)
        self.y = []
        for i in range(CHANNELS_NUMBER):
            self.y.append((self.n * 0.0) + 50)

        # The window
        self.fig = Figure(figsize=(5, 5), dpi=100)

        self.subplots = []
        for i in range(CHANNELS_NUMBER):
            line = Line2D([], [], color='blue')
            line_tail = Line2D([], [], color='red', linewidth=2)
            line_head = Line2D([], [], color='red', marker='o', markeredgecolor='r')

            subplot = self.fig.add_subplot(CHANNELS_NUMBER, 1, i + 1)
            subplot.add_line(line)
            subplot.add_line(line_tail)
            subplot.add_line(line_head)
            subplot.set_xlim(0, self.xlim - 1)

            self.lines.append(line)
            self.line_heads.append(line_head)
            self.line_tails.append(line_tail)
            self.subplots.append(subplot)

        self.sample_num = 0

        FigureCanvas.__init__(self, self.fig)
        TimedAnimation.__init__(self, self.fig, interval=16, blit=True)

    def new_frame_seq(self):
        return iter(range(self.n.size))

    def _init_draw(self):
        for i in range(len(self.subplots)):
            for l in [self.lines[i], self.line_tails[i], self.line_heads[i]]:
                l.set_data([], [])

    def addData(self, value):
        self.addedData.append(value)

        update_axis_interval = 3
        self.sample_num = self.sample_num + 1
        if self.sample_num % update_axis_interval == 0:
            for i in range(0, len(self.subplots)):
                v = float(value[i])
                self.subplots[i].set_ylim(v + v * GRAPH_PROPORTION, v - v * GRAPH_PROPORTION)

    def _step(self, *args):
        try:
            TimedAnimation._step(self, *args)
        except Exception as e:
            self.abc += 1
            print(str(self.abc))
            TimedAnimation._stop(self)
            pass

    def _draw_frame(self, framedata):
        margin = 2

        while len(self.addedData) > 0:
            for i in range(len(self.subplots)):
                self.y[i] = np.roll(self.y[i], -1)
                self.y[i][-1] = self.addedData[0][i]
            del (self.addedData[0])

        self._drawn_artists = []
        for i in range(len(self.subplots)):
            line = self.lines[i]
            tail = self.line_tails[i]
            head = self.line_heads[i]

            line.set_data(self.n[0: self.n.size - margin], self.y[i][0: self.n.size - margin])
            tail.set_data(np.append(self.n[-10:-1 - margin], self.n[-1 - margin]),
                          np.append(self.y[i][-10:-1 - margin], self.y[i][-1 - margin]))
            head.set_data(self.n[-1 - margin], self.y[i][-1 - margin])

            self._drawn_artists.append(line)
            self._drawn_artists.append(tail)
            self._drawn_artists.append(head)

def dataSendLoop(addData_callbackFunc):
    communicator = Communicate()
    communicator.data_signal.connect(addData_callbackFunc)

    # reader = ReadSample()
    # sample = reader.read_sample()
    #
    # while sample is not None:
    #     time.sleep(1. / 255.)
    #     value = sample.channel_data
    #     communicator.data_signal.emit(value)
    #     sample = reader.read_sample()

    board = OBCIConnector()
    board.attach_handlers(lambda sample: communicator.data_signal.emit(sample.channel_data))


class Communicate(QtCore.QObject):
    data_signal = QtCore.pyqtSignal(list)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myGUI = CustomMainWindow()
    sys.exit(app.exec_())
