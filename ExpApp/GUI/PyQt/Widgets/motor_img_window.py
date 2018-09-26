import sys

from PyQt5 import QtWidgets, QtCore, QtGui

from ExpApp.Utils.constants import IMG_EVENT_INTERVAL, IMG_EVENT_REPETITIONS


class MotorImgWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.is_flash = False
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Text, QtCore.Qt.lightGray)
        palette.setColor(QtGui.QPalette.Background, QtCore.Qt.black)
        self.setPalette(palette)
        self.event_timer = QtCore.QTimer(self)
        self.event_timer.timeout.connect(self.draw_event)
        self.event_timer.start(IMG_EVENT_INTERVAL)
        self.action_type = True  # Real = True, Imaginary = False
        self.action_direction = True  # True - right, false - left

        self.sequence = "RL" * IMG_EVENT_REPETITIONS + "RL" * IMG_EVENT_REPETITIONS
        self.index = 0

    # True - right, false - left
    def draw_triangle(self, painter, x, y, direction, color):
        path = QtGui.QPainterPath()
        side = 80
        path.moveTo(x, y - side)
        path.lineTo(x, y + side)
        path.lineTo(x + 2 * side * (1 if direction else -1), y)
        path.lineTo(x, y - side)
        painter.fillPath(path, color)

    def paintEvent(self, event):
        resolution = self.geometry()
        max_x = resolution.width()
        max_y = resolution.height()
        x = max_x / 2
        y = max_y / 2

        m = 20  # margin
        ts = 400  # tile_size
        arx = 200  # arrow body length
        ary = 60  # arrow body height

        la_arrow = QtCore.Qt.darkRed  # left arrow active color
        ra_arrow = QtCore.Qt.darkGreen  # right arrow active color
        i_arrow = QtCore.Qt.black  # inactive arrow color
        a_tile = QtCore.Qt.lightGray  # active tile color
        i_tile = QtCore.Qt.darkGray  # inactive tile color

        rac = ra_arrow if self.action_direction else i_arrow
        rtc = a_tile if self.action_direction else i_tile

        lac = la_arrow if not self.action_direction else i_arrow
        ltc = a_tile if not self.action_direction else i_tile

        painter = QtGui.QPainter(self)
        left_tile = QtCore.QRectF(x - m - ts, y - ts / 2, ts, ts)
        right_tile = QtCore.QRectF(x + m, y - ts / 2, ts, ts)
        left_arrow = QtCore.QRectF(x - 2 * m - arx, y - ary / 2, arx, ary)
        right_arrow = QtCore.QRectF(x + 2 * m, y - ary / 2, arx, ary)

        # right
        painter.fillRect(right_tile, rtc)
        painter.fillRect(right_arrow, rac)
        self.draw_triangle(painter, x + m + arx, y, True, rac)

        # left
        painter.fillRect(left_tile, ltc)
        painter.fillRect(left_arrow, lac)
        self.draw_triangle(painter, x - m - arx, y, False, lac)

        # Text
        painter.setFont(QtGui.QFont("Arial", 50))

        text_tile = QtCore.QRectF(x - 2 * ts, m, ts * 4, ts)
        painter.setPen(QtGui.QPen(QtCore.Qt.lightGray))
        text = ("PERFORM" if self.action_type else "IMAGINE") + " " + \
               ("RIGHT" if self.action_direction else "LEFT") + " HAND MOVEMENT"
        painter.drawText(text_tile, QtCore.Qt.AlignCenter, text)

    def draw_event(self):
        self.action_direction = not self.action_direction
        self.index += 1
        if self.index == IMG_EVENT_REPETITIONS - 1:
            self.action_type = False
        elif self.index == IMG_EVENT_REPETITIONS * 2 - 1:
            self.event_timer.stop()
        self.update()


def main():
    app = QtWidgets.QApplication([])
    window = MotorImgWindow()
    window.showFullScreen()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
