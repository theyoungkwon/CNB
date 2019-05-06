import socket

from ExpApp.Utils.datacore_constants import get_random_gesture

import tensorflow as tf

PACKAGE_MAX_SIZE = 25

class UDPCServer:

    def formPacket(self, gesture):
        while len(gesture) < PACKAGE_MAX_SIZE:
            gesture += "_"
        return gesture

    def __init__(self, debug=False) -> None:
        super().__init__()
        ip = '192.168.137.1'
        port = 90
        buffer_size = 3610
        udp_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        udp_server_socket.bind((ip, port))
        print("UDP Classification server on " + ip + ":" + str(port))
        while (True):
            bytes_address_pair = udp_server_socket.recvfrom(buffer_size)
            message = bytes_address_pair[0]
            data = message.decode("utf-8")
            data = data.split("_")
            emg = data[0]
            time = data[1]
            # feed bytes from emg to classifier
            address = bytes_address_pair[1]
            print(address)
            bytes_to_send = str.encode(self.formPacket(get_random_gesture() + "_" + time))
            udp_server_socket.sendto(bytes_to_send, address)


if __name__ == '__main__':
    tf.logging.set_verbosity(tf.logging.ERROR)
    UDPCServer(debug=True)
