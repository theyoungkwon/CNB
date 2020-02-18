import os
from collections import deque
from time import time

import numpy as np
from tensorflow_core.python.keras.saving.save import load_model

from EMG.EMGConnector import EMGConnector
from ExpApp.Utils.datacore_constants import INPUT_SET, \
    KERAS_BATCH_SIZE, RT_LAG, RT_OVERLAP, WINDOW_LENGTHS


class EasyPredictor:

    def __init__(self,
                 model_path=os.path.dirname(__file__) + "/../datacore/cnn_qwerty_debug",
                 _set=INPUT_SET,
                 debug=False,
                 w_length=WINDOW_LENGTHS[0],
                 lag_after_reset=RT_LAG,
                 w_overlap=RT_OVERLAP) -> None:
        super().__init__()
        self.model = load_model(model_path)
        self._set = _set
        self.predicted = None
        self.debug = debug
        self.lag_after_reset = lag_after_reset
        self.lag_counter = lag_after_reset
        self.width = 8
        self.w_length = w_length
        self.w_overlap = int(w_overlap * self.w_length)
        self.stack = deque(maxlen=self.w_length)
        self.model.predict(np.zeros((1, self.w_length, self.width, 1)), batch_size=KERAS_BATCH_SIZE)

    def predict(self):
        start_time = time()
        emg_data = np.asarray(self.stack).reshape((1, self.w_length, self.width, 1))
        emg_data = np.asarray(emg_data).astype(np.float32)
        y_pred = [np.argmax(y) for y in self.model.predict(emg_data, batch_size=KERAS_BATCH_SIZE)]
        self.predicted = self._set[y_pred[0]]
        if self.debug:
            print(str((time() - start_time) * 1000) + " : " + self.predicted)
        # removing all elements from deque except the ones for the window overlap
        while len(self.stack) > self.w_overlap:
            self.stack.popleft()
        return self.predicted

    def set_overlap(self, overlap):
        overlap = min(1., max(0., overlap))
        self.w_overlap = int(overlap * self.w_length)
        self.stack.clear()

    def set_length(self, length):
        length = min(200, max(20, length))
        self.w_length = length
        self.w_overlap = int(self.w_overlap * self.w_length)
        self.stack = deque(maxlen=self.w_length)

    def handle_emg(self, emg):
        if self.lag_counter > 0:
            self.lag_counter -= 1
            return
        self.stack.append(emg[:8])
        if len(self.stack) == self.w_length:
            return self.predict()
        return None

    def reset(self):
        self.stack.clear()
        self.lag_after_reset = self.lag_after_reset
        self.predicted = None


if __name__ == '__main__':
    online_predictor = EasyPredictor(_set=INPUT_SET, debug=True)
    EMGConnector(data_handler=online_predictor.handle_emg)
