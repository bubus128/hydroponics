from modules.Module import Module
import RPi.GPIO as GPIO


class LightModule(Module):
    def __init__(self, pin, on_state='LOW'):
        self.pins = pin
        self.state = False
        self.pin = pin
        if on_state == 'HIGH':
            self.on = GPIO.HIGH
            self.off = GPIO.LOW
        elif on_state == 'LOW':
            self.on = GPIO.LOW
            self.off = GPIO.HIGH
        # Init lights pins
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
        # Switch lights off
        self.switch('OFF')

    def switch(self, state):
        if type(state) == bool:
            state = 'ON' if state else 'OFF'
        for pin in self.pins:
            if state == 'ON':
                GPIO.output(pin, self.on)
                self.state = True
            else:
                GPIO.output(self.pin, self.off)
                self.state = False
