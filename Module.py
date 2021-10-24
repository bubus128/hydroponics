from Logger import Logger
import adafruit_dht
import RPi.GPIO as GPIO
import board


class Module:
    def __init__(self, pin, on_state='LOW'):
        """
        state: False if module is off and True when it's on
        switch: method to change state of module (on/off)
        """
        self.state = False
        self.pin=pin
        if on_state == 'HIGH':
            self.on=GPIO.HIGH
            self.off=GPIO.LOW
        elif on_state == 'LOW':
            self.on=GPIO.LOW
            self.off=GPIO.HIGH
        # Init GPIO pin
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, self.off)

    def switch(self, state):
        if type(state) == bool:
            state = 'ON' if state else 'OFF'
        if state == 'ON':
            GPIO.output(self.pin, self.on)
            self.state = True
        else:
            GPIO.output(self.pin, self.off)
            self.state = False








