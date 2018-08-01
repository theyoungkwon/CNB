import sys;

sys.path.append('..')  # help python find cyton.py relative to scripts folder
from ExpApp.API.openbci import cyton as bci
import time


class Connector:
    def __init__(self, port='COM3'):
        self.board = bci.OpenBCICyton(port=port, scaled_output=False, log=True)
        time.sleep(10)

    def attach_handlers(self, handlers):
        self.board.start_streaming(handlers)
        self.board.print_bytes_in()
