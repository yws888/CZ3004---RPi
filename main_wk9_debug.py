from multiprocessing import Process, Queue
from time import sleep

from STMComms import STMComm
from AndroidComms import AndroidComm
from AppletComms import AppletComm

import traceback
import os
import json
import sys
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

    os.system("sudo hciconfig hci0 piscan")

    ## Initialisation - RPi Comms
    commsList = []
    commsList.append(AndroidComm())
    commsList.append(AppletComm())
    # commsList.append(STMComm())

    connect(commsList)

    ANDROID = 0 # shld be 1
    APPLET = 1
#     STM = 1


    msgQueue = Queue()
    # STMListener = Process(target=listen, args=(msgQueue, commsList[STM]))
    androidListener = Process(target=listen, args=(msgQueue, commsList[ANDROID]))
    appletListener = Process(target=listen, args=(msgQueue, commsList[APPLET]))

    # STMListener.start()
    androidListener.start()
    appletListener.start()
    #turning radius = 35 cm
    turning_commands = turning_cmds
    received = True #for STM acknowledgment
    running = True
    forward = True #True if going towards obstacle; False if moving towards carpark
    sensor_value = -1 #default?
    first_ack = True #first write to STM
    turning = False #True if going through turning motion, False otherwise
    lastcommand = None
    firstCmdAfterTurn = False

    commsList[APPLET].write('W') #just change the movement here only

    try:
        while running:

            message = msgQueue.get()

            if message is None:
                continue
            elif message == 'A': #receipt from STM
                received = True
                print('ack received')

                if first_ack: #for initial STM write
                    first_ack = False
                    commsList[APPLET].write('R') # or whatever value to get sensor reading; cant write here as it may enter queue later

                elif turning:
                    lastcommand = turning_commands.pop(0)
                    msgQueue.put(lastcommand)
                    if len(turning_commands) == 0: #if last turn command, set turning to False
                        turning = False
                        forward = False
                        firstCmdAfterTurn = True
                        commsList[APPLET].write('R')
                elif firstCmdAfterTurn:
                    firstCmdAfterTurn = False
                    dist = sensor_value + 20
                    direction = 'W' + str(dist)
                    msgQueue.put({"command": "move", "direction": direction})
                    lastcommand = {"command": "move", "direction": direction}
                else:
                    msgQueue.put({"command": "move", "direction": 'W'})
                    lastcommand = {"command": "move", "direction": 'W'}
                #note fwd dist is between 50 - 200 cm
                continue

            elif str(message).isdigit() or (str(message).startswith('-') and str(message)[1:].isdigit()): #STM sensor value
                sensor_value = int(message)

                if sensor_value == 20 and forward == True: #condition to check; indicates when to turn
                    turning = True
                    lastcommand = turning_commands.pop(0)
                    msgQueue.put(lastcommand)
                #     execute turn sequence by adding commands from list
                elif sensor_value == 10: #condition to check; indicates when to stop (i.e. in carpark). Also when turning back, to rely on count (i.e. no. of times forward just now) or sensor data?
                    msgQueue.close()
                    sys.exit(0)
                continue

            if isinstance(message, str) and message != 'A' and (not str(message).isdigit()): #from Android
                response = json.loads(message)
            else:
                response = message
#             print(type(response))
            command = response["command"]
            
            if command == 'move' and received == True: #check if STM always sends received after every movement
                cmd = response['direction']
                if cmd == 'W': #from android
                    commsList[APPLET].write('W10') #just change the movement here only
                    commsList[ANDROID].write('{"status":"moving forward"}')
                    #change the coordinates accordingly
                elif cmd == 'S':
                    commsList[APPLET].write('S10')
                    commsList[ANDROID].write('{"status":"moving back"}')
                elif cmd == 'D':
                    commsList[APPLET].write('D90')
                    commsList[ANDROID].write('{"status":"turning right"}')
                elif cmd == 'A':
                    commsList[APPLET].write('A90')
                    commsList[ANDROID].write('{"status":"turning left"}')
                else:
                    commsList[APPLET].write(str(response['direction']))
                    commsList[ANDROID].write('{"command": ' + str(response['direction']) + '}')
                received = False
                print('waiting for ack')

            elif command == 'auto': #start button pressed from Android
                print('Android start button pressed')
                if response['mode'] == 'racecar':
                    dist = sensor_value - 50
                    direction = 'W' + str(dist)
                    msgQueue.put({"command": "move", "direction": direction})
                    lastcommand = {"command": "move", "direction": direction}
            
            elif command == 'retransmit': #timeout from STM
                msgQueue.put(lastcommand)


    except Exception as e:
        print(traceback.format_exc())

    finally:
        commsList[ANDROID].disconnect()
        commsList[APPLET].disconnect()
        sys.exit(0)
