import os
import sys
import threading

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from EMG.EMGConnector import EMGConnector
from ExpApp.Utils.constants import BACKGROUND_COLOR
from ExpApp.datacore.EMG.EMG_CNN import EMG_CNN
from ExpApp.datacore.EMG.EMGWindowSlicer import EMGWindowSlicer


class Communicate(QtCore.QObject):
    data_signal = QtCore.pyqtSignal(list)


class GestureWidget(QWidget):
    def __init__(self, data_handler=None, parent=None, q=None):
        self.communicator = Communicate()
        my_data_loop = threading.Thread(name='my_data_loop', target=self.data_send_loop, daemon=True,
                                        args=(self.receive_data,))
        my_data_loop.start()
        QWidget.__init__(self, parent=parent)
        lay = QVBoxLayout(self)
        self.setGeometry(1230, 320, 256, 256)
        self.path = os.getcwd() + "/../GUI/PyQt/res/"
        self.setStyleSheet("background-color: " + BACKGROUND_COLOR + ";")
        self.data_handler = data_handler
        self.img = QPixmap(self.path + "PALM.png").scaled(256, 256)
        self.pic = QLabel()
        self.pic.setPixmap(self.img)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.q = q

        lay.addWidget(self.pic)
        self.show()

    def data_send_loop(self, add_data_callback_func):
        self.communicator.data_signal.connect(add_data_callback_func)
        EMGConnector(self.communicator)

    def receive_data(self, data):
        # additional timestamp is received from main_window communicator
        name = self.data_handler.handle_record(data[:-1])
        # name = self.data_handler.handle_record(data)
        if name is not None:
            self.redraw(name)
            if self.q is not None:
                self.q.put([name])

    def redraw(self, name):
        self.img = QPixmap(self.path + name + ".png").scaled(256, 256)
        self.pic.setPixmap(self.img)
        self.update()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


def gesture_widget_main(q=None):
    app = QtWidgets.QApplication([])
    sys.excepthook = except_hook
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    cfg = {
        "start": 0,
        "end": 200,
        "dir": "CNN_EXPORT",
        # "dir": "CNN_YOUNG_0_200____",
        "shift": 160
    }
    clf = EMG_CNN.load(cfg["dir"], params=cfg)
    data_handler = EMGWindowSlicer(clf, start=cfg["start"], end=cfg["end"], shift=cfg["shift"])
    GestureWidget(data_handler=data_handler, q=q)
    sys.exit(app.exec_())


if __name__ == '__main__':
    gesture_widget_main()
