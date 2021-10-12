from multiprocessing import Process, Queue
from time import sleep

from STMComms import STMComm
from AppletComms import AppletComm
from Sensor import sense

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

    commsList = []
    commsList.append(STMComm())

    connect(commsList)

    STM = 0

    msgQueue = Queue()
    STMListener = Process(target=listen, args=(msgQueue, commsList[STM]))

    STMListener.start()

    turning_commands = turning_cmds
    ack_received = True #for STM acknowledgment
    forward = True #True if going forward towards obstacle; False if moving back to carpark
    sensor_value = -1 #default?
    first_ack = True #first write to STM
    turning = False #True if going through turning motion, False otherwise
    lastcommand = None
    firstCmdAfterTurn = False

    commsList[STM].write('W') #the first write to trigger first_ack


    try:
        while True:
            message = msgQueue.get()

            if message is None:
                continue
            elif message == 'A': #receipt from STM
                ack_received = True
                print('ack received')

                if first_ack: #first W write to STM
                    first_ack = False
                    sensor_value = sense()
                    distance = sensor_value - 40
                    string = 'W' + str(distance)
                    msgQueue.put({"command": "move", "direction": string})
                    lastcommand = {"command": "move", "direction": string}
                elif turning: #turning commands
                    lastcommand = turning_commands.pop(0)
                    msgQueue.put(lastcommand)
                    if len(turning_commands) == 0: #if last turn command, set turning to False
                        turning = False
                        forward = False
                        firstCmdAfterTurn = True
                elif firstCmdAfterTurn:
                    firstCmdAfterTurn = False
                    msgQueue.put({"command": "move", "direction": 'W40'})
                    lastcommand = {"command": "move", "direction": 'W40'}

                else:
                    #commsList[STM].write('R') or whatever value to get sensor reading
                    msgQueue.put({"command": "move", "direction": 'W'})
                    lastcommand = {"command": "move", "direction": 'W'}
                #note fwd dist is between 50 - 200 cm
                continue
                #see if can repeat the command if
            elif str(message).isdigit() or (str(message).startswith('-') and str(message)[1:].isdigit()): #STM sensor value
                sensor_value = int(message)

                if 40 <= sensor_value <= 45 and forward: #condition to check, indicates when to turn
                    turning = True
                    lastcommand = turning_commands.pop(0)
                    msgQueue.put(lastcommand)
                #execute turn sequence by adding commands from list
                elif sensor_value <= 15: #condition to check; indicates when to stop (i.e. in carpark). Also when turning back, to rely on count (i.e. no. of times forward just now) or sensor data?
                    msgQueue.close()
                    sys.exit(0)
                continue

            if isinstance(message, str) and message != 'A' and (not str(message).isdigit()): #from Android
                response = json.loads(message)
            else:
                response = message
            command = response["command"]
            
            if command == 'move' and ack_received: #check if STM always sends received after every movement
                cmd = response['direction']
                if cmd == 'W': #from android
                    commsList[STM].write('W10') #just change the movement here only
                    #change the coordinates accordingly
                elif cmd == 'S':
                    commsList[STM].write('S10')
                elif cmd == 'D':
                    commsList[STM].write('D90')
                elif cmd == 'A':
                    commsList[STM].write('A90')
                else:
                    commsList[STM].write(str(response['direction']))

                ack_received = False
                print('waiting for ack')


    except Exception as e:
        print(traceback.format_exc())

    finally:
        commsList[STM].disconnect()
        sys.exit(0)
