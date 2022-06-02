import RPi.GPIO as GPIO
import time


class PeristalticPump:
    def __init__(self, pin):
        """Init GPIO pins
        
        Keyword arguments:
        pin -- GPIO pin number to which the pump is connected
        """
        self.pin = pin
        self.fertilizer_ml_per_second = 1.83
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.HIGH)

    def dosing(self, dose):
        """Dose the right amount of liquid

        Keyword arguments:
        dose -- liquid dose in ml of to be dosed
        """
        delay = dose/self.fertilizer_ml_per_second
        GPIO.output(self.pin, GPIO.LOW)
        time.sleep(delay)
        GPIO.output(self.pin, GPIO.HIGH)
