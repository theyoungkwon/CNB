import datetime
import random
from time import time

SUB_DIR = "myokey_logs/"


class MyoKeyLogger:
    def __init__(self, file_name='') -> None:
        super().__init__()
        self.date = datetime.datetime.now().strftime("%Y%m%d:%H%M%S")
        self.id = self.exp_id = int(random.random() * 1000)
        self.file_name = file_name
        if len(file_name) == 0:
            self.file_name = str(self.date + "_" + str(id))
        self.log = []
        self.times = []

    # gesture | letter | time
    def record_gesture(self, gesture):
        timestamp = time()
        self.log.append(gesture + ", N/A, " + str(timestamp))

    def record_letter(self, letter):
        timestamp = time()
        self.times.append(timestamp)
        self.log.append("N/A, " + letter + "," + str(timestamp))

    def stop(self):
        total_time = (self.times[-1] - self.times[0])
        print("Flushing " + str(
            len(self.log)) + " log records  to the file: " + self.file_name + " Total time of input: " + str(
            total_time))
        with open(SUB_DIR + self.file_name, 'w') as f:
            for record in self.log:
                f.write(record + "\n")
