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
from infer import infer 


# Setup to handle cases where serial port jumps to USB1
# Run this command via SSH: $ sudo python3 main_EX_Test.py --port /dev/ttyUSB1 (ttyUSB0 is the default)
parser = argparse.ArgumentParser(description='MDP RPi Module')
parser.add_argument('--port', type=str, default='/dev/ttyUSB0', help='STM Serial port')
args = parser.parse_args()
stm_port = args.port

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
    os.system("sudo hciconfig hci0 piscan")
    os.system("sudo systemctl start rfcomm")

    ## Initialisation - RPi Comms
    commsList = []
#     commsList.append(STMComm(port=stm_port))
    commsList.append(AndroidComm())
    commsList.append(AppletComm())
    connect(commsList)

#     STM = 0
    ANDROID = 0 # shld be 1
    APPLET = 1 # shld be 2

    msgQueue = Queue()
#     STMListener = Process(target=listen, args=(msgQueue, commsList[STM]))
    androidListener = Process(target=listen, args=(msgQueue, commsList[ANDROID]))
    appletListener = Process(target=listen, args=(msgQueue, commsList[APPLET]))

#     STMListener.start()
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
                #commsList[STM].write('S20')
                commsList[ANDROID].write('RPi > Android, "{"status":"moving forward"}", Robot is moving forward\n')
                commsList[ANDROID].write('RPi > Android, "{"move":[{"direction":"forward"}]}", Robot goes forward on the android map')
                commsList[APPLET].write('W1 received')

            elif command == "D90":
                # turn right
                #commsList[STM].write('D90\r\n')
                commsList[ANDROID].write('RPi > Android, "{"status":"turning right"}", Robot is turning right')
                commsList[ANDROID].write('RPi > Android, "{"move":[{"direction":"right"}]}", Robot goes backward on the android map')
                commsList[APPLET].write('D90 received')
            
            elif command == "A90":
                # turn right
                #commsList[STM].write('A90\r\n')
                commsList[ANDROID].write('RPi > Android, "{"status":"turning left"}", Robot is turning right')
                commsList[ANDROID].write('RPi > Android, "{"move":[{"direction":"left"}]}", Robot goes backward on the android map')
                commsList[APPLET].write('A90 received')
            
#             elif command == "I": #take picture and send to Brandon's laptop for IR
#                 response = infer()
#                 if response != []:
#                     print(response)
#                     print('iteration: ' + str(_))
#                     for i in range(len(response)):
#                         if response[i]["image_id"] == '0' and response[i]["description"] == 'Obstacle':
#                             return ('Done')


    except Exception as e:
        print("[MAIN_ERROR] Error. Prepare to shutdown...")

    finally:
        #commsList[STM].disconnect()
        commsList[ANDROID].disconnect()
        commsList[APPLET].disconnect()
        logfile.close()
        sys.exit(0)
