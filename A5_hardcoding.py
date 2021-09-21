from datetime import datetime

import serial, os
from time import sleep
from multiprocessing import Process, Value, Queue, Manager


def STMConnect():
    print('Initializing Connections:')
    ser = serial.Serial(
        port='/dev/ttyUSB0',
        baudrate=115200,
    )
    print("initialize STMController successful")
    print("Writing test command")

    # ser.write(str.encode('Test'))


    ser.write(str.encode('S100\r\n')) #straight
    sleep(10)
    #take pic to detect face? if no face, then:

    ser.write(str.encode('L90\r\n'))
    sleep(10)
    ser.write(str.encode('R90\r\n'))
    sleep(10)
    # ser.write(str.encode('S5\r\n'))
    # sleep(10)

    #take pic to detect face? if no face, then:

    ser.write(str.encode('R90\r\n')) #right turn
    sleep(10)

    #take pic to detect face? if no face, then:

    ser.write(str.encode('R90\r\n')) #right turn
    sleep(10)
    # ser.write(b'Test')
    print('Done')

if __name__ == '__main__':
    STMConnect()



