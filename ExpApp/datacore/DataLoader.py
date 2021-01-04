import os
import numpy as np
from sklearn.preprocessing import normalize

from ExpApp.Utils.datacore_constants import *


class DataLoader:
    class Params:

        @staticmethod
        def init():
            return {
                "prefix": 100,
                "end": TC_E,
                "dir": "s0",
                "all": False,
                "set": SET1,
                "bandpass": False,
                "normalize": False,
                "interval": C_INTERVAL
            }

    def __init__(self):
        self.y = []
        self.x = []
        self.params = self.Params().init()
        self.data = {}

    def handle_params(self, params=None):
        try:
            iter(params)
        except TypeError:
            pass  # using default
        else:
            self.params.update(params)

    def read_files(self):
        dir_prefix = os.path.dirname(os.path.abspath(__file__)) + '/../../data/app/Device.EMG/'
        dir_ = self.params["dir"] + "/"
        set_ = self.params["set"]
        files_for_label = {}

        for label in set_:
            raw_data = []
            for file in os.listdir(dir_prefix + dir_):
                if file.startswith(label):
                    record = np.loadtxt(dir_prefix + dir_ + file)
                    raw_data.extend(record[:, 0:IMG_X])

                    if label in files_for_label:
                        files_for_label[label] = files_for_label[label] + 1
                    else:
                        files_for_label[label] = 1

            if self.verbose and label in files_for_label:
                print("{0} file(s) read for label: {1}".format(files_for_label[label], label))

            self.data[label] = np.array(raw_data)

    def preprocess(self):
        to_normalize = self.params["normalize"]
        if to_normalize:
            for l in self.data:
                self.data[l] = normalize(self.data[l], axis=0)
        to_bandpass = self.params["bandpass"]

    def split_trials(self):
        trial_size = self.params["end"]
        interval = self.params["interval"]
        y = 0
        for l in self.data:
            data = self.data[l]
            start = 0

            while start + trial_size <= len(data):
                t = data[start:start + trial_size]
                self.x.append(t)
                self.y.append(y)
                start += interval

            y += 1

    def load(self, params=None, verbose=False):
        self.verbose = verbose
        self.handle_params(params)
        self.read_files()
        self.preprocess()
        self.split_trials()
        return np.array(self.x), np.array(self.y)


if __name__ == '__main__':
    # tests
    loader = DataLoader()
    interval_ = 10
    loader.load({"interval": interval_, "end": 50})
    assert (loader.params["interval"] == interval_)
