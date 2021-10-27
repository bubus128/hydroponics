import RPi.GPIO as GPIO
import time


class PeristalticPump:
    def __init__(self, pin):
        self.pin = pin
        self.fertilizer_ml_per_second = 1.83
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.HIGH)

    def dosing(self, dose):
        delay = dose/self.fertilizer_ml_per_second
        GPIO.output(self.pin, GPIO.LOW)
        time.sleep(delay)
        GPIO.output(self.pin, GPIO.HIGH)
