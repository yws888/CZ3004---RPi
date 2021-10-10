from multiprocessing import Process, Queue
from time import sleep

from STMComms import STMComm
from AndroidComms import AndroidComm

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
    commsList[STM].write('W') #the first write to trigger first_ack


    try:
        while running:
            message = msgQueue.get()

            if message is None:
                continue
            elif message == 'A': #receipt from STM
                received = True
                print('ack received')

                if first_ack: #first W write to STM
                    first_ack = False
                elif turning: #turning commands
                    lastcommand = turning_commands.pop(0)
                    msgQueue.put(lastcommand)
                    if len(turning_commands) == 0: #if last turn command, set turning to False
                        turning = False
                        forward = False
                else:
                    #commsList[STM].write('R') or whatever value to get sensor reading
                    msgQueue.put({"command": "move", "direction": 'W'})
                    lastcommand = {"command": "move", "direction": 'W'}

                #note fwd dist is between 50 - 200 cm
                continue

            elif str(message).isdigit() or (str(message).startswith('-') and str(message)[1:].isdigit()): #STM sensor value
                sensor_value = int(message)

                if sensor_value == 20 and forward: #condition to check, indicates when to turn
                    turning = True
                    lastcommand = turning_commands.pop(0)
                    msgQueue.put(lastcommand)
                #     #execute turn sequence by adding commands from list
                elif sensor_value == 10: #condition to check; indicates when to stop (i.e. in carpark). Also when turning back, to rely on count (i.e. no. of times forward just now) or sensor data?
                    msgQueue.close()
                    sys.exit(0)
                else:
                    pass
                continue


            try:
                logfile.write(str(message))
            except Exception as e:
                print('[LOGFILE_ERROR] Logfile Write Error: %s' % str(e))

            if isinstance(message, str) and message != 'A' and (not str(message).isdigit()): #from Android
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
                    #TODO : change this line below accordingly
                    commsList[ANDROID].write('{ "robot": {"x":'+ str(response["end_state"][0]) +',"y":'+str(response["end_state"][1])+', "angle":'+str(-1 * (int(response["end_state"][2]) - 90))+'} }')
                received = False
                print('waiting for ack')

            elif command == 'auto': #start button pressed from Android
                print('mode: ' + response['mode'])
                if response['mode'] == 'racecar':
                    msgQueue.put({"command": "move", "direction": 'W40'})
                    lastcommand = {"command": "move", "direction": 'W40'}



    except Exception as e:
        print(traceback.format_exc())

    finally:
        commsList[STM].disconnect()
        commsList[ANDROID].disconnect()
        logfile.close()
        sys.exit(0)
