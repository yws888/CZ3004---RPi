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
    logfile = open(os.path.join('logs', 'rpilog_' + run_timestamp + '.txt'), 'a+')

    ## Initialisation - RPi Comms
    commsList = []
    #commsList.append(STMComm())
    commsList.append(AndroidComm())
    commsList.append(AppletComm())
    connect(commsList)

    #STM = 0
    ANDROID = 0
    APPLET = 1

    msgQueue = Queue()
    #STMListener = Process(target=listen, args=(msgQueue, commsList[STM]))
    androidListener = Process(target=listen, args=(msgQueue, commsList[ANDROID]))
    appletListener = Process(target=listen, args=(msgQueue, commsList[APPLET]))

    #STMListener.start()
    androidListener.start()
    appletListener.start()

    try:
        while True:
            message = msgQueue.get()

            if message == None:
                continue

            try:
                logfile.write(message)
            except Exception as e:
                print('[LOGFILE_ERROR] Logfile Write Error: %s' % str(e))

            msgSplit = message.split(',')
            sender = msgSplit[0].split('>')[0]
            receiver = msgSplit[0].split('>')[1]
            command = msgSplit[1]
            info = msgSplit[2]

            ## W, A, D: From Android or Applet
            if command == 'W1|':
                # Move forward
                #commsList[STM].write('W')
                commsList[ANDROID].write('{"com": "statusUpdate", "status": "Moving forward"}')
                commsList[APPLET].write('received')

            elif command == 'S1|':
                # Move back
                #commsList[STM].write('S')
                commsList[ANDROID].write(';{"com": "statusUpdate", "status": "Moving backward"}')
                commsList[APPLET].write('received')


            elif command == 'B|':
                # break and disconnect
                continue

    except Exception as e:
        print("[MAIN_ERROR] Error. Prepare to shutdown...")

    finally:
        #commsList[STM].disconnect()
        commsList[ANDROID].disconnect()
        commsList[APPLET].disconnect()
        logfile.close()
        sys.exit(0)
