import sys

from PyQt5 import QtWidgets, QtCore, QtGui

from ExpApp.Utils.constants import PINCODE_FLASH_DURATION, PINCODE_FLASH_INTERVAL


class PinCodeWindow(QtWidgets.QWidget):
    def __init__(self, parent=None,
                 sequence=None,
                 repetitions=1):
        super().__init__(parent=parent)
        self.is_flash = False
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background, QtCore.Qt.black)
        self.setPalette(palette)
        self.update()

        self.highlight_timer = QtCore.QTimer(self)
        self.highlight_timer.timeout.connect(self.next_highlight)
        self.highlight_timer.start(PINCODE_FLASH_INTERVAL)

        self.dim_timer = QtCore.QTimer(self)
        self.dim_timer.timeout.connect(self.dim)

        self.dim_delay_timer = QtCore.QTimer(self)
        self.dim_delay_timer.timeout.connect(self.delay_dim)
        self.dim_delay_timer.start(PINCODE_FLASH_DURATION)

        self.index = 0
        self.repetition = 0
        self.isHighlighted = False
        self.sequence = sequence
        self.repetitions = repetitions

    def delay_dim(self):
        self.dim_timer.start(PINCODE_FLASH_INTERVAL)
        self.dim_delay_timer.stop()

    def paintEvent(self, event):
        resolution = self.geometry()
        max_x = resolution.width()
        max_y = resolution.height()
        margin_left = (max_x - max_y) / 2
        tile_size = max_y / 3
        p = 20

        painter = QtGui.QPainter(self)
        painter.setFont(QtGui.QFont("Arial", 69))

        for number in range(9):
            x = int(number % 3) * tile_size + margin_left
            y = int(number / 3) * tile_size
            tile = QtCore.QRectF(x + p, y + p, tile_size - p, tile_size - p)

            if self.isHighlighted and self.sequence[self.index - 1] == number + 1:
                painter.fillRect(tile, QtCore.Qt.white)
            else:
                painter.fillRect(tile, QtCore.Qt.darkGray)

            painter.drawText(tile, QtCore.Qt.AlignCenter, str(number + 1))

    def next_highlight(self):
        self.isHighlighted = True
        self.update()
        if self.index < len(self.sequence):
            self.index += 1
        if self.index >= len(self.sequence):
            if self.repetition >= self.repetitions - 1:
                self.highlight_timer.stop()
            else:
                self.index = 0
                self.repetition += 1

    def dim(self):
        if self.isHighlighted:
            self.isHighlighted = False
            self.update()


def main():
    app = QtWidgets.QApplication([])
    window = PinCodeWindow(sequence=[1, 4, 8, 8], repetitions=3)
    window.showFullScreen()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
