from multiprocessing import Process, Queue
from time import sleep

from STMComms import STMComm
from AndroidComms import AndroidComm
from Sensor import sense

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
    logfile = open(os.path.join('logs', 'rpi_received_log_' + run_timestamp + '.txt'), 'a+')
    os.system("sudo hciconfig hci0 piscan")

    commsList = []
    commsList.append(STMComm())
    commsList.append(AndroidComm())

    connect(commsList)

    STM = 0
    ANDROID = 1

    msgQueue = Queue()
    STMListener = Process(target=listen, args=(msgQueue, commsList[STM]))
    androidListener = Process(target=listen, args=(msgQueue, commsList[ANDROID]))

    STMListener.start()
    androidListener.start()

    turning_commands = turning_cmds
    received = True #for STM acknowledgment
    running = True
    forward = True #True if going towards obstacle; False if moving towards carpark
    sensor_value = -1 #default?
    first_ack = True #first write to STM
    turning = False #True if going through turning motion, False otherwise
    lastcommand = None
    firstCmdAfterTurn = False
    commsList[STM].write('W') #the first write to trigger first_ack
    timeSinceLastAck = 0


    try:
        while running:
            message = msgQueue.get()

            if message is None:
                if not received:
                    timeSinceLastAck += 1
                if timeSinceLastAck > 18:
                    print('resending command')
                    msgQueue.put(lastcommand)
                    timeSinceLastAck = 0
                continue
            elif message == 'A': #receipt from STM
                received = True
                timeSinceLastAck = 0
                print('ack received')

                if first_ack: #first W write to STM
                    first_ack = False
                elif forward:
                    turning = True
                    forward = False
                    lastcommand = turning_commands.pop(0)
                    msgQueue.put(lastcommand)
                elif turning: #turning commands
                    lastcommand = turning_commands.pop(0)
                    msgQueue.put(lastcommand)
                    if len(turning_commands) == 0: #if last turn command, set turning to False
                        turning = False
                elif firstCmdAfterTurn:
                    firstCmdAfterTurn = False
                    sensor_value = sense()
                    distance = (sensor_value - 50)
                    if distance <= 0:
                        direction = 'W1'
                    else:
                        direction = 'W' + distance
                    msgQueue.put({"command": "move", "direction": distance})
                    lastcommand = {"command": "move", "direction": distance}
                #note fwd dist is between 50 - 200 cm
                continue

            # if sensor_value == 20 and forward: #condition to check, indicates when to turn

                #     #execute turn sequence by adding commands from list
                # elif sensor_value == 10: #condition to check; indicates when to stop (i.e. in carpark). Also when turning back, to rely on count (i.e. no. of times forward just now) or sensor data?
                #     msgQueue.close()
                #     sys.exit(0)

            try:
                logfile.write(str(message))
            except Exception as e:
                print('[LOGFILE_ERROR] Logfile Write Error: %s' % str(e))

            if isinstance(message, str) and message != 'A': #from Android
                response = json.loads(message)
            else:
                response = message
            command = response["command"]
            
            if command == 'move' and received: #check if STM always sends received after every movement
                cmd = response['direction']
                if cmd == 'W': #from android
                    commsList[STM].write('W10') #just change the movement here only
                    commsList[ANDROID].write('{"status":"moving forward"}')
                    #change the coordinates accordingly
                elif cmd == 'D':
                    commsList[STM].write('D90')
                    commsList[ANDROID].write('{"status":"turning right"}')
                elif cmd == 'A':
                    commsList[STM].write('A90')
                    commsList[ANDROID].write('{"status":"turning left"}')
                else:
                    commsList[STM].write(str(response['direction']))
                    commsList[ANDROID].write('{"status":' + str(response['direction']) + '}')
                received = False
                print('waiting for ack')

            elif command == 'auto': #start button pressed from Android
                print('mode: ' + response['mode'])
                if response['mode'] == 'racecar':
                    sensor_value = sense()
                    distance = (sensor_value - 50)
                    if distance <= 0:
                        direction = 'W1'
                    else:
                        direction = 'W' + distance
                    msgQueue.put({"command": "move", "direction": distance})
                    lastcommand = {"command": "move", "direction": distance}



    except Exception as e:
        print(traceback.format_exc())

    finally:
        commsList[STM].disconnect()
        commsList[ANDROID].disconnect()
        logfile.close()
        sys.exit(0)
