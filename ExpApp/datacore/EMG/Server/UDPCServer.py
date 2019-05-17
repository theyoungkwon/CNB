import ast
import socket
import time

from ExpApp.Utils.datacore_constants import get_random_gesture, label_to_gesture

import tensorflow as tf
import numpy as np

from ExpApp.datacore.EMG.EMG_CNN import EMG_CNN

PACKAGE_MAX_SIZE = 25
cfg = {
    "start": 0,
    "end": 200,
    "dir": "Ubi6_0_200",
    "shift": 160
}
clf = EMG_CNN.load(cfg["dir"], params=cfg)


class UDPCServer:

    def formPacket(self, gesture):
        while len(gesture) < PACKAGE_MAX_SIZE:
            gesture += "_"
        return gesture

    def __init__(self, debug=False) -> None:
        super().__init__()
        self.debug = debug
        ip = '192.168.137.1'
        port = 90
        buffer_size = 6000
        udp_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        udp_server_socket.bind((ip, port))
        print("UDP Classification server on " + ip + ":" + str(port))
        while (True):
            bytes_address_pair = udp_server_socket.recvfrom(buffer_size)
            message = bytes_address_pair[0]
            data = message.decode("utf-8")
            data = data.split("_")
            emg_str = data[0]
            client_time = data[1]
            gesture = ""
            server_time = 0
            if not self.debug:
                start = emg_str.find('[')
                end = emg_str.rfind(']') + 1
                emg_package = emg_str[start:end]
                emg_data = ast.literal_eval(emg_package)[0:200]
                emg_data = np.asarray([emg_data]).astype(np.float32)
                start_time = int(round(time.time() * 1000))
                eval_input_fn = tf.estimator.inputs.numpy_input_fn(
                    x={"x": emg_data},
                    num_epochs=1,
                    shuffle=False)
                predictions = clf.predict(input_fn=eval_input_fn)
                for prediction in predictions:
                    # gesture = label_to_gesture(prediction['classes'])
                    gesture = get_random_gesture()
                end_time = int(round(time.time() * 1000))
                server_time = end_time - start_time
            else:
                gesture = get_random_gesture()
            address = bytes_address_pair[1]
            print(address)
            bytes_to_send = str.encode(self.formPacket(gesture + "_" + client_time + "_" + str(server_time)))
            udp_server_socket.sendto(bytes_to_send, address)


if __name__ == '__main__':
    tf.logging.set_verbosity(tf.logging.ERROR)
    UDPCServer(debug=True)
