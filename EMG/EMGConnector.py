from collections import deque
from time import time
from threading import Lock

import myo


class EMGConnector:
    def __init__(self, communicator=None, data_handler=None, imu_handler=None):
        myo.init("C:\\myo\\myo64.dll")
        hub = myo.Hub()
        listener = EmgCollector(n=50,  # redundant
                                communicator=communicator,
                                emg_data_handler=data_handler,
                                imu_data_handler=imu_handler)
        while hub.run(listener.on_event, 500):
            pass


class EmgCollector(myo.DeviceListener):

    def __init__(self, n, communicator, emg_data_handler, imu_data_handler=None):
        self.n = n
        self.lock = Lock()
        self.emg_data_queue = deque(maxlen=n)
        self.communicator = communicator
        self.emg_data_handler = emg_data_handler
        self.imu_data_handler = imu_data_handler
        self.imu = []

    def get_emg_data(self):
        with self.lock:
            return list(self.emg_data_queue)

    def on_connected(self, event):
        event.device.stream_emg(True)

    def on_emg(self, event):
        with self.lock:
            self.emg_data_queue.append((event.timestamp, event.emg))
            # print(dir(event))
            # print(event.orientation)
            timestamp = event.timestamp
            value = event.emg
            value.extend(self.imu)
            value.append(time())
            if self.communicator is not None:
                # TODO append the timestamp from myo
                self.communicator.data_signal.emit(value)
            if self.emg_data_handler is not None:
                self.emg_data_handler(value)

    def on_orientation(self, event):
        orientation = event.orientation
        acceleration = event.acceleration
        gyroscope = event.gyroscope
        self.imu = []
        self.imu.extend(orientation)
        self.imu.extend(acceleration)
        self.imu.extend(gyroscope)
        if self.imu_data_handler is not None:
            self.imu_data_handler([orientation, acceleration, gyroscope])
