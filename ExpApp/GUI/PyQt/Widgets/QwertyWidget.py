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


ANGLE_RANGE = 35  # 20 .. 45
MAX_YAW = 360
PICKER_THICKNESS = 2
ARC_START_Y = 220
MAX_W = 1100
MAX_H = 450
ARC_DIAMETER = 400
BAR_W = 240
BAR_H = 200
BAR_FONT_SIZE = 30
_BLUE_COLOR = 0x3498DB
KEY_W = 80
KEY_H = 80
KEY_M = 10
SLIDEBAR_W = MAX_W - 210
HIGHLIGHT_COLOR = "c9e9ff"

HIGHLIGHT_PALETTE = [
    "cfe1ff",
    "abcaff",
    "7aabff",
]

button_style = "border: 1px outset grey; border-radius: 10px; border-style: outset;"


class QwertyWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.init_communicators()
        self.frame = 1
        self.gesture = None
        self.vkeyboard = VKeyboard(config=KeyboardControl.configQ)
        model_path = os.path.dirname(__file__) + "/../../../datacore/cnn_qwerty_debug"
        self.predictor = EasyPredictor(_set=INPUT_SET, model_path=model_path)
        self.bar_height = self.vkeyboard.max_votes
        self.bar_height_step = BAR_H / self.bar_height
        self.bar_width_step = BAR_W / self.vkeyboard.block_size
        self.delete_votes = 0
        self._rows = len(self.vkeyboard.key_config[0])
        self._columns = len(self.vkeyboard.key_config)
        self.init_ui()
        self.right_yaw = 6
        self.left_yaw = 2
        self.yaw = self.right_yaw
        self.imu_set = False
        self.imu_fix = False
        self.tip_position = self.slidebar.width() - 10

    def init_ui(self):

        self.setStyleSheet("background: white")
        self.setGeometry(200, 200, MAX_W, MAX_H)

        self.KeyboardHolder = QLabel(self)
        self.keys = [QLabel] * (self._columns * self._rows)

        for i in range(self._rows):
            for j in range(self._columns):
                if i >= len(self.vkeyboard.key_config[j]):
                    continue
                key_button = QLabel(self)
                key_button.setAlignment(Qt.AlignCenter)
                key_button.setStyleSheet(button_style + "background: white")
                key_button.setText(self.vkeyboard.key_config[j][i])
                font = key_button.font()
                font.setPointSize(22)
                key_button.setFont(font)
                key_button.setGeometry(50 + KEY_M * j + KEY_W * j + i * 40,
                                       150 + KEY_M * i + KEY_H * i,
                                       KEY_W, KEY_H)
                self.keys[i * self._columns + j] = key_button

        self.input_display = QLineEdit(self)
        self.input_display.setText("")
        self.input_display.setGeometry(50, 50, MAX_W - 100, 50)
        self.input_display.setStyleSheet("background: none")
        fontParam = self.input_display.font()
        fontParam.setPointSize(27)
        self.input_display.setFont(fontParam)

        self.gesture_holder = QLabel(self)
        self.gesture_holder.setGeometry(0 + 965, 200, 80, 80)
        self.gesture_holder.setStyleSheet("background: transparent;")

        self.slidebar = QLabel(self)
        self.slidebar.setGeometry(50, 120, MAX_W - 210, 20)

        # reset imu button
        self.reset_imu_button = QPushButton(self)
        self.reset_imu_button.setText('Reset IMU')
        self.reset_imu_button.setGeometry(0 + 965, 300, 80, 40)
        self.reset_imu_button.setStyleSheet(button_style + "background: white")
        fontParam.setPointSize(10)
        self.reset_imu_button.setFont(fontParam)
        self.reset_imu_button.clicked.connect(lambda: self.reset_imu())

        self.show()

    def reset_imu(self, yaw=None):
        if yaw is None:
            yaw = self.yaw
        print("Resetting RIGHT yaw to: " + str(yaw))
        self.right_yaw = yaw
        self.left_yaw = yaw + ANGLE_RANGE
        self.imu_set = True

    def highlight_column(self, col_index):
        for i in range(self._rows):
            for j in range(self._columns):
                if i >= len(self.vkeyboard.key_config[j]):
                    continue
                key_button = self.keys[i * self._columns + j]
                if j == col_index:
                    votes = self.vkeyboard.votes
                    key_button.setStyleSheet(button_style + "background: #" + HIGHLIGHT_PALETTE[votes[i]])
                else:
                    key_button.setStyleSheet(button_style + "background: white")

    def init_communicators(self):
        self.communicator = Communicate()
        my_data_loop = threading.Thread(daemon=True,
                                        name='my_data_loop',
                                        target=self.data_send_loop,
                                        args=(self.receive_data,))
        my_data_loop.start()

    def paintEvent(self, event):

        # slide bar
        self.slider_pixmap = QPixmap(MAX_W - 210, 20)
        self.slider_pixmap.fill(Qt.transparent)
        painter = QPainter(self.slider_pixmap)
        path = QPainterPath()
        gradient = QLinearGradient(0, 5, MAX_W - 20, 10)
        gradient.setColorAt(0.0, QColor.fromRgb(0x3498DB))
        gradient.setColorAt(1.0, QColor.fromRgb(0x91cbf2))
        path.addRoundedRect(0, 5, MAX_W - 210, 10, 3, 3)
        painter.fillPath(path, gradient)

        # slider tip
        yaw = self.yaw
        max_width = self.slidebar.width()
        degree = IMUUtils.is_angle_between(yaw, self.right_yaw, self.left_yaw)
        if degree is not None:
            self.tip_position = (1 - degree) * max_width
            self.tip_position = min(self.tip_position, max_width - 40)

        path = QPainterPath()
        path.addRoundedRect(self.tip_position, 0, 20, 20, 2, 2)
        painter.fillPath(path, Qt.black)
        self.slidebar.setPixmap(self.slider_pixmap)

        # highlight column
        column_index = int(self._columns * self.tip_position / max_width)
        column_index = max(0, min(column_index, self._columns - 1))
        self.highlight_column(column_index)
        self.vkeyboard.get_block_by_Index(column_index)

        # gesture image
        if self.gesture is not None:
            path = os.path.dirname(__file__) + "/img/" + self.gesture + ".png"
            self.gesture_holder.setStyleSheet("background: url(" + path + ") no-repeat center center fixed; "
                                                                          "background-color: white;")

    def data_send_loop(self, add_data_callback_func):
        self.communicator.data_signal.connect(add_data_callback_func)
        EMGConnector(self.communicator)

    def handle_imu(self, imu_array):
        yaw, pitch, roll = IMUUtils.handleIMUArray(imu_array, 360)
        if not self.imu_set:
            self.reset_imu(yaw)
        self.yaw = yaw

    def receive_data(self, data):

        self.handle_imu(data[8:-1])
        gesture = self.predictor.handleEMG(data[:8])
        if gesture is not None:
            self.gesture = gesture
            input_letter = self.vkeyboard.recordVote(self.gesture)
            if input_letter is not None:
                self.delete_votes = 0
                if input_letter == "<":
                    # delete last character
                    self.input_display.setText(self.input_display.text()[:-1])
                    return
                else:
                    # append input
                    self.input_display.setText(self.input_display.text() + input_letter)

        self.update()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    ex = QwertyWidget()
    sys.exit(app.exec_())
