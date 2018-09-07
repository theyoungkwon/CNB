import datetime

from ExpApp.Utils.constants import FILE_LOCATION


class Recorder:

    def __init__(self, file_name='') -> None:
        super().__init__()
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        if len(file_name) == 0:
            file_name = self.timestamp
        self.file_name = file_name
        print("Recording samples to file: " + file_name)
        self.samples = []
        self.file = open(FILE_LOCATION + self.file_name, 'w')

    def start(self):
        pass

    def record_sample(self, sample):
        self.samples.append(sample)

    def stop(self):
        print("Flushing " + str(len(self.samples)) + " records  to the file: " + self.file_name)
        for sample in self.samples:
            self.file.write(str(sample))
            self.file.write('\n')
        self.file.close()
