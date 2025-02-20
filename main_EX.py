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

# Run this command via SSH: $ sudo python3 main_EX.py

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
    commsList.append(STMComm())
    commsList.append(AndroidComm())
    commsList.append(AppletComm())
    connect(commsList)

    STM = 0
    ANDROID = 1
    APPLET = 2

    msgQueue = Queue()
    STMListener = Process(target=listen, args=(msgQueue, commsList[STM]))
    androidListener = Process(target=listen, args=(msgQueue, commsList[ANDROID]))
    appletListener = Process(target=listen, args=(msgQueue, commsList[APPLET]))

    STMListener.start()
    androidListener.start()
    appletListener.start()

    ## Initialise variables
    running = True
    exploring = False
    obsHex = ''
    expHex = ''
    imgs = ''

    try:
        while running:
            message = msgQueue.get()

            if message == None:
                continue

            try:
                logfile.write(message)
            except Exception as e:
                print('[LOGFILE_ERROR] Logfile Write Error: %s' % str(e))

            msgSplit = message.split('>')  # Try without semi-colon

            for i, value in enumerate(msgSplit):
                # Skip the first empty string
                if i == 0:
                    continue
                msg = json.loads(value)
                com = msg['com']

                ## W, A, D: From Android or Applet
                if com == 'W':
                    # Move forward
                    commsList[STM].write('W')
                    commsList[ANDROID].write('{"com": "statusUpdate", "status": "Moving forward"}')

                elif com == 'A':
                    # Turn left
                    commsList[STM].write('A')
                    commsList[ANDROID].write(';{"com": "statusUpdate", "status": "Turning left"}')

                elif com == 'D':
                    # Turn right
                    commsList[STM].write('D')
                    commsList[ANDROID].write(';{"com": "statusUpdate", "status": "Turning right"}')

                ## Exploration and Fastest Path: From Android and Applet
                elif com == 'ex':
                    # Start Explore
                    if exploring == False:
                        commsList[ANDROID].write(';{"com": "statusUpdate", "status": "Exploring"}')
                        commsList[APPLET].write('{"com": "statusUpdate", "status": "Exploring"}')
                        exploring = True

                elif com == 'fp':
                    # Start Fastest Path
                    commsList[ANDROID].write(';{"com": "statusUpdate", "status": "Running Fastest Path"}')
                    commsList[APPLET].write('{"com": "statusUpdate", "status": "Running Fastest Path"}')
                ## Additional command: Applet send path to STM
                elif com == 'fpath':
                    commsList[STM].write(msg['path'])

                ## Sensor Data: From STM
                elif com == 'SD':
                    ## All these is senior's group formatting JSON string in RPi.
                    ## We decided to bypass that assuming Applet can read the message by itself.
                    commsList[APPLET].write(json.dumps(msg))

                ## Sensor Data: From STM, after each move.
                elif com == 'MF':
                    data = deepcopy(msg)
                    data['status'] = "Finish Move"
                    commsList[APPLET].write(json.dumps(data))

                ## Way point and Starting point: From Android
                ## Check if WM might want to send without formatting data
                elif com == 'wayPoint':
                    # Received waypoint
                    wp = msg['wayPoint']
                    data = {'com': 'wayPoint', 'wayPoint': wp}
                    commsList[APPLET].write(json.dumps(data))

                elif com == 'startingPoint':
                    # Received robot starting position
                    sp = msg['startingPoint']
                    data = {'com': 'startingPoint', 'startingPoint': sp}
                    commsList[APPLET].write(json.dumps(data))

                elif com == 'K':
                    # Force get sensor data from STM
                    commsList[STM].write('K')

                ## R, F, C: all calibration - from Applet or STM
                elif com == 'R': # R got right, F for front
                    commsList[STM].write('R')
                    # if msg['from'] == 'Applet':
                    #     commsList[STM].write('R')
                    # elif msg['from'] == 'STM':
                    #     commsList[APPLET].write('{"com":"statusUpdate", "status":"Finish Calibrate"}')

                elif com == 'F': #nobangwallszxc
                    commsList[STM].write('F')
                    # if msg['from'] == 'Applet':
                    #     commsList[STM].write('F')
                    # elif msg['from'] == 'STM':
                    #     commsList[APPLET].write('{"com":"statusUpdate", "status":"Finish Calibrate"}')

                elif com == 'f': #nobangblockszxc
                    commsList[STM].write('f')
                    # if msg['from'] == 'Applet':
                    #     commsList[STM].write('f')
                    # elif msg['from'] == 'STM':
                    #     commsList[APPLET].write('{"com":"statusUpdate", "status":"Finish Calibrate"}')

                elif com == 'C':
                    if msg['from'] == 'Applet':
                        commsList[STM].write('C')
                    elif msg['from'] == 'STM':
                        commsList[APPLET].write('{"com":"statusUpdate", "status":"Finish Calibrate"}')

                elif com == 'Q': # calibrate start for exploration.
                    commsList[STM].write('Q')
                    # if msg['from'] == 'Applet':
                    #     commsList[STM].write('Q')
                    # elif msg['from'] == 'STM':
                    #     commsList[APPLET].write('{"com":"statusUpdate", "status":"Finish Calibrate (Right-facing)"}')

                elif com == 'q': # calibrate start for fastest path.
                    commsList[STM].write('q')

                elif com == 'RST':
                    exploring = False

                ## G, H: EX -> FP transition (from Applet)
                elif com == 'G':
                    exploring = False
                    commsList[STM].write('G')
                    commsList[APPLET].write('{"com":"statusUpdate", "status":"calibrated for FP"}')
                    commsList[ANDROID].write(';{"com":"statusUpdate", "status":"Exploration Complete"}')

                    jsonExpHex = " Exp " + expHex
                    # data = {'com':'statusUpdate', 'status':jsonExpHex}
                    # commsList[ANDROID].write(json.dumps(data))
                    # #commsList[ANDROID].write(';' + json.dumps(data))
                    jsonObsHex = ", Obj " + obsHex
                    # data = {'com':'statusUpdate', 'status':jsonObsHex}
                    # commsList[ANDROID].write(json.dumps(data))
                    # #commsList[ANDROID].write(';' + json.dumps(data))
                    jsonImgs = ", Img " + str(imgs)
                    # data = {'com':'statusUpdate', 'status':jsonImgs}
                    # commsList[ANDROID].write(json.dumps(data))
                    # #commsList[ANDROID].write(';' + json.dumps(data))

                    ## We try this - send at once
                    jsonString = jsonExpHex + jsonObsHex + jsonImgs
                    data = {'com': 'statusUpdate', 'status': jsonString}
                    commsList[ANDROID].write(json.dumps(data))

                elif com == 'H':
                    exploring = False
                    commsList[STM].write('H')
                    commsList[APPLET].write('{"com":"statusUpdate", "status":"calibrated for FP"}')
                    commsList[ANDROID].write(';{"com":"statusUpdate", "status":"Exploration Complete"}')

                    jsonExpHex = " Exp " + expHex
                    # data = {'com':'statusUpdate', 'status':jsonExpHex}
                    # commsList[ANDROID].write(json.dumps(data))
                    # #commsList[ANDROID].write(';' + json.dumps(data))
                    jsonObsHex = ", Obj " + obsHex
                    # data = {'com':'statusUpdate', 'status':jsonObsHex}
                    # commsList[ANDROID].write(json.dumps(data))
                    # #commsList[ANDROID].write(';' + json.dumps(data))
                    jsonImgs = ", Img " + str(imgs)
                    # data = {'com':'statusUpdate', 'status':jsonImgs}
                    # commsList[ANDROID].write(json.dumps(data))
                    # #commsList[ANDROID].write(';' + json.dumps(data))

                    ## We try this - send at once
                    jsonString = jsonExpHex + jsonObsHex + jsonImgs
                    data = {'com': 'statusUpdate', 'status': jsonString}
                    commsList[ANDROID].write(json.dumps(data))

                ## MDF: From Applet to Android
                elif com == 'MDF':
                    ## All these is senior's group formatting JSON string in RPi.
                    ## We decided to bypass that since Android can read the message by itself.
                    # Received MDF from applet, relay it to Android
                    # expHex = msg['expMDF']
                    # obsHex = msg['objMDF']  # obj and obs used interchangeably wah toh
                    # robotPos = msg['pos']
                    # imgs = msg['imgs']
                    #
                    # data = {'mapState': {'com': 'GS', 'obstacles': obsHex,
                    #                      'explored': expHex, 'robotPosition': robotPos, 'imgs': imgs}}

                    ## If line below is not a needed visual, we can leave it out
                    # commsList[ANDROID].write(
                    #     ';{"com": "statusUpdate", "status": "Moving to (' + str(robotPos[0]) + ',' + str(
                    #         robotPos[1]) + ')"}')
                    # commsList[ANDROID].write(';' + json.dumps(data))

                    commsList[ANDROID].write(json.dumps(msg))

    except Exception as e:
        print("[MAIN_ERROR] Error. Prepare to shutdown...")

    finally:
        commsList[STM].disconnect()
        commsList[ANDROID].disconnect()
        commsList[APPLET].disconnect()
        logfile.close()
        sys.exit(0)
