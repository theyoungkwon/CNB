import enum
import threading
from time import time
import numpy

from pynput.keyboard import Key, Listener

from ExpApp.Utils.constants import KEYS_SUFFIX


class KeyboardLogger():
    class Event(enum.Enum):
        Press = 1
        Release = 2

    def __init__(self, file_name=None, debug=False, handler=None) -> None:
        super().__init__()
        self.listener = None
        self.data = []
        self.debug = debug
        self.handler = handler
        self.file_name = file_name
        self.last_pressed_key = None
        self.last_released_key = None

    def on_press(self, key):
        if self.handler is not None and callable(self.handler):
            self.handler(key)
        if key != self.last_pressed_key and hasattr(key, 'vk'):
            timestamp = time()
            self.data.append([timestamp, key.vk, KeyboardLogger.Event.Press.value])
            self.last_released_key = None
            self.last_pressed_key = key
            if self.debug:
                print('{0} pressed at {1}'.format(key, timestamp))

    def on_release(self, key):
        if key != self.last_released_key and hasattr(key, 'vk'):
            timestamp = time()
            self.data.append([timestamp, key.vk, KeyboardLogger.Event.Release.value])
            self.last_released_key = key
            self.last_pressed_key = None
            if self.debug:
                print('{0} released at {1}'.format(key, timestamp))

    def start_thread(self):
        if self.debug:
            print("Logger started")
        self.listener = Listener(on_press=self.on_press, on_release=self.on_release)
        with self.listener:
            self.listener.join()

    def start(self):
        listener_thread = threading.Thread(target=self.start_thread)
        listener_thread.start()

    def stop(self):
        if self.debug:
            print("Logger stopped")
        if self.file_name is None:
            return
        if self.listener is not None:
            self.listener.stop()
        numpy.savetxt(self.file_name + KEYS_SUFFIX, self.data)


if __name__ == '__main__':
    logger = KeyboardLogger(file_name="test_keyboard_file", debug=True)
    logger.start()
    threading.Timer(5, logger.stop).start()
