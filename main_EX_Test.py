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


# from infer import infer 


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

    try:
        while True:
            message = msgQueue.get()
            
            if message == None:
                continue
            
            response = json.loads(message)
            command = response['command']
            
            try:
                logfile.write(message)
            except Exception as e:
                print('[LOGFILE_ERROR] Logfile Write Error: %s' % str(e))
            
            if command == 'move':
                cmd = response['direction']
                if cmd == 'W': #from android
                    commsList[STM].write('W30')
                    commsList[ANDROID].write('{"status":"moving forward"}')
                elif cmd == 'S':
                    commsList[STM].write('S30')
                    commsList[ANDROID].write('{"status":"moving back"}')
                elif cmd == 'D':
                    commsList[STM].write('D90')
                    commsList[ANDROID].write('{"status":"turning right"}')
                elif cmd == 'A':
                    commsList[STM].write('A90')
                    commsList[ANDROID].write('{"status":"turning left"}')
                else:
                    commsList[STM].write(str(response['direction']))
                    commsList[ANDROID].write('{"status":"robot moving"}')

                    
            elif command == 'obstacle':
                obstacles = response['obstacle']
                print('obstacle received: ', obstacles)
                obstacles = str(obstacles)
                commsList[APPLET].write(obstacles)

                #TODO
            
            elif command == 'auto':
                mode = response['mode']
                print('mode: ' + mode)
                mode=str(mode)
                commsList[APPLET].write(mode)



#             msgSplit = message.split(', ')
#             command = msgSplit[1]
#             command = command.rstrip(command[-1])
#             command = command.lstrip(command[0])

#             sender = msgSplit[0].split(' > ')[0]
#             receiver = msgSplit[0].split(' > ')[1]
#             info = msgSplit[2]

            ## W, A, D: From Android or Applet
#             if command == "W":
#                 # Move forward
#                 commsList[STM].write('W30')
#                 commsList[ANDROID].write('{"status":"moving forward"}')
# #                 commsList[APPLET].write('W received')
# 
#             elif command == "D":
#                 # turn right
#                 
# #                 commsList[APPLET].write('D90 received')
#             
#             elif command == "A":
#                 # turn right
#                 
# #                 commsList[APPLET].write('A90 received')
#             
#             elif command == "S":
#                 # move back
#                 
# #                 commsList[APPLET].write('S received')
#             elif command == "{"auto":"racecar"}"
#             elif command == "I": #take picture and send to Brandon's laptop for IR
#                 response = infer()
#                 if response != []:
#                     print(response)
#                     print('iteration: ' + str(_))
#                     for i in range(len(response)):
#                         if response[i]["image_id"] == '0' and response[i]["description"] == 'Obstacle':
#                             return ('Done')


    except Exception as e:
        print(traceback.format_exc())
        print("[MAIN_ERROR] Error. Prepare to shutdown...")

    finally:
        commsList[STM].disconnect()
        commsList[ANDROID].disconnect()
#         commsList[APPLET].disconnect()
#         logfile.close()
        sys.exit(0)
