import sys

from PyQt5 import QtWidgets, QtCore, QtGui

FREQ = 1000 / 30


class SSVEPWindow(QtWidgets.QWidget):
    def __init__(self, freq=FREQ, parent=None):
        super().__init__(parent=parent)
        self.is_black = False
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background, QtCore.Qt.white)
        self.setPalette(palette)
        self.timer_draw = QtCore.QTimer(self)
        self.timer_draw.timeout.connect(self.flicker)
        self.timer_draw.start(freq)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setPen(QtCore.Qt.black)
        resolution = self.geometry()
        x = resolution.width()
        y = resolution.height()
        if self.is_black:
            painter.fillRect(QtCore.QRectF(0, 0, x, y), QtCore.Qt.black)

    def flicker(self):
        self.is_black = not self.is_black
        self.update()


def main():
    app = QtWidgets.QApplication([])
    window = SSVEPWindow()
    window.showFullScreen()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
