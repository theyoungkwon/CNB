import os

import gumpy
import numpy as np
import sklearn
from sklearn.metrics import accuracy_score
from sklearn.svm import SVC

from ExpApp.Utils.datacore_constants import TC_B, TC_E, IMG_X, SET1

data_directory = "5labels/"
data_directory_main = "trist/"
trials_in_file = 28
FPL_train = 2  # FILES PER LABEL


class EMGDataLoader:

    def __init__(self, num_labels) -> None:
        super().__init__()
        self.num_labels = num_labels
        self.is_removed = False

    def load(self):
        self.train_data = []
        for label in range(self.num_labels):
            for file_index in range(FPL_train):
                filename = data_directory + "l" + str(label + 1) + "_" + str(file_index + 1)
                record = np.loadtxt(filename)
                raw_data = record[:, 0:IMG_X]
                self.train_data.append(raw_data)
        self.test_data = []
        for label in range(self.num_labels):
            filename = data_directory + "l" + str(label + 1) + "_test"
            record = np.loadtxt(filename)
            raw_data = record[:, 0:IMG_X]
            self.test_data.append(raw_data)

    def load_extended(self, _dir, _set):
        dir_prefix = os.path.dirname(os.path.abspath(__file__)) + '/../../../data/app/Device.EMG/'
        self.train_data = []
        self.test_data = []
        self.labels = _set
        self.label_files = list(range(len(self.labels)))
        files_for_label = {}
        test_labels = []
        train_labels = []
        _dir = _dir + "/"

        for i in range(len(_set)):
            label = _set.__getitem__(i)
            for file in os.listdir(dir_prefix + _dir):
                if file.startswith(label):
                    record = np.loadtxt(dir_prefix + _dir + file)
                    raw_data = record[:, 0:IMG_X]

                    if label in files_for_label:
                        files_for_label[label] = files_for_label[label] + 1
                    else:
                        files_for_label[label] = 1

                    if files_for_label[label] <= FPL_train:
                        # TRAIN
                        self.train_data.append(raw_data)
                        train_labels = np.append(train_labels, np.repeat(i, trials_in_file))
                    else:
                        # TEST
                        self.test_data.append(raw_data)
                        test_labels = np.append(test_labels, np.repeat(i, trials_in_file))

        return train_labels, test_labels

    def load_main(self):
        dir_prefix = os.path.dirname(os.path.abspath(__file__)) + '/../../../data/app/Device.EMG/'
        self.train_data = []
        self.test_data = []
        self.labels = []
        self.label_files = list(range(len(self.labels)))
        i = 0
        for label in self.labels:

            for file_index in range(FPL_train):
                filename = dir_prefix + data_directory_main + label + "_" + str(file_index + 1)
                # try:
                record = np.loadtxt(filename)
                raw_data = record[:, 0:IMG_X]
                self.train_data.append(raw_data)
                # except:
                #     print(str(file_index) + " files loaded for " + label)
                # finally:
            self.label_files[i] = FPL_train

            i += 1

            filename = dir_prefix + data_directory_main + label + "_test"
            record = np.loadtxt(filename)
            raw_data = record[:, 0:IMG_X]
            self.test_data.append(raw_data)

    def get_train_labels(self):
        labels = []
        for i in range(self.num_labels):
            labels = np.append(labels, np.repeat(i, trials_in_file * self.label_files[i]))
        return labels

    def get_test_labels(self):
        labels = []
        for i in range(self.num_labels):
            labels = np.append(labels, np.repeat(i, trials_in_file))
        return labels

    def split_into_trials(self):
        self.train_trials = []
        for file in self.train_data:
            file_trials = np.array_split(file, trials_in_file)
            self.train_trials.extend(file_trials)
        self.test_trials = []
        for file in self.test_data:
            file_trials = np.array_split(file, trials_in_file)
            self.test_trials.extend(file_trials)

    def trim_trials(self, x, y):
        for i in range(len(self.test_trials)):
            self.test_trials[i] = self.test_trials[i][x:y, :]

        for i in range(len(self.train_trials)):
            self.train_trials[i] = self.train_trials[i][x:y, :]

    def scale(self):
        for i in range(len(self.test_trials)):
            self.test_trials[i] = sklearn.preprocessing.scale(self.test_trials[i])

        for i in range(len(self.train_trials)):
            self.train_trials[i] = sklearn.preprocessing.scale(self.train_trials[i])

    def norm_sk(self):
        for i in range(len(self.test_trials)):
            self.test_trials[i] = sklearn.preprocessing.normalize(self.test_trials[i])

        for i in range(len(self.train_trials)):
            self.train_trials[i] = sklearn.preprocessing.normalize(self.train_trials[i])

    def pca(self, n_components=IMG_X):
        pca1 = sklearn.decomposition.PCA(n_components)
        pca2 = sklearn.decomposition.PCA(n_components)
        for i in range(len(self.test_trials)):
            pca1.fit_transform(self.test_trials[i])

        for i in range(len(self.train_trials)):
            pca2.fit_transform(self.train_trials[i])

    def bandpass(self, bp):
        lowcut = 5
        highcut = 200
        f0 = 50
        Q = 50

        for i in range(len(self.test_trials)):
            trial = self.test_trials[i]
            if bp: trial = gumpy.signal.butter_bandpass(trial, lowcut, highcut)
            trial = gumpy.signal.notch(trial, cutoff=f0, Q=Q)
            self.test_trials[i] = trial

        for i in range(len(self.train_trials)):
            trial = self.train_trials[i]
            if bp: trial = gumpy.signal.butter_bandpass(trial, lowcut, highcut)
            trial = gumpy.signal.notch(trial, cutoff=f0, Q=Q)
            self.train_trials[i] = trial

    @staticmethod
    def load_data_for_cnn(test=False, params=None):
        start = TC_B
        if "start" in params:
            start = params["start"]
        end = TC_E
        if "end" in params:
            end = params["end"]
        bandpass = False
        if "bandpass" in params:
            bandpass = params["bandpass"]
        _dir = data_directory_main
        if "dir" in params:
            _dir = params["dir"]
        _set = SET1
        if "set" in params:
            _set = params["set"]

        t = EMGDataLoader(num_labels=len(_set))

        # t.load_main()
        # y_train = t.get_train_labels()
        # y_test = t.get_test_labels()

        y_train, y_test = t.load_extended(_dir, _set)

        t.split_into_trials()
        # t.bandpass(bandpass)
        t.trim_trials(x=start, y=end)

        if not test:  # TRAIN
            return np.asarray(t.train_trials).astype(np.float32), np.asarray(y_train).astype(np.int32)
        else:  # TEST
            return np.asarray(t.test_trials).astype(np.float32), np.asarray(y_test).astype(np.int32)

    def flatten(self):
        for i in range(len(self.train_trials)):
            self.train_trials[i] = self.train_trials[i].flatten()
        for i in range(len(self.test_trials)):
            self.test_trials[i] = self.test_trials[i].flatten()

    @staticmethod
    def test_classifier(clf):
        t = EMGDataLoader()
        t.load_main()
        t.split_into_trials()
        t.substract_mean()
        t.normalize()
        t.pca()
        t.trim_trials(x=150, y=350)
        t.flatten()
        y_train = t.get_train_labels()
        y_test = t.get_test_labels()

        clf.fit(t.train_trials, y_train)
        y_pred = clf.predict(t.test_trials)

        print(y_pred)

        print(accuracy_score(y_test, y_pred))

    def substract_mean(self):
        for i in range(len(self.train_trials)):
            mean = np.mean(self.train_trials[i])
            self.train_trials[i] -= mean

        for i in range(len(self.test_trials)):
            mean = np.mean(self.test_trials[i])
            self.test_trials[i] -= mean

    def normalize(self):
        for i in range(len(self.test_trials)):
            self.test_trials[i] = self.test_trials[i] / np.sqrt((np.sum(self.test_trials[i] ** 2)))
        for i in range(len(self.train_trials)):
            self.train_trials[i] = self.train_trials[i] / np.sqrt((np.sum(self.train_trials[i] ** 2)))


def test():
    EMGDataLoader.test_classifier(clf=SVC())


if __name__ == '__main__':
    test()
