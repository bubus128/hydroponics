import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(4, GPIO.OUT)
#GPIO.output(4, GPIO.HIGH) #turn atomizer on
#time.sleep(100)            #delay 10 seconds
GPIO.output(4, GPIO.LOW)  #turn atomizer off
