import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
#lights 
GPIO.setup(11, GPIO.OUT)
GPIO.setup(0, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)
#atomizer
GPIO.setup(4, GPIO.OUT)
#cooling
GPIO.setup(14, GPIO.OUT)
#fan
GPIO.setup(15, GPIO.OUT)
#relay (unlocated)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(10, GPIO.OUT)
GPIO.setup(9, GPIO.OUT)

#all relays off
GPIO.output(0, GPIO.HIGH)
GPIO.output(5, GPIO.HIGH)
GPIO.output(6, GPIO.HIGH)
GPIO.output(9, GPIO.HIGH)
GPIO.output(10, GPIO.HIGH)
GPIO.output(11, GPIO.HIGH)
GPIO.output(13, GPIO.HIGH)
GPIO.output(14, GPIO.HIGH)
GPIO.output(15, GPIO.HIGH)
GPIO.output(18, GPIO.HIGH)
GPIO.output(19, GPIO.HIGH)
GPIO.output(23, GPIO.HIGH)
GPIO.output(4, GPIO.LOW)