import sys; sys.path.append('..') # help python find cyton.py relative to scripts folder
from ExpApp.API.openbci import cyton as bci
import logging
import time


def printData(sample):
    #os.system('clear')
    print("----------------")
    print("%f" %(sample.id))
    print(sample.channel_data)
    print(sample.aux_data)
    print("----------------")


def handleData(sample):

    return



if __name__ == '__main__':
    # port = '/dev/tty.OpenBCI-DN008VTF'
    # port = '/dev/tty.usbserial-DB00JAM0'
    # port = 'FTDIBUS\VID_0403+PID_6015+DQ0085S3A\0000'
    # port = '/dev/tty.OpenBCI-DN0096XA'
    port = 'COM3'
    baud = 115200
    logging.basicConfig(filename="test.log",format='%(asctime)s - %(levelname)s : %(message)s',level=logging.DEBUG)
    logging.info('---------LOG START-------------')
    board = bci.OpenBCICyton(port=port, scaled_output=False, log=True)
    print("Board Instantiated")
    # board.ser.write('v')
    time.sleep(10)
    board.start_streaming([printData, handleData])
    board.print_bytes_in()

