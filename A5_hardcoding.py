from datetime import datetime

import serial, os
from time import sleep
# from multiprocessing import Process, Value, Queue, Manager
from infer import infer 

def STMConnect():
#     print('Initializing Connections:')
#     ser = serial.Serial(
#         port='/dev/ttyUSB0',
#         baudrate=115200,
#     )
#     print("initialize STMController successful")
#     print("Writing command")

    # ser.write(str.encode('Test'))
# W - up
# A - left
# S - down
# D - right

#     ser.write(str.encode('S100\r\n')) #straight
#     ser.write(str.encode('W100\r\n')) #straight
#     sleep(5)
#     ser.write(str.encode('W0\r\n')) #straight
#     sleep(5)
   
    #take pic to detect face? if no face, then:

#     ser.write(str.encode('L90\r\n'))
    for _ in range (4):
#         ser.write(str.encode('D90\r\n'))
        response = infer()
        if response != []:
            print(response)
            print('iteration: ' + str(_))
            for i in range(len(response)):
                if response[i]["image_id"] == '0' and response[i]["description"] == 'Obstacle':
                    return ('Done')
#         sleep(5)
    
#     sleep(5)
#     ser.write(str.encode('W0\r\n')) #straight
#     sleep(5)
#     message = input('Enter command:')
#     message = message + '\r\n'
#     ser.write(str.encode(message))
#     sleep(5)
#     ser.write(str.encode('W0\r\n')) #straight
#     sleep(5)

#     sleep(5)
#     ser.write(str.encode('D90\r\n'))
#     infer()
#     sleep(5)
# #     sleep(5)
#     # ser.write(str.encode('S5\r\n'))
#     # sleep(10)
# 
#     #take pic to detect face? if no face, then:
# 
# #     ser.write(str.encode('R90\r\n')) #right turn
#     ser.write(str.encode('D90\r\n'))
#     infer()
#     sleep(5)
    #take pic to detect face? if no face, then:

    #ser.write(str.encode('L180\r\n')) #right turn
#     ser.write(str.encode('D90\r\n'))
    # ser.write(b'Test')

if __name__ == '__main__':
    print(STMConnect())



