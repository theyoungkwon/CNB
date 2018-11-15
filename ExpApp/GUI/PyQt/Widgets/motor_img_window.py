import sys
from enum import Enum

from PyQt5 import QtWidgets, QtCore, QtGui

from ExpApp.Utils.constants import TRIAL_STEPS, MI_CALIBRATION_TRIALS, EMG_TRIAL_STEPS, Device


class MI_TASK:
    # L left
    LEFT_HAND = 'L'
    # R right
    RIGHT_HAND = 'R'
    # D down
    FEET = 'D'
    # U up
    TONGUE = 'U'


class SEQUENCE:
    CALIBRATION = MI_TASK.LEFT_HAND * MI_CALIBRATION_TRIALS + \
                  MI_TASK.RIGHT_HAND * MI_CALIBRATION_TRIALS + \
                  MI_TASK.FEET * MI_CALIBRATION_TRIALS + \
                  MI_TASK.TONGUE * MI_CALIBRATION_TRIALS

    INPUT = (MI_TASK.LEFT_HAND) + \
            (MI_TASK.RIGHT_HAND) + \
            (MI_TASK.FEET) + \
            (MI_TASK.TONGUE) + \
            (MI_TASK.LEFT_HAND) + \
            (MI_TASK.LEFT_HAND) + \
            (MI_TASK.RIGHT_HAND) + \
            (MI_TASK.RIGHT_HAND) + \
            (MI_TASK.FEET) + \
            (MI_TASK.FEET) + \
            (MI_TASK.TONGUE) + \
            (MI_TASK.TONGUE)


TIME_INCREMENT = 250


class MotorImgWindow(QtWidgets.QWidget):
    def __init__(self, parent=None, device=Device.EMG, sequence=SEQUENCE.INPUT):
        super().__init__(parent=parent)

        self.points = {
            MI_TASK.LEFT_HAND: [-1, 0],
            MI_TASK.RIGHT_HAND: [1, 0],
            MI_TASK.FEET: [0, -1],
            MI_TASK.TONGUE: [0, 1],
        }

        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Text, QtCore.Qt.lightGray)
        palette.setColor(QtGui.QPalette.Background, QtCore.Qt.black)
        self.setPalette(palette)

        self.trial_timer = QtCore.QTimer(self)
        self.trial_timer.timeout.connect(self.manage_sequence)
        self.trial_timer.start(TIME_INCREMENT)

        self.sequence = sequence
        self.sequence_index = 0
        self.time = 0
        self.trial_step = 0

        self.arrow_color = QtCore.Qt.darkGreen
        self.tracker = EMG_TRIAL_STEPS() if device == Device.EMG else TRIAL_STEPS()

    def draw_arrow(self, painter, x, y):
        body = 150
        side = 180
        ts = 400

        tile = QtCore.QRectF(x - ts / 2, y - ts / 2, ts, ts)
        painter.fillRect(tile, QtCore.Qt.darkGray)

        d = (self.points[self.sequence[self.sequence_index]])
        path = QtGui.QPainterPath()
        path.moveTo(x + d[0] * side, y - d[1] * side)
        path.lineTo(x + (-1 if d[0] == 0 else 0) * side, y - (-1 if d[1] == 0 else 0) * side)
        path.lineTo(x + (1 if d[0] == 0 else 0) * side, y - (1 if d[1] == 0 else 0) * side)
        path.lineTo(x + d[0] * side, y - d[1] * side)
        painter.fillPath(path, self.arrow_color)

        arrow = QtCore.QRectF(x - body / 2, y - body / 2, body, body)
        painter.fillRect(arrow, self.arrow_color)

    def draw_cross(self, painter, x, y):
        tl = 300
        tw = 30
        vertical = QtCore.QRectF(x - tw / 2, y - tl / 2, tw, tl)
        horizontal = QtCore.QRectF(x - tl / 2, y - tw / 2, tl, tw)
        painter.fillRect(vertical, QtCore.Qt.darkGray)
        painter.fillRect(horizontal, QtCore.Qt.darkGray)

    def paintEvent(self, event):
        resolution = self.geometry()
        max_x = resolution.width()
        max_y = resolution.height()
        x = max_x / 2
        y = max_y / 2

        painter = QtGui.QPainter(self)
        painter.setPen(QtGui.QPen(QtCore.Qt.darkGray))

        if self.tracker.CROSS_START <= self.time < self.tracker.CROSS_END:
            self.draw_cross(painter, x, y)
        if self.tracker.CUE_START <= self.time < self.tracker.CUE_END:
            self.draw_arrow(painter, x, y)

        painter.drawText(QtCore.QRectF(0, 0, 200, 100), QtCore.Qt.AlignLeft, str(self.time))

    def manage_sequence(self):
        self.time += TIME_INCREMENT
        if self.time % self.tracker.TRIAL_END == 0:
            self.time = 0
            self.sequence_index += 1
            if self.sequence_index % MI_CALIBRATION_TRIALS == 0:
                self.arrow_color = QtCore.Qt.darkGreen if self.arrow_color == QtCore.Qt.darkRed else QtCore.Qt.darkRed
        self.update()


def main():
    app = QtWidgets.QApplication([])
    window = MotorImgWindow()
    window.showFullScreen()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
