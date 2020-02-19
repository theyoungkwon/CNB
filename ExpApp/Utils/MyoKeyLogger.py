import datetime
import random
from time import time

from ExpApp.Utils.MyInputBox import MyInputBox

SUB_DIR = "myokey_logs/"


class MyoKeyLogger:
    def __init__(self, file_name='') -> None:
        super().__init__()
        self.date = datetime.datetime.now().strftime("%Y%m%d:%H%M%S")
        self.id = self.exp_id = int(random.random() * 1000)
        self.file_name = file_name
        if len(file_name) == 0:
            self.file_name = str(self.date + "_" + str(id))
        self.log_gestures = []
        self.log_inputs = []
        self.times = []

    # gesture | letter | time
    def record_gesture(self, gesture):
        timestamp = time()
        self.log_gestures.append(f"{gesture}; {timestamp}")

    def record_letter(self, letter):
        timestamp = time()
        self.times.append(timestamp)
        self.log_inputs.append(f"{letter}; {timestamp}")

    def stop(self):
        total_time = (self.times[-1] - self.times[0])
        print(f"Flushing log records  to the file: {self.file_name}; Total time of input: {total_time}")
        with open(SUB_DIR + self.file_name + '_gestures.csv', 'w') as f:
            for record in self.log_gestures:
                f.write(record + "\n")

        with open(SUB_DIR + self.file_name + '_inputs.csv', 'w') as f:
            for record in self.log_inputs:
                f.write(record + "\n")

    def record_log(self, log):
        with open(SUB_DIR + self.file_name + "_words.csv", 'w') as f:
            f.write(MyInputBox.get_log_header())
            for record in log:
                f.write(record + "\n")