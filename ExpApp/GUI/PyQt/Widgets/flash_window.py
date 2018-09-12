import sys

from PyQt5 import QtWidgets, QtCore, QtGui

from ExpApp.Utils.constants import FLASH_START, FLASH_END


class FlashWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.is_flash = False
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background, QtCore.Qt.black)
        self.setPalette(palette)
        self.timer_white = QtCore.QTimer(self)
        self.timer_white.timeout.connect(self.white)
        self.timer_white.start(FLASH_START)
        self.timer_black = QtCore.QTimer(self)
        self.timer_black.timeout.connect(self.black)
        self.timer_black.start(FLASH_END)

    def paintEvent(self, event):
        resolution = self.geometry()
        x = resolution.width()
        y = resolution.height()
        rect = QtCore.QRectF(0, 0, x, y)
        painter = QtGui.QPainter(self)
        if self.is_flash:
            painter.fillRect(rect, QtCore.Qt.white)
        if not self.is_flash:
            painter.fillRect(rect, QtCore.Qt.black)

    def white(self):
        self.is_flash = True
        self.update()
        self.timer_white.stop()

    def black(self):
        self.is_flash = False
        self.update()
        self.timer_black.stop()


def main():
    app = QtWidgets.QApplication([])
    window = FlashWindow()
    window.showFullScreen()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
