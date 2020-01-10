import signal
import sys
from collections import deque

from tensorflow_core.python.keras.saving.save import load_model
import numpy as np

from EMG.EMGConnector import EMGConnector
from ExpApp.Utils.KeyboardLogger import KeyboardLogger
from ExpApp.Utils.datacore_constants import KeyConstants


class KeyWidget:
    def __init__(self, path="../datacore/" + KeyConstants.MODEL_PATH + "") -> None:
        super().__init__()
        self.model = load_model(path)
        self.logger = None
        self.emg_buffer = []
        self.before = deque(maxlen=KeyConstants.BEFORE + KeyConstants.RT_LAG)
        self.after = deque(maxlen=KeyConstants.AFTER - KeyConstants.RT_LAG)
        self.key = None
        self.after_count = 0
        self.width = len(range(*KeyConstants.CHANNELS_CONFIG.indices(KeyConstants.TOTAL_CHANNELS)))

    def predict(self):
        combined = np.append(np.asarray(self.before), self.after)
        # np.flip(combined.reshape(KeyConstants.BEFORE + KeyConstants.AFTER, self.width), axis=0)

        emg_data = np.asarray(combined).reshape((1, KeyConstants.BEFORE + KeyConstants.AFTER, self.width, 1))
        y_pred = [np.argmax(y) for y in self.model.predict(emg_data)]
        print("Pressed: {0} Predicted: {1}".format(self.key, y_pred[0] + 1))
        self.key = None
        self.after_count = 0

    def key_handler(self, key):
        self.key = key
        # self.predict()

    def emg_handler(self, emg):
        self.before.appendleft(emg[KeyConstants.CHANNELS_CONFIG])
        if self.key is not None:
            self.after.appendleft(emg[KeyConstants.CHANNELS_CONFIG])
            self.after_count += 1
            if self.after_count == KeyConstants.AFTER - KeyConstants.RT_LAG:
                self.predict()

    def start(self):
        self.logger = KeyboardLogger(handler=self.key_handler)
        self.logger.start()
        EMGConnector(data_handler=self.emg_handler, communicator=None)


def exit():
    print("Intercepted")
    sys.exit()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, exit)
    KeyWidget().start()
