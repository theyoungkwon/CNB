import datetime
import os

import numpy

from ExpApp.Utils.constants import FILE_LOCATION


class Recorder:

    def __init__(self, file_name='', subdir='', _dir='') -> None:
        super().__init__()
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        if len(file_name) == 0:
            file_name = self.timestamp
        self.file_name = file_name
        self.subdir = subdir
        print("Recording samples to file: " + file_name)
        self.samples = []
        self._dir = _dir
        full_dir = self._dir + "/" + FILE_LOCATION + self.subdir
        self.full_name = full_dir + self.file_name
        if not os.path.exists(full_dir):
            os.makedirs(full_dir)

    def start(self):
        pass

    def record_sample(self, sample):
        self.samples.append(sample)

    def stop(self):
        print("Flushing " + str(len(self.samples)) + " records  to the file: " + self.file_name)
        numpy.savetxt(self.full_name, self.samples)
