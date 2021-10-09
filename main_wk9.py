from multiprocessing import Process, Queue
from time import sleep
import time

from STMComms import STMComm
from AndroidComms import AndroidComm
# from AppletComms2 import AppletComm

import traceback
import os
import json
import sys
from datetime import datetime
from turningCommands import turning_cmds

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
    # os.makedirs('logs', exist_ok=True)
    logfile = open(os.path.join('logs', 'rpi_received_log_' + run_timestamp + '.txt'), 'a+')
    os.system("sudo hciconfig hci0 piscan")

    ## Initialisation - RPi Comms
    commsList = []
    commsList.append(STMComm())
    commsList.append(AndroidComm())
#     commsList.append(AppletComm())

    connect(commsList)

    STM = 0
    ANDROID = 1 # shld be 1
#     APPLET = 2 # shld be 2

    msgQueue = Queue()
    STMListener = Process(target=listen, args=(msgQueue, commsList[STM]))
    androidListener = Process(target=listen, args=(msgQueue, commsList[ANDROID]))
#     appletListener = Process(target=listen, args=(msgQueue, commsList[APPLET]))

    STMListener.start()
    androidListener.start()
#     appletListener.start()

    turning_commands = turning_cmds
    received = True #for STM acknowledgment
    running = True
    forward = True #True if going towards obstacle; False if moving towards carpark
    sensor_value = -1 #default?
    first_ack = True #first write to STM
    turning = False #True if going through turning motion, False otherwise
    timeSinceLastCommand = 0
    lastTick = time.time()
    lastcommand = None
    
    try:
        while running:
            message = msgQueue.get()

            if message == None:
                currTime = time.time()
                timeSinceLastCommand += currTime - lastTick
                lastTick = currTime
                #if no msg received, add time to timeSinceLastCommand
                continue
            elif message == 'A': #receipt from STM
                received = True
                print('ack received')
                timeSinceLastCommand = 0

                if first_ack:
                    first_ack = False
                elif turning:
                    lastcommand = turning_commands.pop(0)
                    msgQueue.put(lastcommand)
                    if len(turning_commands) == 0: #if last turn command, set turning to False
                        turning = False
                        forward = False
                else:
                    msgQueue.put({"command": "move", "direction": 'W'})
                    lastcommand = {"command": "move", "direction": 'W'}
                #note fwd dist is between 50 - 200 cm
                continue
                #see if can repeat the command if
            elif message.isdigit() or (message.startswith('-') and message[1:].isdigit()): #STM sensor value
                sensor_value = int(message)
                timeSinceLastCommand = 0

                if sensor_value == 20: #condition to check
                    turning = True
                    lastcommand = turning_commands.pop(0)
                    msgQueue.put(lastcommand)
                #     #execute turn sequence by adding commands from list, maybe read from text file, or use a harcoded list
                continue
            else:
                if timeSinceLastCommand > 10:
                    msgQueue.put(lastcommand)
                    continue

            try:
                logfile.write(str(message))
            except Exception as e:
                print('[LOGFILE_ERROR] Logfile Write Error: %s' % str(e))

            if isinstance(message, str) and message != 'A' and (not message.isdigit()): #from Android
                response = json.loads(message)
            else:
                response = message
            print(type(response))
            command = response["command"]
            
            if command == 'move' and received == True: #check if STM always sends received after every movement
                cmd = response['direction']
                if cmd == 'W': #from android
                    commsList[STM].write('W30') #just change the movement here only
                    commsList[ANDROID].write('{"status":"moving forward"}')
                    #change the coordinates accordingly
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
                    commsList[ANDROID].write('{ "robot": {"x":'+ str(response["end_state"][0]) +',"y":'+str(response["end_state"][1])+', "angle":'+str(-1 * (int(response["end_state"][2]) - 90))+'} }')

            elif command == 'auto': #start button pressed from Android
                print('mode: ' + response['mode'])
                if response['mode'] == 'racecar':
                    #To do; android start button
                    msgQueue.put({"command": "move", "direction": 'W'})

            received = False
            print('waiting for ack')


    except Exception as e:
        print(traceback.format_exc())
        # print("[MAIN_ERROR] Error. Prepare to shutdown")

    finally:
        commsList[STM].disconnect()
        commsList[ANDROID].disconnect()
#         commsList[APPLET].disconnect()
        logfile.close()
        sys.exit(0)
