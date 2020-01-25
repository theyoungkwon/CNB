import os
import sys
import threading

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from EMG.EMGConnector import EMGConnector
from ExpApp.Utils import IMUUtils

from ExpApp.Utils.EasyPredictor import EasyPredictor
from ExpApp.Utils.VKeyboard import VKeyboard
from ExpApp.Utils.datacore_constants import INPUT_SET, KeyboardControl


class Communicate(QObject):
    data_signal = pyqtSignal(list)


SENSITIVITY = 5
MIN_ANGLE = 30
MAX_ANGLE = 150
PICKER_THICKNESS = 2
ARC_START_Y = 220
MAX_W = 500
MAX_H = 500
ARC_DIAMETER = 400
BAR_W = 240
BAR_H = 200
BAR_FONT_SIZE = 30
_BLUE_COLOR = 0x3498DB


class MyoKeyWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.roll = 5
        self.initUI()
        self.initCommunicators()
        self.frame = 1
        self.gesture = None
        self.vkeyboard = VKeyboard()
        model_path = os.path.dirname(__file__) + "/../../../datacore/cnn_qwerty_release"
        self.predictor = EasyPredictor(_set=INPUT_SET, model_path=model_path)
        self.bar_height = self.vkeyboard.max_votes
        self.bar_height_step = BAR_H / self.bar_height
        self.bar_width_step = BAR_W / self.vkeyboard.block_size
        self.delete_votes = 0

    def initUI(self):

        path = os.path.dirname(__file__) + "/img/keyboard.png"
        self.setStyleSheet("background: url(" + path + ")  no-repeat center center fixed; background-color: white;")

        self.rPickerHolder = QLabel(self)
        self.setStyleSheet("background: white")
        self.rPickerPixmap = QPixmap(MAX_W, MAX_H)
        self.rPickerPixmap.fill(QColor.fromRgb(_BLUE_COLOR))
        self.rPickerHolder.setGeometry(0, 0, MAX_W, 400)
        self.rPickerHolder.setPixmap(self.rPickerPixmap)

        self.inputDisplay = QLineEdit(self)
        self.inputDisplay.setText("")
        self.inputDisplay.setGeometry(50, 50, MAX_W - 100, 50)
        self.inputDisplay.setStyleSheet("background: none")
        fontParam = self.inputDisplay.font()
        fontParam.setPointSize(27)
        self.inputDisplay.setFont(fontParam)

        self.barHolder = QLabel(self)
        self.barHolder.setGeometry(125, ARC_START_Y, BAR_W + 10, BAR_H + 100)
        self.barHolder.setStyleSheet("background: none")
        self.barPixmap = QPixmap(BAR_W + 10, BAR_H)
        self.barPixmap.fill(Qt.transparent)
        self.barHolder.setPixmap(self.barPixmap)

        self.gestureHolder = QLabel(self)
        self.gestureHolder.setGeometry(210, 188, 80, 80)
        self.gestureHolder.setStyleSheet("background: none")

        self.show()

    def initCommunicators(self):
        self.communicator = Communicate()
        my_data_loop = threading.Thread(name='my_data_loop', target=self.data_send_loop, daemon=True,
                                        args=(self.receive_data,))
        my_data_loop.start()

    def paintEvent(self, event):
        angle = 90 - int((self.roll / SENSITIVITY) * 360)
        angle = angle % 360
        if angle - PICKER_THICKNESS < MIN_ANGLE: angle = MIN_ANGLE + PICKER_THICKNESS
        if angle + PICKER_THICKNESS > MAX_ANGLE: angle = MAX_ANGLE - PICKER_THICKNESS

        self.rPickerPixmap.fill(Qt.transparent)

        painter = QPainter(self.rPickerPixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # gesture image
        if self.gesture is not None:
            path = os.path.dirname(__file__) + "/img/" + self.gesture + ".png"
            self.gestureHolder.setStyleSheet("background: url(" + path + ") no-repeat center center fixed; "
                                                                         "background-color: white;")

        # picker full arc
        painter.setPen(QPen(QColor.fromRgb(_BLUE_COLOR), 10, Qt.SolidLine))
        painter.drawArc(50, ARC_START_Y, ARC_DIAMETER, ARC_DIAMETER, MIN_ANGLE * 16, (MAX_ANGLE - MIN_ANGLE) * 16)

        # picker itself
        painter.setPen(QPen(QColor.fromRgb(0x000000), 15, Qt.SolidLine))
        painter.drawArc(50, ARC_START_Y, ARC_DIAMETER, ARC_DIAMETER, (angle - PICKER_THICKNESS) * 16,
                        PICKER_THICKNESS * 2 * 16)

        self.rPickerHolder.setPixmap(self.rPickerPixmap)

        # chart area
        painter = QPainter(self.barPixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        self.barPixmap.fill(Qt.transparent)
        votes = self.vkeyboard.votes
        bws = self.bar_width_step
        bhs = self.bar_height_step
        bm = 10
        path_painter = QPainterPath()
        # bars
        for i in range(self.vkeyboard.block_size):
            path_painter.addRoundedRect(bws * i + bm * i, BAR_H - votes[i] * bhs, bws - bm, votes[i] * bhs + 50, 2, 2)
            painter.fillPath(path_painter, QColor.fromRgb(_BLUE_COLOR))

        # bar outlines
        painter.setPen(QPen(QColor.fromRgb(0xDDDDDD), 2, Qt.SolidLine))
        for i in range(self.vkeyboard.block_size):
            path_painter.addRoundedRect(bws * i + bm * i, 0, bws - bm, BAR_H, 2, 2)
            painter.drawPath(path_painter)

        # bar letters
        block = self.vkeyboard.getBlockByAngle(angle, MIN_ANGLE, MAX_ANGLE)
        painter.setPen(QPen(QColor.fromRgb(0x000000), 4, Qt.SolidLine))
        font = painter.font()
        font.setBold(True)
        font.setPointSize(BAR_FONT_SIZE)
        painter.setFont(font)
        index = 0
        for letter in block:
            painter.drawText(index * (bws + bm) + bws / 2 - BAR_FONT_SIZE / 2 - 5, BAR_H - BAR_FONT_SIZE, letter)
            index += 1
        self.barHolder.setPixmap(self.barPixmap)

    def data_send_loop(self, add_data_callback_func):
        self.communicator.data_signal.connect(add_data_callback_func)
        EMGConnector(self.communicator)

    def handleIMU(self, imu_data):
        yaw, pitch, roll = IMUUtils.handleIMUArray(imu_data)
        self.roll = roll
        # self.roll = - imu_data[1] * 2

    def receive_data(self, data):

        self.handleIMU(data[8:-1])
        # TODO move prediction into separate thread
        gesture = self.predictor.handleEMG(data[:8])
        if gesture is not None:
            self.gesture = gesture

            # handle backspace command
            if self.gesture == "fist":
                self.delete_votes += 1
                if self.delete_votes > KeyboardControl.DELETE_VOTES_LIMIT:
                    if len(self.inputDisplay.text()) > 0:
                        self.inputDisplay.setText(self.inputDisplay.text()[:-1])
                        self.delete_votes = 0
                    return

            # handle other commands
            input_letter = self.vkeyboard.recordVote(self.gesture)
            if input_letter is not None:
                self.delete_votes = 0
                self.inputDisplay.setText(self.inputDisplay.text() + input_letter)

        self.update()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    ex = MyoKeyWidget()
    sys.exit(app.exec_())
