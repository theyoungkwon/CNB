
import os

# import gumpy
import scipy.io
import numpy as np

from ExpApp.Utils.datacore_constants import IMG_X



def nina(test=False, params=None):
    tr_labels = []
    trials = []
    wl = 200
    subject = 1
    for e in [1, 2, 3]:
        mat = scipy.io.loadmat("S3_E1_A1.mat")
        emg = mat["emg"][:, 1:9]
        labels = mat["restimulus"]
        curr_label = labels[0]
        for i in range(len(labels)):
            if labels[i] != curr_label:
                curr_label = labels[i]
                continue
            if i % wl == 0 and i != 0:
                # trials.append(gumpy.signal.notch(emg[i - wl:i], cutoff=50, Q=50))
                # trials.append(emg[i - wl:i])
                tr_labels.append(curr_label[0])

    print(str(len(set(tr_labels))))
    size = int(len(trials) * 0.75 // 200 * 200)
    if not test:  # TRAIN
        return np.asarray(trials[0:size]).astype(np.float32), np.asarray(tr_labels[0:size]).astype(np.int32)
    else:  # TEST
        return np.asarray(trials[size:]).astype(np.float32), np.asarray(tr_labels[size:]).astype(np.int32)


if __name__ == '__main__':
    x, y = nina()
