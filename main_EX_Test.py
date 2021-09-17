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

# Run this command via SSH: $ sudo python3 main_EX_Test.py
# command F to find and decomment  all STM portions before testing with STM

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
    ## Set up message logs
    run_timestamp = datetime.now().isoformat()
    os.makedirs('logs', exist_ok=True)
    logfile = open(os.path.join('logs', 'rpi_received_log_' + run_timestamp + '.txt'), 'a+')
#     os.system("sudo hciconfig hci0 piscan")

    ## Initialisation - RPi Comms
    commsList = []
    commsList.append(STMComm())
    commsList.append(AndroidComm())
    #commsList.append(AppletComm())
    connect(commsList)

    STM = 0
    ANDROID = 1 # shld be 1
    #APPLET = 2 # shld be 2

    msgQueue = Queue()
    STMListener = Process(target=listen, args=(msgQueue, commsList[STM]))
    androidListener = Process(target=listen, args=(msgQueue, commsList[ANDROID]))
    #appletListener = Process(target=listen, args=(msgQueue, commsList[APPLET]))

#     STMListener.start()
    androidListener.start()
    #appletListener.start()

    try:
        while True:
            message = msgQueue.get()

            if message == None:
                continue

            try:
                logfile.write(message)
            except Exception as e:
                print('[LOGFILE_ERROR] Logfile Write Error: %s' % str(e))

            msgSplit = message.split(', ')
            command = msgSplit[1]
            command = command.rstrip(command[-1])
            command = command.lstrip(command[0])

#             sender = msgSplit[0].split(' > ')[0]
#             receiver = msgSplit[0].split(' > ')[1]
#             info = msgSplit[2]

            ## W, A, D: From Android or Applet
            if command == "W1":
                # Move forward
                commsList[STM].write('S20\r\n')
                #commsList[ANDROID].write('RPi > Android, "{"status":"moving forward"}", Robot is moving forward')
#                 commsList[ANDROID].write('RPi > Android, "{"move":[{"direction":"forward"}]}", Robot goes forward on the android map')
                #commsList[APPLET].write('received')

            elif command == "R1":
                # Move back
                commsList[STM].write('R90\r\n')
                #commsList[ANDROID].write('RPi > Android, "{"status":"turning right"}", Robot is turning right')
                #commsList[ANDROID].write('RPi > Android, "{"move":[{"direction":"backward"}]}", Robot goes backward on the android map')
                #commsList[APPLET].write('received')


    except Exception as e:
        print("[MAIN_ERROR] Error. Prepare to shutdown...")

    finally:
        #commsList[STM].disconnect()
        commsList[ANDROID].disconnect()
        commsList[APPLET].disconnect()
        logfile.close()
        sys.exit(0)
