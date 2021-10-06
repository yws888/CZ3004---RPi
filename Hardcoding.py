from datetime import datetime

import serial, os
from time import sleep
# from infer import infer
from get_sim import get_string
from STMComms import STMComm
from AndroidComms import AndroidComm
import subprocess
import sys

from multiprocessing import Process, Queue

def algoProcessingTest():
    algoCommands = []
    algoResponse = [
  {
    "actions": "A45|C45|C45|C45|C45|Z45|", 
    "block": [
      0, 
      10, 
      0.0
    ], 
    "continuous_states": [
      [
        1.5, 
        1.5, 
        90.0
      ], 
      [
        0.5041630560342618, 
        3.9041630560342617, 
        135.0
      ], 
      [
        2.908326112068523, 
        2.908326112068523, 
        180.0
      ], 
      [
        5.312489168102784, 
        3.904163056034261, 
        -135.0
      ], 
      [
        6.308326112068523, 
        6.308326112068523, 
        -90.0
      ], 
      [
        5.312489168102784, 
        8.712489168102785, 
        -45.0
      ], 
      [
        4.316652224137046, 
        11.116652224137045, 
        -90.0
      ]
    ], 
    "discrete_states": [
      [
        2, 
        2, 
        90.0
      ], 
      [
        1, 
        4, 
        135.0
      ], 
      [
        3, 
        3, 
        180.0
      ], 
      [
        5, 
        4, 
        -135.0
      ], 
      [
        6, 
        6, 
        -90.0
      ], 
      [
        5, 
        9, 
        -45.0
      ], 
      [
        4, 
        11, 
        -90.0
      ]
    ]
  }, 
  {
    "actions": "C45|C45|A45|S10|S10|A45|", 
    "block": [
      6, 
      15, 
      180.0
    ], 
    "continuous_states": [
      [
        4.316652224137046, 
        11.116652224137045, 
        -90.0
      ], 
      [
        3.320815280171308, 
        13.520815280171306, 
        -45.0
      ], 
      [
        0.9166522241370463, 
        14.516652224137044, 
        0.0
      ], 
      [
        3.320815280171308, 
        15.512489168102782, 
        45.0
      ], 
      [
        2.6137084989847605, 
        14.805382386916234, 
        45.0
      ], 
      [
        1.906601717798213, 
        14.098275605729686, 
        45.0
      ], 
      [
        2.9024386617639513, 
        16.502438661763946, 
        90.0
      ]
    ], 
    "discrete_states": [
      [
        4, 
        11, 
        -90.0
      ], 
      [
        3, 
        14, 
        -45.0
      ], 
      [
        1, 
        15, 
        0.0
      ], 
      [
        3, 
        16, 
        45.0
      ], 
      [
        3, 
        15, 
        45.0
      ], 
      [
        2, 
        14, 
        45.0
      ], 
      [
        3, 
        17, 
        90.0
      ]
    ]
  }, 
  {
    "actions": "D45|D45|D45|S10|A45|", 
    "block": [
      10, 
      15, 
      90.0
    ], 
    "continuous_states": [
      [
        2.9024386617639513, 
        16.502438661763946, 
        90.0
      ], 
      [
        3.8982756057296895, 
        18.906601717798207, 
        45.0
      ], 
      [
        6.302438661763951, 
        19.902438661763945, 
        0.0
      ], 
      [
        8.706601717798213, 
        18.906601717798207, 
        -45.0
      ], 
      [
        7.999494936611665, 
        19.613708498984753, 
        -45.0
      ], 
      [
        10.403657992645927, 
        18.617871555019015, 
        0.0
      ]
    ], 
    "discrete_states": [
      [
        3, 
        17, 
        90.0
      ], 
      [
        4, 
        19, 
        45.0
      ], 
      [
        6, 
        20, 
        0.0
      ], 
      [
        9, 
        19, 
        -45.0
      ], 
      [
        8, 
        20, 
        -45.0
      ], 
      [
        10, 
        19, 
        0.0
      ]
    ]
  }, 
  {
    "actions": "D45|D45|A45|D45|A45|C45|C45|Z45|C45|C45|C45|C45|", 
    "block": [
      10, 
      4, 
      -90.0
    ], 
    "continuous_states": [
      [
        10.403657992645927, 
        18.617871555019015, 
        0.0
      ], 
      [
        12.80782104868019, 
        17.622034611053277, 
        -45.0
      ], 
      [
        13.803657992645928, 
        15.217871555019016, 
        -90.0
      ], 
      [
        14.799494936611666, 
        12.813708498984756, 
        -45.0
      ], 
      [
        15.795331880577404, 
        10.409545442950495, 
        -90.0
      ], 
      [
        16.791168824543142, 
        8.005382386916235, 
        -45.0
      ], 
      [
        14.38700576850888, 
        9.001219330881973, 
        0.0
      ], 
      [
        11.982842712474618, 
        8.005382386916235, 
        45.0
      ], 
      [
        9.578679656440356, 
        7.009545442950497, 
        0.0
      ], 
      [
        7.174516600406093, 
        6.013708498984759, 
        45.0
      ], 
      [
        6.178679656440355, 
        3.6095454429504974, 
        90.0
      ], 
      [
        7.174516600406093, 
        1.2053823869162357, 
        135.0
      ], 
      [
        9.578679656440354, 
        0.20954544295049704, 
        180.0
      ]
    ], 
    "discrete_states": [
      [
        10, 
        19, 
        0.0
      ], 
      [
        13, 
        18, 
        -45.0
      ], 
      [
        14, 
        15, 
        -90.0
      ], 
      [
        15, 
        13, 
        -45.0
      ], 
      [
        16, 
        10, 
        -90.0
      ], 
      [
        17, 
        8, 
        -45.0
      ], 
      [
        14, 
        9, 
        0.0
      ], 
      [
        12, 
        8, 
        45.0
      ], 
      [
        10, 
        7, 
        0.0
      ], 
      [
        7, 
        6, 
        45.0
      ], 
      [
        6, 
        4, 
        90.0
      ], 
      [
        7, 
        1, 
        135.0
      ], 
      [
        10, 
        0, 
        180.0
      ]
    ]
  }
]
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
#    algoProcessingTest()
    #getCommands()



