import time

import numpy
import pkg_resources

from ExpApp.API.openbci import OpenBCISample


class ReadSample:

    def __init__(self,
                 filename="EEGMOCK") -> None:
        super().__init__()
        self.array = numpy.loadtxt(filename)
        self.index = 0

    def read_sample(self):
        if self.index >= len(self.array):
            return None
        raw = self.array[self.index]
        self.index += 1
        _sample = OpenBCISample()
        _sample.timestamp = raw[len(raw) - 1].tolist()
        _sample.channel_data = raw[:len(raw) - 1].tolist()
        return _sample


if __name__ == '__main__':
    reader = ReadSample()
    sample = reader.read_sample()
    while sample is not None:
        print(sample.timestamp)
        time.sleep(1. / 255.)
        sample = reader.read_sample()
