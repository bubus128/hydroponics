import RPi.GPIO as GPIO
import time


class Hydroponics:
    
    sensors_indications={
        'ph':None,
        'tds':None,
        'light':None,
        'temperature1':None,
        'temperature2':None,
        'humidity1':None,
        'humidity2':None
    }
    lights_list={0,5,6,11,13,19}

    def setup(self):
        GPIO.setmode(GPIO.BCM)
        # Lights 
        for pin in self.lights_list:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)

        # Atomizer
        GPIO.setup(4, GPIO.OUT)
        GPIO.output(4, GPIO.LOW)

        # Cooling
        GPIO.setup(14, GPIO.OUT)
        GPIO.output(14, GPIO.HIGH) #Off

        # Fan
        GPIO.setup(15, GPIO.OUT)
        GPIO.output(15, GPIO.HIGH) #Off

        # Relay (unlocated)
        GPIO.setup(9, GPIO.OUT)
        GPIO.setup(10, GPIO.OUT)
        GPIO.setup(18, GPIO.OUT)
        GPIO.setup(23, GPIO.OUT)
        # Off
        GPIO.output(9, GPIO.HIGH)
        GPIO.output(10, GPIO.HIGH)
        GPIO.output(18, GPIO.HIGH)
        GPIO.output(23, GPIO.HIGH)        

    def lightControl(self,lights_number=0):
        # Switch on 'light_number' lights
        for light in range(lights_number):
            GPIO.output(self.light_list[light], GPIO.HIGH) 
        # Switch off rest of lights
        for light in range(lights_number,len(self.lights_list)):
            GPIO.output(self.light_list[light], GPIO.LOW)

    
