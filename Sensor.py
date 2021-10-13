#!/usr/bin/python
import RPi.GPIO as GPIO
import time

def sense():
    distance = -1
    try:
        GPIO.setmode(GPIO.BOARD)

        PIN_TRIGGER = 7
        PIN_ECHO = 11
        pulse_start_time = 0
        pulse_end_time = 0
        GPIO.setup(PIN_TRIGGER, GPIO.OUT)
        GPIO.setup(PIN_ECHO, GPIO.IN)

        GPIO.output(PIN_TRIGGER, GPIO.LOW)

        print("Waiting for sensor to settle")

        time.sleep(0.5)

        print("Calculating distance")
        for _ in range(3):
          GPIO.output(PIN_TRIGGER, GPIO.HIGH)

          time.sleep(0.00003)

          GPIO.output(PIN_TRIGGER, GPIO.LOW)

          while GPIO.input(PIN_ECHO)==0:
                pulse_start_time = time.time()
          while GPIO.input(PIN_ECHO)==1:
                pulse_end_time = time.time()

          pulse_duration = pulse_end_time - pulse_start_time
          distance += pulse_duration * 34500/2
        distance = distance/3

        print("Distance:",distance,"cm")

    finally:
          GPIO.cleanup()
    
    return(int(distance))
          
if __name__ == '__main__':
    sense()
