import getopt
import os
import subprocess
import sys
import threading
from time import time

import os

from ExpApp.Utils.KeyboardLogger import KeyboardLogger

path_fix = os.path.dirname(os.path.abspath(__file__)) + "/"

import matplotlib
from ExpApp.API.OBCIConnector import OBCIConnector
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QPushButton, QDoubleSpinBox, QLineEdit, QLabel, QRadioButton, QSpinBox, QComboBox

from EMG.EMGConnector import EMGConnector
from ExpApp.GUI.PyQt.Widgets.flash_window import FlashWindow
from ExpApp.GUI.PyQt.Widgets.graphs import GraphWidget
from ExpApp.GUI.PyQt.Widgets.motor_img_window import MotorImgWindow, SEQUENCE
from ExpApp.GUI.PyQt.Widgets.p300_secret_speller import P300SecretSpeller
from ExpApp.GUI.PyQt.Widgets.pincode_window import PinCodeWindow
from ExpApp.Utils.ExperimentParams import ExperimentParams
from ExpApp.Utils.Recorder import Recorder
from ExpApp.Utils.constants import WINDOW_X, WINDOW_Y, _FLASH, MAX_RECORD_DURATION, _EC, _EO, EP_EO_DURATION, \
    EP_FLASH_RECORD_DURATION, _SSVEP1, _SSVEP2, _SSVEP3, \
    _PINCODE_4_TRUE_SEQ_REP_3, PINCODE_FLASH_INTERVAL, _P300_SECRET_9, PINCODE_TRUE_SEQ, PINCODE_REPETITIONS, \
    PINCODE_LENGTH, _MI_CALIBRATION, SSVEP_TIME_WINDOW, \
    _MI_INPUT, TRIAL_STEPS, MI_CALIBRATION_TRIALS, MI_LABELS, MI_INPUT_LENGTH, FREQ, DEBUG_SUBDIR, \
    Device, EMG_TRIAL_STEPS, BACKGROUND_COLOR
from ExpApp.tests.read_sample import ReadSample

RESUME_GRAPH = 'Resume graph'
PAUSE_GRAPH = "Pause graph"

matplotlib.use("Qt4Agg")


class CustomMainWindow(QtWidgets.QMainWindow):

    def __init__(self, device=Device.EEG, mock=False, log_keyboard=False):
        super(CustomMainWindow, self).__init__()
        self.communicator = Communicate()
        self.is_recording = False
        self.recorder = None
        self.device = device
        self.mock = mock
        self.log_keyboard = log_keyboard

        self.keyboard_logger = None
        self.threadpool = QThreadPool()

        self.setWindowTitle("ExpApp")
        self.setGeometry(100, 100, WINDOW_X, WINDOW_Y)
        self.options = [
            _EO,
            _EC,
            _PINCODE_4_TRUE_SEQ_REP_3,
            _P300_SECRET_9,
            _MI_CALIBRATION,
            _MI_INPUT,
            _SSVEP1,
            _SSVEP2,
            _SSVEP3,
        ]

        # Default parameters
        self.exp_params = ExperimentParams()
        self.exp_params.experiment = self.options[0]

        self.main_widget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QGridLayout()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        # Experiment window
        self.exp_window = None

        # Create graph frame
        graph_col_span = 8
        self.graph_layout = QtWidgets.QGridLayout()
        self.graph_frame = QtWidgets.QFrame(self)
        self.graph_frame.setLayout(self.graph_layout)
        self.main_layout.addWidget(self.graph_frame, 0, 0, 3, graph_col_span)
        self.myFig = GraphWidget(True if self.device == Device.EMG else False)
        self.graph_layout.addWidget(self.myFig)
        my_data_loop = threading.Thread(name='my_data_loop', target=self.data_send_loop, daemon=True,
                                        args=(self.add_data_callback_func,))
        my_data_loop.start()

        # Create control panel frame
        cpr = 0
        self.control_panel_layout = QtWidgets.QGridLayout()
        self.control_panel_frame = QtWidgets.QFrame(self)
        self.control_panel_frame.setLayout(self.control_panel_layout)
        self.main_layout.addWidget(self.control_panel_frame, cpr, graph_col_span, 1, 3)
        self.is_paused = False
        if True:
            # Pause button
            self.pause_button = QPushButton(PAUSE_GRAPH)
            self.pause_button.clicked.connect(lambda: self.pause_graphs())
            self.control_panel_layout.addWidget(self.pause_button, cpr, 0, 1, 3)
            cpr += 1

            # Record panel
            self.record_button = QPushButton('Record')
            self.record_button.clicked.connect(lambda: self.start_record_())
            self.record_time_input = QDoubleSpinBox()
            self.record_count = 1
            self.record_time_input.setValue(self.exp_params.record_duration)
            self.record_time_input.setSingleStep(0.1)
            self.record_time_input.setMaximum(MAX_RECORD_DURATION)
            self.record_time_input.valueChanged.connect(self.set_record_time)
            self.record_countdown = QLabel("")
            self.control_panel_layout.addWidget(self.record_time_input, cpr, 0)
            self.control_panel_layout.addWidget(self.record_countdown, cpr, 1, 1, 1)
            self.control_panel_layout.addWidget(self.record_button, cpr, 2, 1, 1)
            cpr += 1

            # Experiment setup panel
            # File name
            self.exp_name_prefix_input = QLineEdit()
            self.exp_name_prefix_input.setText(self.exp_params.name_prefix)
            self.exp_name_prefix_input.editingFinished.connect(self.set_exp_name)
            self.control_panel_layout.addWidget(QLabel("File Name Prefix: "), cpr, 0, 1, 1)
            self.control_panel_layout.addWidget(self.exp_name_prefix_input, cpr, 1, 1, 2)
            cpr += 1
            # Subject id
            self.exp_subject_id_prefix_input = QLineEdit()
            self.exp_subject_id_prefix_input.setText(self.exp_params.subject_id)
            self.exp_subject_id_prefix_input.editingFinished.connect(self.set_exp_subject)
            self.control_panel_layout.addWidget(QLabel("User: "), cpr, 0, 1, 1)
            self.control_panel_layout.addWidget(self.exp_subject_id_prefix_input, cpr, 1, 1, 2)
            cpr += 1
            # Gender
            self.control_panel_layout.addWidget(QLabel("Gender:"), cpr, 0, 1, 1)
            self.exp_m_input = QRadioButton("male")
            self.exp_m_input.setChecked(self.exp_params.gender == self.exp_m_input.text())
            self.exp_m_input.toggled.connect(lambda checked: self.set_exp_gender(self.exp_m_input.text(), checked))
            self.exp_f_input = QRadioButton("female")
            self.exp_f_input.setChecked(self.exp_params.gender == self.exp_f_input.text())
            self.exp_f_input.toggled.connect(lambda checked: self.set_exp_gender(self.exp_f_input.text(), checked))
            self.control_panel_layout.addWidget(self.exp_m_input, cpr, 1, 1, 1)
            self.control_panel_layout.addWidget(self.exp_f_input, cpr, 2, 1, 1)
            cpr += 1
            # Age
            self.control_panel_layout.addWidget(QLabel("Age:"), cpr, 0, 1, 1)
            self.exp_age_input = QSpinBox()
            self.exp_age_input.setValue(self.exp_params.age)
            self.exp_age_input.editingFinished.connect(self.set_exp_age)
            self.control_panel_layout.addWidget(self.exp_age_input, cpr, 1, 1, 2)
            cpr += 1
            # Electrodes
            self.exp_electrodes_input = QLineEdit()
            self.exp_electrodes_input.setText(self.exp_params.electrodes)
            self.exp_electrodes_input.editingFinished.connect(self.set_electrodes)
            self.control_panel_layout.addWidget(QLabel("Electrodes:"), cpr, 0, 1, 1)
            self.control_panel_layout.addWidget(self.exp_electrodes_input, cpr, 1, 1, 2)
            cpr += 1

            # Experiment selection
            self.exp_selection_box = QComboBox()
            self.exp_selection_box.addItems(self.options)
            self.exp_selection_box.currentIndexChanged.connect(self.set_exp)
            self.exp_run_button = QPushButton("Run")
            self.exp_run_button.clicked.connect(self.exp_run)
            self.control_panel_layout.addWidget(self.exp_run_button, cpr, 0, 1, 1)
            self.control_panel_layout.addWidget(self.exp_selection_box, cpr, 1, 1, 2)

        if self.device == Device.EMG:
            self.setStyleSheet("background-color: " + BACKGROUND_COLOR + ";")

        self.show()

    def set_exp(self):
        self.exp_params.experiment = self.exp_selection_box.currentText()

    def exp_run(self):
        # Flash
        if self.exp_params.experiment == _FLASH:
            self.exp_params.record_duration = EP_FLASH_RECORD_DURATION
            self.start_record()
            self.exp_window = FlashWindow()
            self.exp_window.showFullScreen()
        # EO / EC
        elif self.exp_params.experiment == _EC or self.exp_params.experiment == _EO:
            self.exp_params.record_duration = EP_EO_DURATION
            self.start_record()
        # SSVEP
        elif self.exp_params.experiment[:5] == "SSVEP":
            id = int(self.exp_params.experiment[5:6]) - 1
            self.exp_params.record_duration = SSVEP_TIME_WINDOW * len(FREQ[id]) / 1000
            self.exp_window = None
            self.start_record()
            path = path_fix + "./Widgets/ssvep_exp.py"
            subprocess.Popen(["python", path, str(id)])
        # PINCODE TRUE SEQ
        elif self.exp_params.experiment == _PINCODE_4_TRUE_SEQ_REP_3:
            true_seq = PINCODE_TRUE_SEQ
            repetitions = PINCODE_REPETITIONS
            self.exp_window = PinCodeWindow(sequence=true_seq, repetitions=repetitions)
            self.exp_params.record_duration = ((len(true_seq) + 1) * PINCODE_FLASH_INTERVAL / 1000) * repetitions
            self.start_record()
            self.exp_window.showFullScreen()
        # P300 Secret
        elif self.exp_params.experiment == _P300_SECRET_9:
            length = PINCODE_LENGTH
            self.exp_window = P300SecretSpeller(length=length)
            self.exp_params.record_duration = (9 * PINCODE_FLASH_INTERVAL / 1000) * length
            self.start_record()
            self.exp_window.showFullScreen()
        # MOTOR IMG
        elif self.exp_params.experiment == _MI_CALIBRATION:
            self.exp_window = MotorImgWindow(sequence=SEQUENCE.CALIBRATION, device=self.device)
            tracker = EMG_TRIAL_STEPS() if self.device == Device.EMG else TRIAL_STEPS()
            self.exp_params.record_duration = MI_LABELS * MI_CALIBRATION_TRIALS * tracker.TRIAL_END / 1000
            self.start_record()
            self.exp_window.showFullScreen()
        elif self.exp_params.experiment == _MI_INPUT:
            self.exp_window = MotorImgWindow(sequence=SEQUENCE.INPUT, device=self.device)
            tracker = EMG_TRIAL_STEPS() if self.device == Device.EMG else TRIAL_STEPS()
            self.exp_params.record_duration = MI_INPUT_LENGTH * tracker.TRIAL_END / 1000
            self.start_record()
            self.exp_window.showFullScreen()

    def start_record_(self):
        self.exp_params.experiment = 'Record'
        self.start_record()

    def set_electrodes(self):
        self.exp_params.electrodes = self.exp_electrodes_input.text()

    def set_exp_age(self):
        self.exp_params.age = self.exp_age_input.value()

    def set_exp_gender(self, value, checked):
        if checked:
            self.exp_params.gender = value

    def set_exp_name(self):
        self.exp_params.name_prefix = self.exp_name_prefix_input.text()

    def set_exp_subject(self):
        self.exp_params.subject_id = self.exp_subject_id_prefix_input.text()

    def set_record_time(self):
        self.exp_params.record_duration = self.record_time_input.value()

    def looper(self, time_left):
        if time_left < 0: return
        self.record_countdown.setText('%5.1f' % time_left + " s")
        interval = 0.5
        threading.Timer(interval, lambda: self.looper(time_left - interval)).start()

    def start_record(self):
        t = threading.Timer(int(self.exp_params.record_duration), lambda: self.stop_record())
        self.looper(self.exp_params.record_duration)
        self.is_recording = True
        self.record_button.setDisabled(self.is_recording)
        subdir = ""
        if self.mock:
            subdir = DEBUG_SUBDIR
        if self.device == Device.EMG:
            subdir = str(Device.EMG) + "/"
        subdir += self.exp_params.subject_id + "/"
        self.recorder = Recorder(_dir=path_fix, file_name=self.exp_params.to_file_name(), subdir=subdir)
        if self.log_keyboard:
            self.keyboard_logger = KeyboardLogger(file_name=self.recorder.full_name)
            self.keyboard_logger.start()
        self.exp_params.exp_id += 1
        t.start()

    def stop_record(self):
        self.is_recording = False
        self.record_button.setDisabled(self.is_recording)
        self.exp_params.exp_id += 1
        self.recorder.stop()
        if self.exp_window is not None:
            del self.exp_window
            self.exp_window = None
        if self.log_keyboard and self.keyboard_logger != None:
            self.keyboard_logger.stop()

    def pause_graphs(self):
        self.is_paused = not self.is_paused
        self.pause_button.setText(RESUME_GRAPH if self.is_paused else PAUSE_GRAPH)

    def add_data_callback_func(self, value):
        if not self.is_paused:
            self.myFig.addData(value)
        if self.is_recording:
            self.recorder.record_sample(value)

    def data_handler(self, sample):
        timestamp = time()
        value = sample.channel_data
        value.append(timestamp)
        self.communicator.data_signal.emit(value)

    def data_send_loop(self, add_data_callback_func):
        self.communicator.data_signal.connect(add_data_callback_func)
        if self.mock:
            file_name = "EEGMOCK" if self.device == Device.EEG else "EMGMOCK"
            reader = ReadSample(path_fix + file_name)
            sample = reader.read_sample()

            while sample is not None:
                time.sleep(1. / 50.)
                value = sample.channel_data
                value.append(sample.timestamp)
                self.communicator.data_signal.emit(value)
                sample = reader.read_sample()
        else:
            if self.device == Device.EEG:
                board = OBCIConnector()
                board.attach_handlers(self.data_handler)
            elif self.device == Device.EMG:
                self.exp_params.name_prefix = "EMG"
                EMGConnector(self.communicator)


class Communicate(QtCore.QObject):
    data_signal = QtCore.pyqtSignal(list)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


def main():
    opts, args = getopt.getopt(sys.argv[1:], "kmd:")
    device = Device.EEG
    log_keyboard = False
    mock = False
    for option, value in opts:
        if option == "-d":
            device = Device[value]
        elif option == "-k":
            log_keyboard = True
        elif option == "-m":
            mock = True
    sys.excepthook = except_hook
    app = QtWidgets.QApplication(sys.argv)
    CustomMainWindow(device, mock, log_keyboard)  # TODO refactor to params
    sys.exit(app.exec_())


# command line options
# -k to log keyboard into _KEYS file
# -d EEG/EMG device choice
# -m mock. If present files EMGMOCK and EEGMOCK are going to used
if __name__ == '__main__':
    main()
