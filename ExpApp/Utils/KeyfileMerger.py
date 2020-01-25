import glob
import os

import numpy as np

from ExpApp.Utils.constants import KEYS_SUFFIX
from ExpApp.Utils.datacore_constants import KeyConstants


class KeyfileMerger:

    def __init__(self, dir_="") -> None:
        super().__init__()
        self.dir_ = dir_
        self.full_dir = os.path.dirname(os.path.abspath(__file__)) + '/../../data/app/Device.EMG/KeyLogger/s0/' + self.dir_
        self.emg_data = []
        self.keyboard_data = []
        self.x = []
        self.y = []

    def load_files(self):
        files_read = 0
        files = list(filter(os.path.isfile, glob.glob(self.full_dir + "*")))
        files.sort(key=lambda x: os.path.getmtime(x))
        for file in files:
            full_name = os.path.join(self.full_dir, file)
            if os.path.isfile(full_name):
                if not file.endswith(KEYS_SUFFIX) and os.path.exists(full_name + KEYS_SUFFIX):
                    self.emg_data.extend(np.loadtxt(full_name))
                    self.keyboard_data.extend(np.loadtxt(full_name + KEYS_SUFFIX))
                    files_read += 1

        self.emg_data = np.asarray(self.emg_data)
        self.keyboard_data = np.asarray(self.keyboard_data)
        print("Files read: {0}".format(files_read))

    def merge(self):
        # emg_data = 8 x EMG | 10 x IMU | Timestamp
        x = self.emg_data[:, KeyConstants.CHANNELS_CONFIG]
        y = np.zeros(len(x))

        emg_timesteps = self.emg_data[:, -1]

        # TODO creating labels from keycodes
        # A proper way would be to create a map from plain [0, 1, ...] labels to key codes
        self.keyboard_data[:, 1] -= min(self.keyboard_data[:, 1]) - 1

        key_index = 0
        key_data = self.keyboard_data
        key_timesteps = self.keyboard_data[:, 0]

        # TODO remove -- debug purposes only
        # start_time = min(emg_timesteps)  # emg is earlier
        # emg_timesteps -= start_time
        # emg_timesteps *= 10000
        # key_timesteps -= start_time
        # key_timesteps *= 10000

        emg_index = 0
        while True:
            if emg_timesteps[emg_index] < key_timesteps[key_index]:
                y[emg_index] = 0  # no activity

            elif np.isclose(emg_timesteps[emg_index], key_timesteps[key_index]) or \
                    emg_timesteps[emg_index] > key_timesteps[key_index]:
                pressed_key = key_data[key_index][1]
                y[emg_index] = pressed_key
                key_index += 1
                # TODO check that key was RELEASED (might be another key pressed)
                if key_index >= len(key_timesteps):
                    break

                # label emg samples between key press and key release
                while emg_index < len(emg_timesteps) and emg_timesteps[emg_index] < key_timesteps[key_index]:
                    y[emg_index] = pressed_key
                    emg_index += 1

                key_index += 1
                if key_index >= len(key_timesteps):
                    break
            emg_index += 1
            if emg_index >= len(emg_timesteps):
                break

        self.x = x
        self.y = y
        return x, y

    def analyse(self, verbose=False):
        y = self.y.astype(int)
        no_activity = 0
        keys_pressed = np.zeros(max(y))
        last_pressed = None
        distance = 0
        counter = 0

        min_distance = len(y)
        max_distance = 0

        min_press = len(y)
        max_press = 0

        min_dst_press = len(y)

        for i in range(len(y)):
            label = y[i]
            if label == 0:
                distance += 1
                no_activity += 1
                if counter != 0:
                    keys_pressed[last_pressed - 1] += 1
                    if verbose:
                        print("Key {0} was hold down for {1} timesteps in a row after {2} timesteps"
                              .format(last_pressed, counter, distance))

                    min_press = min(counter, min_press)
                    max_press = max(counter, max_press)

                    min_distance = min(distance, min_distance)
                    max_distance = max(distance, max_distance)

                    min_dst_press = min(distance + counter, min_dst_press)

                    counter = 0
                    distance = 0
            else:
                counter += 1
                last_pressed = label

        print("-------------------------------------------------")
        print("No activity was detected for {0} timesteps total".format(no_activity))
        print("Min distance {0}; Max distance {1}; Min press {2}; Max press {3}; Min combined {4}"
              .format(min_distance, max_distance, min_press, max_press, min_dst_press))
        for i in range(len(keys_pressed)):
            print("Key {0} was pressed {1} times in total".format(i + 1, int(keys_pressed[i])))
        print("-------------------------------------------------")

    def cut_trials(self):
        y = self.y
        x = self.x
        before = KeyConstants.BEFORE
        after = KeyConstants.AFTER
        trials = []
        labels = []
        press = False
        last_press = 0
        i = 0
        while True:
            if y[i] == 0:
                if press:
                    trial = x[i - before: i + after]
                    if len(trial) != before + after:
                        continue
                    trials.append(trial)
                    labels.append(last_press)
                    press = False
            else:
                press = True
                last_press = y[i]
            i += 1
            if i >= len(y):
                break

        # # TODO add zero trials
        # trials_per_label = int(len(trials) / max(labels))
        # print(trials_per_label)
        # added = 0
        # i = 0
        # while True:
        #     zero_trial = []
        #     collected = 0
        #     while y[i] == 0:
        #         zero_trial.append(x[i])
        #         i += 1
        #         if i >= len(y):
        #             break
        #         collected += 1
        #         if collected == trial_len:
        #             trials.append(np.asarray(zero_trial))
        #             labels.append(0.)
        #             added += 1
        #
        #     if added >= trials_per_label:
        #         break
        #     i += 1
        #     if i >= len(y):
        #         break
        labels -= np.ones(np.asarray(labels).shape)
        return np.asarray(trials), np.asarray(labels).astype(int)


if __name__ == '__main__':
    merger = KeyfileMerger()
    merger.load_files()
    merger.merge()
    merger.analyse(verbose=True)
    trials, labels = merger.cut_trials()
    pass
