import random
from time import strftime, gmtime

from ExpApp.Utils.constants import DEFAULT_AGE, DEFAULT_RECORD_ATTEMPT, DEFAULT_GENDER, DEFAULT_NAME_PREFIX, \
    DEFAULT_ELECTRODES, _FLASH, _FACES, DEFAULT_SUBJECT

DELIM = '_'


class ExperimentParams:

    def __init__(self) -> None:
        super().__init__()
        self.age = DEFAULT_AGE
        self.experiment = _FLASH
        self.gender = DEFAULT_GENDER
        self.options = [_FLASH, _FACES]
        self.subject_id = DEFAULT_SUBJECT
        self.electrodes = DEFAULT_ELECTRODES
        self.record_attempt = DEFAULT_RECORD_ATTEMPT
        self.name_prefix = DEFAULT_NAME_PREFIX
        self.exp_id = int(random.random() * 100000)
        self.record_time = strftime("%Y.%m.%d %H.%M.%S", gmtime())

    def to_file_name(self):
        return self.name_prefix + DELIM \
               + self.experiment + DELIM \
               + str(self.exp_id) + DELIM \
               + str(self.record_attempt) + DELIM \
               + self.record_time + DELIM \
               + self.gender + DELIM \
               + str(self.age) + DELIM \
               + self.electrodes + DELIM \
               + self.subject_id

    def from_file_name(self, file_name):
        self.name_prefix, \
            self.experiment, \
            self.exp_id, \
            self.record_attempt, \
            self.record_time, \
            self.gender, \
            self.age, \
            self.electrodes, \
            self.subject_id \
            = file_name.split(DELIM)
