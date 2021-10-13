from datetime import datetime

import serial, os
from time import sleep
# from get_sim import get_string
from STMComms import STMComm
from AndroidComms import AndroidComm
import subprocess
import sys
from Sensor import sense

from multiprocessing import Process, Queue

def algoProcessingTest():
    algoCommands = []
    algoResponse = []

    count = 0
    for i in algoResponse:
        msgSplit = i['actions'].split('|')  # Try without semi-col                        
        for command in msgSplit:
            if (command):
                algoCommands.append( {"command": "move", "direction": command})
        states = iter(i['discrete_states'])
        next(states)
        for state in states:
            algoCommands[count]["end_state"] = state
            count+=1
        algoCommands.append({"command": "picture", "coordinates": i['block']})
        count+=1
    
    print(algoCommands)

def ImageRec():
    print('Initializing Connections:')
    ser = serial.Serial(
        port='/dev/ttyUSB0',
        baudrate=115200,
    )
    print("initialize STMController successful")
    print("Writing command")

    not_recognized = True
    count = 1
    while not_recognized:
    #     ser.write(str.encode('L90\r\n'))
        ser.write(str.encode('D90\r\n'))
        response = infer()
        if response != []:
            print(response)
            print('iteration: ' + count)
            for i in range(len(response)):
                if response[i]["image_id"] == '0' and response[i]["description"] == 'Obstacle':
                    not_recognized = False

def getCommands():
    response = get_string() #returns a list
    
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

def STMTest():
    
    ser = STMComm()
    ser.connect()
    msgQueue = Queue()
    STMListener = Process(target=listen, args=(msgQueue, ser))
    STMListener.start()

    timeSinceLastCommand = 0
    sense_again = False

#     response = getCommands()
    sensor_value = sense()
    if sensor_value > 60:
        distance = sensor_value - 60
        string = str('W' + str(distance))
        sense_again = True
        response = [string, 'A50', 'W50', 'D118', 'W40','D118', 'W50','A50', 'D25', string]

    
    elif sensor_value <= 60:
        response = ['A45', 'W50', 'D118', 'W40','D118', 'W50','A50', 'D5']
        
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
#                 else:
#                     timeSinceLastCommand += 1
#                     if timeSinceLastCommand > 88:
#                         print('resending command: time - ', timeSinceLastCommand)
#                         ser.write(command)
#                         timeSinceLastCommand = 0
            except:
                sys.exit(0)
                
#         if i == 0:
#             sensor_value = sense()
#             distance = sensor_value - 60
#             string = str('W' + str(distance))
    sys.exit(0)

if __name__ == '__main__':
     STMTest()



