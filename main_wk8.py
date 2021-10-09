from multiprocessing import Process, Queue
from time import sleep
import time

from STMComms import STMComm
from AndroidComms import AndroidComm
from AppletComms2 import AppletComm

import numpy as np
import os
import json
import sys
from datetime import datetime
import argparse
import requests
import traceback

from infer import infer
from generate_stitched import generate_stitched

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
    commsList[STM].write('W\r\n')

    algoCommands = []
    received = True
    running = True
    timeSinceLastCommand = 0
    lastTick = time.time()
    try:
        while running:
            message = msgQueue.get()

            currTick = time.time()
            timeSinceLastCommand += currTick - lastTick
            lastTick = currTick

            if message == None:
                continue
            elif message == 'A': #receipt from STM
                print('A received')
                received = True
                timeSinceLastCommand = 0
#                 print(msgQueue.qsize())
#                 if (not algoCommands) and (not msgQueue.empty()):
                print(algoCommands)

                if (len(algoCommands)!=0):
                    print(msgQueue.qsize())
                    msgQueue.put(algoCommands.pop(0))
                    print('popped')
                continue
            else:
                if timeSinceLastCommand > 10:
                    pass
                pass
            #if 10 seconds never receive anything, resend again            
                        
            if isinstance(message, str) and message != 'A':
                response = json.loads(message)
            else:
                response = message
            print(type(response))
            command = response["command"]
            
            if command == 'move' and received == True: #check if STM always sends received after every movement
                cmd = response["direction"]
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
                    commsList[STM].write(str(cmd))
#                     commsList[ANDROID].write('{"status":"robot moving"}')
                    temp=str(int(response["end_state"][2]))
                    commsList[ANDROID].write('{ "robot": {"x":'+ str(response["end_state"][0]) +',"y":'+str(response["end_state"][1])+', "angle":'+str(-1 * (int(response["end_state"][2]) - 90))+'} }')
                    #update after each mvmt based on algo commands
                    received = False

            elif command == 'obstacle': #receiving obstacle coordinates and info from Android
                obstacles = response['obstacle']
                print('obstacle received: ', obstacles)
                obstacles = str(obstacles)
                
                algoResponse = commsList[APPLET].write(obstacles)
#                 algoResponse = algoResponse.json()

            elif command == 'auto': #start button pressed from Android
                print('mode: ' + response['mode'])
                if response["mode"] == 'obstacle':
                    print('retrieving info from Algo')

                    #algoResponse = commsList[APPLET].write(mode)
                   
                    #algoResponse = requests.post("http://192.168.3.20:5000/simulate")
                    algoResponse = requests.get("http://192.168.3.20:5000/get_sim_output")
                    print(algoResponse)
                    algoResponse = algoResponse.json()
#                     print(algoResponse)
                    count = 0
                    for j, i in enumerate(algoResponse):
                        msgSplit = i['actions'].split('|')                       
                        for command in msgSplit:
                            if (command):
                                algoCommands.append( {"command": "move", "direction": command})
                        states = iter(i['discrete_states'])
                        next(states)
                        for state in states:
                            algoCommands[count]["end_state"] = state
                            count+=1
                        if (j == 0):
                            algoCommands.append( {"command": "move", "direction": "S15", "end_state":[5,5, 90.0]})
                            count+=1
                        algoCommands.append({"command": "picture", "coordinates": i['block']})
                        count+=1
# #                     
#                     for msg in algoCommands:
#                         msgQueue.put(algoCommands.pop(0))
                    
#                     print(algoCommands)
# #                     print(type(algoCommands[0]))
                    msgQueue.put(algoCommands.pop(0))


                elif response['mode'] == 'racecar':
                    continue

            elif command == "picture": #take picture and send to laptop for IR; ideally x, y coordinates of obstacle should be in the response json too
#                coordinates = send to 
                d = {}
                d['x']=response['coordinates'][0]
                d['y']=response['coordinates'][1]
                irResponse = infer(d)

                if irResponse == []:
                    # Run inference again
                    commsList[STM].write('S15')
                    # while msgQueue.get() != 'A':
                        # pass
                    sleep(1)
                    irResponse = infer(d)

                if irResponse != []:
                    print(irResponse)
                    for i in range(len(irResponse)):
                        # if response[i]["image_id"] == '0' and response[i]["description"] == 'Obstacle':
                        #think abt how to deal with image file
                        print(i)
                        image_id = irResponse[i]["image_id"]
                        commsList[ANDROID].write('{"image":{"x":' + str(response['coordinates'][0]) + ',"y": ' + str(response['coordinates'][1]) + ', "imageID": ' + str(image_id) + '}}')
                if (len(algoCommands)!=0):
                    msgQueue.put(algoCommands.pop(0))

    
    except Exception as e:
#         print(e)
#         print("[MAIN_ERROR] Error. Prepare to shutdown...")
        print(traceback.format_exc())

    finally:
        commsList[STM].disconnect()
        commsList[ANDROID].disconnect()
        generate_stitched()
#         commsList[APPLET].disconnect()
#         logfile.close()
        sys.exit(0)
