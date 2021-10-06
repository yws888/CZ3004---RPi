from multiprocessing import Process, Queue
from time import sleep

from STMComms import STMComm
from AndroidComms import AndroidComm
from AppletComms2 import AppletComm

import numpy as np
import os
import json
import sys
from copy import deepcopy
from datetime import datetime
import argparse


from infer import infer


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
        #if integer from sensor, add to another queue?
        

if __name__ == '__main__':
    ## Set up message logs
    run_timestamp = datetime.now().isoformat()
    os.makedirs('logs', exist_ok=True)
    logfile = open(os.path.join('logs', 'rpi_received_log_' + run_timestamp + '.txt'), 'a+')
    os.system("sudo hciconfig hci0 piscan")

    ## Initialisation - RPi Comms
    commsList = []
    commsList.append(STMComm())
    commsList.append(AndroidComm())
    commsList.append(AppletComm())

    connect(commsList)

    STM = 0
    ANDROID = 1 # shld be 1
    APPLET = 2 # shld be 2

    msgQueue = Queue()
    STMListener = Process(target=listen, args=(msgQueue, commsList[STM]))
    androidListener = Process(target=listen, args=(msgQueue, commsList[ANDROID]))
#     appletListener = Process(target=listen, args=(msgQueue, commsList[APPLET]))

    STMListener.start()
    androidListener.start()
#     appletListener.start()
#     commsList[STM].write('dummy\r\n')

    algoCommands = []
    received = True

    try:
        while True:
            message = msgQueue.get()
            
            if message == None:
                continue
            elif message == 'A': #receipt from STM
                received = True
                msgQueue.put(algoCommands.pop(0))
                continue
            
            response = json.loads(message)
            command = response['command']
            
            try:
                logfile.write(message)
            except Exception as e:
                print('[LOGFILE_ERROR] Logfile Write Error: %s' % str(e))
            
            if command == 'move' and received == True: #check if STM always sends received after every movement
                cmd = response['direction']
                if cmd == 'W': #from android
                    commsList[STM].write('W30')
                    commsList[ANDROID].write('{"status":"moving forward"}')
                    received = False
                elif cmd == 'S':
                    commsList[STM].write('S30')
                    commsList[ANDROID].write('{"status":"moving back"}')
                    received = False
                elif cmd == 'D':
                    commsList[STM].write('D90')
                    commsList[ANDROID].write('{"status":"turning right"}')
                    received = False
                elif cmd == 'A':
                    commsList[STM].write('A90')
                    commsList[ANDROID].write('{"status":"turning left"}')
                    received = False
                else:
                    commsList[STM].write(str(response['direction']))
                    #commsList[ANDROID].write('{"status":"robot moving"}')
                    commsList[ANDROID].write('{ "robot": {x:x,y:y, angle:angle} }') #update after each mvmt based on algo commands
                    received = False

            elif command == 'obstacle': #receiving obstacle coordinates and info from Android
                obstacles = response['obstacle']
                print('obstacle received: ', obstacles)
                obstacles = str(obstacles)
                commsList[APPLET].write(obstacles)

                #TODO
            
            elif command == 'auto': #start button pressed from Android
                print('mode: ' + response['mode'])
                if response['mode'] == 'obstacle':
                    print('retrieving info from Algo')
                #print('starting Robot movement for IR')
                    # mode=str(mode)
                    algoResponse = commsList[APPLET].write(mode)
                #insert code for handling algoResponse here


            elif command == "picture": #take picture and send to laptop for IR; ideally x, y coordinates of obstacle should be in the response json too

                irResponse = infer()
                if irResponse != []:
                    print(irResponse)
                    for i in range(len(irResponse)):
                        # if response[i]["image_id"] == '0' and response[i]["description"] == 'Obstacle':
                        print(i)
                        image_id = irResponse[i]["image_id"]
                        commsList[ANDROID].write('{"image":{"x":' + response['coordinates']['x'] + ',"y": ' + response['coordinates']['y'] + ', "imageID": ' + image_id + '}}')

    except Exception as e:
        print(traceback.format_exc())
        print("[MAIN_ERROR] Error. Prepare to shutdown...")

    finally:
        commsList[STM].disconnect()
        commsList[ANDROID].disconnect()
#         commsList[APPLET].disconnect()
        logfile.close()
        sys.exit(0)
