from collections import deque
from threading import Lock

import myo


class EMGConnector:
    def __init__(self, communicator, data_handler=None):
        myo.init()
        hub = myo.Hub()
        listener = EmgCollector(50, communicator, data_handler)
        while hub.run(listener.on_event, 500):
            pass


class EmgCollector(myo.DeviceListener):

    def __init__(self, n, communicator, data_handler):
        self.n = n
        self.lock = Lock()
        self.emg_data_queue = deque(maxlen=n)
        self.communicator = communicator
        self.data_handler = data_handler

    def get_emg_data(self):
        with self.lock:
            return list(self.emg_data_queue)

    def on_connected(self, event):
        event.device.stream_emg(True)

    def on_emg(self, event):
        with self.lock:
            self.emg_data_queue.append((event.timestamp, event.emg))
            timestamp = event.timestamp
            value = event.emg
            if self.communicator is not None:
                value.append(timestamp)
                self.communicator.data_signal.emit(value)
            if self.data_handler is not None:
                self.data_handler(value)
