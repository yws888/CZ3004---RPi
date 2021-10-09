import time
import socket
import requests
import json

class AppletComm(object):

    #Initialize the items required for IP Comms
    def __init__(self):
        self.ipAddress = '192.168.3.20' #IP Address of the RPi
        self.isEstablished = False
        self.portNum = 5000  #36126, 8080 Ephemeral Port, configure on Applet too
        self.client = None
        self.connection = None

    #Good to have to check if connected
    def isConnected(self):
        return self.isEstablished

    def connect(self):
        while True:
            retry = False
            try:
                resp = requests.post("http://192.168.3.20:5000/test_conn")
                if (resp):
                    print('[APPLET_ACCEPTED] Connected to Applet.')
                    self.isEstablished = True
                    retry = False

            except Exception as e:
                print('[APPLET_ERROR] Applet Connection Error: %s' % str(e))
                retry = True

            #When established, break the while(true)
            if (self.isEstablished):
                break

            #When not yet established, keep retrying
            print('[APPLET_INFO] Retrying Applet Connection')
            self.connection.close()
            time.sleep(5)

    #read() not used if Flask server is used
    #The fundamental trying to receive

    def read(self):
        try:
            dataRcvBytes = self.client.recv(2048) #Buffer is 2048 bytes, returned value is byte stream
            dataRcvBytes = dataRcvBytes.decode('utf-8')

            if (dataRcvBytes):
                print('[APPLET_INFO] Received:{} '.format(dataRcvBytes))
                return dataRcvBytes

            else:
                print('[APPLET_ERROR] Null transmission. Attempting to re-establish.')
                self.disconnect()
                self.connect()
                return dataRcvBytes

        except Exception as e:
            pass
            '''
            print('[APPLET_ERROR] Receiving Error: %s' % str(e))

            if ('Broken pipe' in str(e) or 'Connection reset by peer' in str(e)):
                print('[APPLET_ERROR] Communication pipe error. Attempting to re-establish.')
                self.disconnect()
                self.connect()
            '''
    #The fundamental trying to send
#             /test_conn (GET)
    def write(self, message):
        try:
            #Make sure there is a connection first before sending
            if (self.isEstablished):
#                 message = json.loads(message)
                print('writing this to Algo: ' + message)
                #message = json.loads(message)
    
                resp = requests.post("http://192.168.3.20:5000/simulate", json = {'message': message})
                print(resp)
                return resp

            #There is no connections. Send what?
            else:
                print('[APPLET_INVALID] No Socket Connections')

        except Exception as e:
            print('[APPLET_ERROR] Cannot send message: %s' % str(e))
