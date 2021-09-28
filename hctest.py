from multiprocessing import Process, Queue
from time import sleep

from STMComms import STMComm
from AndroidComms import AndroidComm
from AppletComms import AppletComm

import numpy as np
import os
import json
import sys
from copy import deepcopy
from datetime import datetime
import argparse


# from infer import infer 


# Setup to handle cases where serial port jumps to USB1
# Run this command via SSH: $ sudo python3 main_EX_Test.py --port /dev/ttyUSB1 (ttyUSB0 is the default)
# parser = argparse.ArgumentParser(description='MDP RPi Module')
# parser.add_argument('--port', type=str, default='/dev/ttyUSB0', help='STM Serial port')
# args = parser.parse_args()
# stm_port = args.port

def connect(commsList):
    for comms in commsList:
        comms.connect()


def disconnect(commsList):
    for comms in commsList:
        comms.disconnect()


def listen(msgQueue, com):
    while True:
        msg = com.read()
        msgQueue.put(msg)

if __name__ == '__main__':

    ## Initialisation - RPi Comms
    commsList = []
    commsList.append(STMComm())
#     commsList.append(AppletComm())

    connect(commsList)

    STM = 0
#     ANDROID = 0 # shld be 1
#     APPLET = 2 # shld be 2



    msgQueue = Queue()
    STMListener = Process(target=listen, args=(msgQueue, commsList[STM]))
#     androidListener = Process(target=listen, args=(msgQueue, commsList[ANDROID]))
#     appletListener = Process(target=listen, args=(msgQueue, commsList[APPLET]))

    STMListener.start()
#     androidListener.start()
#     appletListener.start()
#     commsList[STM].write('dummy\r\n')
    response = ['W10', 'D17', 'W70', 'A6', 'W20', 'A11', 'W10', 'S40', 'C11', 'S10', 'A6', 'Z6', 'D6', 'Z6', 'D6', 'A6', 'W10', 'A17', 'C11', 'W30', 'A6', 'W50', 'D11', 'W10', 'D6', 'W10', 'D11', 'Z11', 'D6', 'W60', 'A6', 'W10', 'A6', 'W10', 'A17']
    print(response)

    try:
        for command in response:
        #message = command + '\r\n'
            commsList[STM].write(command)
            print(command)
            
            msg = msgQueue.get()
            while not_received:
            if msg == 'A':
                not_received = False
                continue



    except Exception as e:
        print("[MAIN_ERROR] Error. Prepare to shutdown...")

    finally:
        commsList[STM].disconnect()
#         commsList[APPLET].disconnect()
        sys.exit(0)
