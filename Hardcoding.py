from datetime import datetime

import serial, os
from time import sleep
# from infer import infer
from get_sim import get_string
from STMComms import STMComm
import subprocess
import sys

from multiprocessing import Process, Queue


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
        sleep(0.005)
        msg = com.read()
        msgQueue.put(msg)

def STMTest():
#     print('Initializing Connections:')
#     ser = serial.Serial(
#         port = subprocess.check_output('ls /dev/ttyUSB*',shell=True).decode('utf-8').strip('\n'),
# #         port='/dev/ttyUSB0',
#         baudrate=115200,
#     )
#     print("initialize STMController successful") 
    
    ser = STMComm()
    ser.connect()
    msgQueue = Queue()
    STMListener = Process(target=listen, args=(msgQueue, ser))
    STMListener.start()

    response = getCommands()
#     response = ['W10', 'D17', 'W70', 'A6', 'W20', 'A11', 'W10', 'S40', 'C11', 'S10', 'A6', 'Z6', 'D6', 'Z6', 'D6', 'A6', 'W10', 'A17', 'C11', 'W30', 'A6', 'W50', 'D11', 'W10', 'D6', 'W10', 'D11', 'Z11', 'D6', 'W60', 'A6', 'W10', 'A6', 'W10', 'A17']
    print(response)
#     ser.write('start')
    for command in response:
        #message = command + '\r\n'
        ser.write(command)
        print(command)
        not_received = True
        
        while not_received:
#             readData = ser.readline().strip().decode('utf-8')
            #ser.flush() #Clean the pipe
            #readData = readData.decode('utf-8')
            try:
                msg = msgQueue.get()
                if msg == 'A':
                    not_received = False
                    break
            except:
                sys.exit(0)
    sys.exit(0)

#     sleep(5)
#     ser.write(str.encode('W0\r\n')) #straight
#     sleep(5)
#     message = input('Enter command:')
#     message = message + '\r\n'
#     ser.write(str.encode(message))
#     sleep(5)
#     ser.write(str.encode('W0\r\n')) #straight
#     sleep(5)
# 
#     #take pic to detect face? if no face, then:
if __name__ == '__main__':
    STMTest()
    #getCommands()



