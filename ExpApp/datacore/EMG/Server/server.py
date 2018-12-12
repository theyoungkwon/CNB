from multiprocessing import Process, Queue
from http.server import BaseHTTPRequestHandler, HTTPServer
from time import sleep

from ExpApp.GUI.PyQt.Widgets.GestureWidget import gesture_widget_main
from ExpApp.Utils.datacore_constants import gestures


class GRServer:
    def __init__(self, cmd):
        def handler(*args):
            RequestHandler(cmd, *args)

        server = HTTPServer(('192.168.137.1', 80), handler)
        server.serve_forever()


class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, cmd, *args):
        self.cmd = cmd
        BaseHTTPRequestHandler.__init__(self, *args)

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes(self.cmd.get()[0], "utf8"))
        return

    def change_CMD(self, cmd):
        self.cmd = cmd


def server_main(q):
    GRServer(cmd=q)


def gesture_mock(q):
    while True:
        for key in gestures:
            q.put([gestures[key]])
            sleep(3)


def debug():
    q = Queue(maxsize=1)
    q.put(["PALM"])
    p2 = Process(target=server_main, args=(q,))
    p1 = Process(target=gesture_mock, args=(q,))
    p2.start()
    p1.start()
    p2.join()
    p1.join()


def release():
    q = Queue(maxsize=1)
    q.put("PALM")
    p2 = Process(target=server_main, args=(q,))
    p1 = Process(target=gesture_widget_main, args=(q,))
    p2.start()
    p1.start()
    p2.join()
    p1.join()


if __name__ == '__main__':
    release()
    # debug()
