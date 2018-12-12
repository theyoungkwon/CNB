import os
from collections import deque

import gumpy
import numpy as np
import tensorflow as tf

from EMG.EMGConnector import EMGConnector
from ExpApp.Utils.datacore_constants import TC_E, TC_B, label_to_gesture
from ExpApp.datacore.EMG.EMG_CNN import EMG_CNN


class EMGWindowSlicer:

    def __init__(self, clf, start=TC_B, end=TC_E, shift=300) -> None:
        super().__init__()
        self.wl = end - start  # wl records in the window
        self.shift = shift  # every frequency records start a new window
        self.wn = int(self.wl / self.shift)
        self.index = 0
        self.step = 0
        self.data = deque(maxlen=self.wl)
        self.clf = clf

    def classify(self, trial):
        eval_input_fn = tf.estimator.inputs.numpy_input_fn(
            x={"x": trial},
            num_epochs=1,
            shuffle=False)
        predictions = self.clf.predict(
            input_fn=eval_input_fn)
        for prediction in predictions:
            gesture = label_to_gesture(prediction['classes'])
            # print(gesture)
            return gesture

    def handle_record(self, record):
        self.data.append(record)
        self.index += 1
        if self.index % self.shift == 0 and self.index >= self.shift:
            trial = list(self.data)
            trial = gumpy.signal.notch(trial, cutoff=50, Q=50)
            trial = np.asarray([trial]).astype(np.float32)
            if trial[0].shape[0] == self.wl:
                return self.classify(trial)
        return None


def test():
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    # Transitions
    cfg2 = {
        "start": TC_B,
        "end": TC_E,
        "dir": "CNNF_0_200____",
        "shift": 300
    }
    # Fuck enabled
    cfg3 = {
        "start": 140,
        "end": 300,
        "dir": "CNNF_0_200____",
        "shift": 160
    }
    # 0 - 200
    cfg3 = {
        "start": 0,
        "end": 200,
        "dir": "CNNF_0_200____",
        "shift": 160
    }
    cfg = cfg3
    clf = EMG_CNN.load(cfg["dir"], params=cfg)
    handler = EMGWindowSlicer(clf, start=cfg["start"], end=cfg["end"], shift=cfg["shift"])
    EMGConnector(data_handler=handler.handle_record, communicator=None)


if __name__ == '__main__':
    # os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    test()
