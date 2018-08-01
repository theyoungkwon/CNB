import random

from ExpApp.Utils.constants import DEFAULT_AGE, DEFAULT_RECORD_TIME, DEFAULT_GENDER, DEFAULT_NAME_PREFIX, \
    DEFAULT_ELECTRODES, _FLASH, _FACES

DELIM = '_'


class ExperimentParams:

    def __init__(self) -> None:
        super().__init__()
        self.age = DEFAULT_AGE
        self.experiment = _FLASH
        self.gender = DEFAULT_GENDER
        self.options = [_FLASH, _FACES]
        self.electrodes = DEFAULT_ELECTRODES
        self.record_time = DEFAULT_RECORD_TIME
        self.name_prefix = DEFAULT_NAME_PREFIX
        self.exp_id = int(random.random() * 100000)

    def to_file_name(self):
        return self.name_prefix + DELIM \
               + self.experiment + DELIM \
               + str(self.exp_id) + DELIM \
               + str(self.record_time) + DELIM \
               + self.gender + DELIM \
               + str(self.age) + DELIM \
               + self.electrodes

    def from_file_name(self, file_name):
        values = file_name.split(DELIM)
        self.experiment = values[1]
        self.exp_id = values[2]
        self.record_time = values[3]
        self.gender = values[4]
        self.age = values[5]
        self.electrodes = values[6]
