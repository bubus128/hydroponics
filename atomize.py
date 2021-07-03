import RPi.GPIO as GPIO
import time
import sys

'''
if there is no arguments then switch atomizer on/off
if there is one argument (delay) then:
    switch atomizer on
    wait (delay) seconds
    switch atomizer off
'''

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT)
if len(sys.argv)==0:
    if GPIO.input(4):
        GPIO.output(4, GPIO.LOW) #turn atomizer on
    else:
        GPIO.output(4, GPIO.HIGH)  #turn atomizer off
else:
    delay=sys.argv[1]
    GPIO.output(4, GPIO.HIGH) #turn atomizer on
    time.sleep(int(delay)) # wait (delay) seconds
    GPIO.output(4, GPIO.LOW) #turn atomizer back off
