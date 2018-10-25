import sys

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QThread

from ExpApp.Utils.constants import INPUT_DURATION, PROGRESS_UPDATE_TIME, SEQUENCE_LENGTH

frequencies = [10, 20, 25, 40]
# frequencies = [4, 5, 10, 20]
update = 5


class SSVEP_PincodeWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # thread = QThread()
        # thread.start(priority=QThread.HighestPriority)
        # self.moveToThread(thread)

        self.is_flash = False
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background, QtCore.Qt.black)
        self.setPalette(palette)
        self.update()

        # flickers
        self.is_black = [False, False, False, False]
        self.timer_draw = QtCore.QTimer(self)
        self.timer_draw.timeout.connect(self.flicker)

        self.timer_draw.start(update)
        self.iteration = 0

        # input sequence
        self.input_step = 1
        self.progress = 0

        # self.showFullScreen()

    def paintEvent(self, event):
        resolution = self.geometry()
        max_x = resolution.width()
        max_y = resolution.height()
        margin_left = (max_x - max_y) / 2
        tile_size = max_y / 2
        p = 20

        painter = QtGui.QPainter(self)
        painter.setFont(QtGui.QFont("Arial", 69))

        # step progress
        side_x = max_x * self.progress
        side_y = side_x
        mid_x = max_x / 2
        mid_y = max_y / 2
        progress_display = QtCore.QRectF(mid_x - side_x / 2, mid_y - side_y / 2, side_x, side_y)
        color = QtCore.Qt.darkRed if  self.progress > 0.9 else QtCore.Qt.darkGreen
        painter.fillRect(progress_display, color)

        # flickers
        for number in range(4):
            x = int(number % 2) * tile_size + margin_left
            y = int(number / 2) * tile_size
            tile = QtCore.QRectF(x + p, y + p, tile_size - p, tile_size - p)

            if self.is_black[number]:
                painter.fillRect(tile, QtCore.Qt.darkGray)
            else:
                painter.fillRect(tile, QtCore.Qt.white)

            painter.drawText(tile, QtCore.Qt.AlignCenter, str(number + 1))

    def flicker(self):
        current_time = self.iteration * update
        for freq, i in zip(frequencies, range(4)):
            if current_time % (1000 / freq) == 0:
                self.is_black[i] = not self.is_black[i]

        if current_time % INPUT_DURATION == 0:
            self.progress = 0
        if current_time % PROGRESS_UPDATE_TIME == 0:
            self.progress += PROGRESS_UPDATE_TIME / INPUT_DURATION

        self.update()

        self.iteration += 1

        if current_time == INPUT_DURATION * SEQUENCE_LENGTH:
            self.close()
            self.thread().exec()


def main():
    app = QtWidgets.QApplication([])
    window = SSVEP_PincodeWindow()
    window.showFullScreen()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
