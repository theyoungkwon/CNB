import time

import pkg_resources

from ExpApp.API.openbci import OpenBCISample


class ReadSample:

    def __init__(self) -> None:
        super().__init__()
        self.file = pkg_resources.resource_stream(__name__, "sample_data.csv")

    def read_sample(self):
        line = self.file.readline()
        if len(line) <= 0:
            return None
        sample_ = OpenBCISample()
        raw_sample = str(line).split(',')
        sample_.timestamp = raw_sample[0]
        sample_.id = raw_sample[1]
        sample_.channel_data = raw_sample[2:10]

        return sample_


if __name__ == '__main__':
    reader = ReadSample()
    sample = reader.read_sample()
    while sample is not None:
        print(sample.timestamp)
        time.sleep(1. / 255.)
        sample = reader.read_sample()
