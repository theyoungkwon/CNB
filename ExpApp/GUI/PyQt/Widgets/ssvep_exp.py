import sys

from PyQt5 import QtWidgets, QtCore, QtGui

from ExpApp.Utils.constants import SSVEP_TIME_WINDOW, FREQ


class SSVEPExperimentWindow(QtWidgets.QWidget, QtCore.QObject):
    def __init__(self, frequencies=FREQ[1], parent=None):
        super().__init__(parent=parent)

        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background, QtCore.Qt.black)
        self.setPalette(palette)

        # parameters
        self.frequencies = frequencies

        # flickers
        self.flicker_state = []
        self.timers = []

        for i in range(len(self.frequencies)):
            self.flicker_state.append(False)
            timer = QtCore.QTimer(self)
            timer.timeout.connect(self.transformer(i))
            timer.start(int(1000 / self.frequencies[i]))

        # active
        self.active_index = 0
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.next_flicker)
        timer.start(SSVEP_TIME_WINDOW)

    def next_flicker(self):
        self.active_index += 1
        if self.active_index > len(self.frequencies) - 1:
            self.close()
            self.thread().exec()

    def transformer(self, i):
        def transform():
            self.flicker_state[i] = not self.flicker_state[i]
            self.update()

        return transform

    def paintEvent(self, event):
        resolution = self.geometry()
        max_x = resolution.width()
        max_y = resolution.height()
        radius = max_x / len(self.frequencies) / 2

        painter = QtGui.QPainter(self)

        # flickers
        for number in range(len(self.frequencies)):
            x = (max_x / len(self.frequencies)) * number
            y = max_y / 2

            if (number == self.active_index):
                painter.setBrush(QtCore.Qt.darkGreen)
                painter.drawEllipse(QtCore.QPoint(x + radius, y), radius - 40, radius - 40)

            if self.flicker_state[number]:
                painter.setBrush(QtCore.Qt.white)
            else:
                painter.setBrush(QtCore.Qt.black)

            painter.drawEllipse(QtCore.QPoint(x + radius, y), radius - 50, radius - 50)


def main():
    app = QtWidgets.QApplication([])
    window = SSVEPExperimentWindow(frequencies=FREQ[int(sys.argv[1])])
    window.showFullScreen()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
