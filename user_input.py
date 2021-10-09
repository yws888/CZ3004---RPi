from datetime import datetime
import subprocess
import serial, os


def STMConnect():
	print('Initializing Connections:')
	ser = serial.Serial(
		port=subprocess.check_output('ls /dev/ttyUSB*',shell=True).decode('utf-8').strip('\n'),
		baudrate=115200,
	)
	print("initialize STMController successful")
	print("Writing command")

	x = "Hi"
	while x != "Bye":
		x = input("Next Command: ")
		if x == "Bye":
			break
		x = x + '\r\n'
		ser.write(str.encode(x))


if __name__ == '__main__':
	print(STMConnect())



