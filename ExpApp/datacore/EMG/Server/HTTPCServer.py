import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qsl
import ast

import gumpy
import tensorflow as tf
import numpy as np

from ExpApp.Utils.datacore_constants import label_to_gesture, get_random_gesture
from ExpApp.datacore.EMG.EMG_CNN import EMG_CNN

cfg = {
    "start": 0,
    "end": 200,
    "dir": "CNN_EXPORT",
    "shift": 160
}
clf = EMG_CNN.load(cfg["dir"], params=cfg)


class HTTPCServer:
    def __init__(self, debug=False):
        def handler(*args):
            RequestHandler(*args, debug=debug)

        ip = '192.168.137.1'
        port = 80
        server = HTTPServer((ip, port), handler)
        print("HTTP Classification server on " + ip + ":" + str(port))
        server.serve_forever()


class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, debug):
        self.EMG_data = []
        self.debug = debug
        BaseHTTPRequestHandler.__init__(self, *args)

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes("It's alive!", "utf8"))
        return

    def do_POST(self):
        self.send_response(200)
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        start_time = int(round(time.time() * 1000))
        parsed = parse_qsl(post_data)
        str_data = parsed[0][1].decode("utf-8")
        start = str_data.find('[')
        end = str_data.rfind(']') + 1
        emg_package = str_data[start:end]
        emg_data = ast.literal_eval(emg_package)[0:200]
        emg_data = np.asarray([emg_data]).astype(np.float32)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        gesture = ""
        if not self.debug:
            eval_input_fn = tf.estimator.inputs.numpy_input_fn(
                x={"x": emg_data},
                num_epochs=1,
                shuffle=False)
            predictions = clf.predict(input_fn=eval_input_fn)
            for prediction in predictions:
                gesture = label_to_gesture(prediction['classes'])
            end_time = int(round(time.time() * 1000))
            print(str(end_time - start_time) + ": " + gesture)
        else:
            gesture = get_random_gesture()
        time_value = 0
        if len(parsed) > 1:
            time_str = parsed[1][1].decode("utf-8")
            start = time_str.rfind('\"')
            end = time_str.find('-')
            time_value = int(time_str[start+1:end])
        self.wfile.write(bytes(gesture + "_" + str(time_value), "utf8"))
        return


if __name__ == '__main__':
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    tf.logging.set_verbosity(tf.logging.ERROR)
    HTTPCServer(debug=True)
