import os
from collections import deque

import numpy as np
from tensorflow_core.python.keras.saving.save import load_model

from EMG.EMGConnector import EMGConnector
from ExpApp.Utils.datacore_constants import INPUT_SET, KERAS_FRAME_LENGTH, \
    KERAS_BATCH_SIZE, KeyConstants


class EasyPredictor:

    def __init__(self, model_path=os.path.dirname(__file__) + "/../datacore/cnn_qwerty_debug", _set=INPUT_SET, debug=False, key_mode=False) -> None:
        super().__init__()
        self.model = load_model(model_path)
        self.interval = KERAS_FRAME_LENGTH * .7
        self._set = _set
        self.predicted = None
        self.debug = debug
        self.i = 0
        self.key_mode = key_mode
        self.width = 8 if not self.key_mode else len(range(*KeyConstants.CHANNELS_CONFIG.indices(KeyConstants.TOTAL_CHANNELS)))
        self.height = KERAS_FRAME_LENGTH if not self.key_mode else KeyConstants.BEFORE + KeyConstants.AFTER
        self.stack = deque(maxlen=self.height)

    def predict(self):

        emg_data = np.asarray(self.stack).reshape((1, self.height, self.width, 1))
        emg_data = np.asarray(emg_data).astype(np.float32)
        y_pred = [np.argmax(y) for y in self.model.predict(emg_data, batch_size=KERAS_BATCH_SIZE)]
        if not self.key_mode:
            self.predicted = self._set[y_pred[0]]
        else:
            self.predicted = y_pred[0]
        if self.debug:
            print(self.predicted)

    def handleEMG(self, emg):
        # normal mode
        if not self.key_mode:
            self.stack.append(emg[:8])
        # key mode
        else:
            self.stack.append(emg[KeyConstants.CHANNELS_CONFIG])

        if len(self.stack) == self.height:
            self.i += 1

        if self.i >= self.interval:
            self.predict()
            self.i = 0
            return self.predicted
        return None


if __name__ == '__main__':
    online_predictor = EasyPredictor(_set=INPUT_SET, debug=True)
    EMGConnector(data_handler=online_predictor.handleEMG)
