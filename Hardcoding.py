from datetime import datetime

import serial, os
from time import sleep
# from get_sim import get_string
from STMComms import STMComm
from AndroidComms import AndroidComm
import subprocess
import sys
from Sensor import sense
import json
import traceback

from multiprocessing import Process, Queue

def AndroidConnect():
    android = AndroidComm()
    android.connect()
    queue = Queue()
    AndroidListener = Process(target=listen, args=(queue, android))
    AndroidListener.start()
    sensor_value = sense()
    distance = int(sensor_value - 40)
    while True:
        try:
            msg = queue.get()
            msg = json.loads(msg)
            if msg['command'] == 'obstacle' and msg['mode'] == 'racecar' :
                AndroidListener.terminate()
                return distance
        except:
            print(traceback.format_exc())

def getCommands():
    # response = get_string() #returns a list
    
    commands = []
    
    for obj in response:
        objSplit=obj.split("|")
        for string in objSplit:
            if string != '':
                commands.append(string)
    
    #print(commands)
    return(commands)

def listen(msgQueue, com):
    while True:
        msg = com.read()
        msgQueue.put(msg)

def STMTest(distance):
    
    ser = STMComm()
    ser.connect()
    msgQueue = Queue()
    STMListener = Process(target=listen, args=(msgQueue, ser))
    STMListener.start()

    timeSinceLastCommand = 0
    sense_again = False

#     response = getCommands()
    sensor_value = sense()
    if sensor_value > 80:

        distance = sensor_value - 40
        string = str('W' + str(distance))
        string2 = str('W' + str((distance)))
        sense_again = True
#         response = [string, 'A50', 'W50', 'D118', 'W40','D118', 'W50','A50', 'D20', string] #for lab surface
        response = [string, 'A50', 'W50', 'D120', 'W40','D120', 'W70','A45',  string2] #for outside behind surface
    
    elif sensor_value <= 80:
        #response = ['A50', 'W50', 'D118', 'W40','D118', 'W50','A50', 'D20'] #lab
        response = ['W20', 'A60', 'W45', 'D125', 'W40','D125', 'W45','A60', 'W20'] 

        
#     response = [string, 'A90', 'D90', 'D90', 'W50','D90','D90', 'A90', 'D5', string]
    print(response)
    
    
    for command in response:
        
        ser.write(command)
        print(command)
        not_received = True
        
        while not_received:

            try:
                msg = msgQueue.get()
                if msg == 'A':
                    not_received = False
                    timeSinceLastCommand = 0
                    break
                else:
                    timeSinceLastCommand += 1
                    if timeSinceLastCommand > 58:
                        print('resending command: time - ', timeSinceLastCommand)
                        ser.write(command)
                        timeSinceLastCommand = 0
            except:
                sys.exit(0)

    value = sense()
    distance = int(value - 10)
    final_str = str('W' + str(distance))
    ser.write(final_str)

if __name__ == '__main__':
    distance = AndroidConnect()
    if isinstance(distance, int):
        STMTest(distance)



