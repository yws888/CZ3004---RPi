import serial
import time
import subprocess
import traceback
from time import sleep

class STMComm(object):

    #Initialize the items required for STM Comms
    #can check baud rate and communication port!
    def __init__(self):
        self.commPort = subprocess.check_output('ls /dev/ttyUSB*',shell=True).decode('utf-8').strip('\n')
        self.isEstablished = False
        self.baud = 115200

    #Good to have to check if connected
    def isConnected(self):
        return self.isEstablished

    def connect(self):
        while True:
            retry = False
            try:
                #Let's wait for connection
                print ('[STM_INFO] Initializing Connection with STM')

                self.serialConn = serial.Serial(self.commPort, self.baud, timeout = 1) #timeout was formerly 0.1
                print('[STM_ACCEPTED] Connected to STM.')
                self.isEstablished = True
                retry = False

            except Exception as e:
                print('[STM_ERROR] STM Connection Error: %s' % str(e))
                retry = True

            #When established, break the while(true)
            if (not retry):
                break

            #When not yet established, keep retrying
            print('[STM_INFO] Retrying STM Establishment')
            time.sleep(5)

    #Disconnect when done
    def disconnect(self):
        if not (self.serialConn is None): #if (self.serialConn):
            print('[STM_CLOSE] Shutting down STM Connection')
            self.serialConn.close()
            self.isEstablished = False

    #The fundamental trying to receive
    def read(self):
        try:
            readData = self.serialConn.readline().decode('utf-8')
#             sleep(0.005)
            self.serialConn.flush() #Clean the pipe
            #readData = readData.decode('utf-8')
            if (readData):
                print('[STM_INFO] Received: ' + readData)
                return readData

        except Exception as e:
            print('[STM_ERROR] Receiving Error: %s' % str(e))
            if ('Input/output error' in str(e)):
                self.disconnect()
                print('[STM_INFO] Re-establishing STM Connection.')
                self.connect()

    #The fundamental trying to send
    def write(self, message):
        try:
            #Make sure there is a connection first before sending
            if self.isEstablished:
                message = message + '\r\n'
                self.serialConn.write(str.encode(message))
                print('writing to STM: ' + message)
                return

            #There is no connections. Send what?
            else:
                print('[STM_INVALID] No STM Connections')

        except Exception as e:
            print('[STM_ERROR] Cannot send message to STM: %s' % str(e))