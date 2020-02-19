from collections import deque
from time import time
from threading import Lock

import myo


class EMGConnector:
    def __init__(self,
                 communicator=None,
                 imu_communicator=None,
                 data_handler=None,
                 imu_handler=None,
                 imu_handlers=[],
                 data_handlers=[]):
        myo.init("C:\\myo\\myo64.dll")
        hub = myo.Hub()
        listener = EmgCollector(communicator=communicator,
                                imu_communicator=imu_communicator,
                                emg_data_handler=data_handler,
                                imu_data_handler=imu_handler,
                                imu_handlers=imu_handlers,
                                data_handlers=data_handlers)
        while hub.run(listener.on_event, 500):
            pass


class EmgCollector(myo.DeviceListener):

    def __init__(self,
                 communicator,
                 emg_data_handler,
                 imu_communicator=None,
                 communicators=None,
                 imu_data_handler=None,
                 imu_handlers=None,
                 data_handlers=None):

        if data_handlers is None:
            data_handlers = []
        self.communicators = []
        if not communicators and communicator:
            self.communicators.append(communicator)

        self.imu_handlers = []
        if not imu_handlers and imu_data_handler:
            self.imu_handlers.append(imu_data_handler)
        else:
            self.imu_handlers = imu_handlers

        self.data_handlers = []
        if not data_handlers and emg_data_handler:
            self.data_handlers.append(emg_data_handler)
        else:
            self.data_handlers = data_handlers

        self.imu_communicator = imu_communicator

        self.imu = []
        self.myos = {}
        self.myo_index = 0

    def on_connected(self, event):
        event.device.stream_emg(True)
        self.myos.update({str(event.device): self.myo_index})
        self.myo_index += 1

    def on_emg(self, event):
        # 8xEMG | 10xIMU | PC timestamp | Myo timestamp
        timestamp = event.timestamp
        value = event.emg
        value.extend(self.imu)
        value.append(time())
        value.append(timestamp)
        if self.communicators and len(self.communicators) > 0:
            current_index = 0
            self.communicators[current_index].data_signal.emit(value)
        if self.data_handlers and len(self.data_handlers) > 0:
            current_index = 0
            self.data_handlers[current_index](value)

    def on_orientation(self, event):
        orientation = event.orientation
        acceleration = event.acceleration
        gyroscope = event.gyroscope
        self.imu = []
        self.imu.extend(orientation)
        self.imu.extend(acceleration)
        self.imu.extend(gyroscope)
        if self.imu_communicator is not None:
            self.imu_communicator.data_signal.emit(self.imu)

        if self.imu_handlers and len(self.imu_handlers) > 0:
            current_index = 0
            self.imu_handlers[current_index]([orientation, acceleration, gyroscope])

