from sensor import Sensor
import RPi.GPIO as GPIO
import adafruit_tsl2591
import board
import time


class SensorLight(Sensor):
    def __init__(self):
        super().__init__()

    def tsl2591_setup(self, attempt=0):
        exceptions_attempts_count = 10
        try:
            i2c = board.I2C()
            self.tsl2591_sensor = adafruit_tsl2591.TSL2591(i2c)    # can it be on init Sensor class?
            adafruit_tsl2591.GAIN_LOW  # Set gain to low (strong light measuring)
            adafruit_tsl2591.INTEGRATIONTIME_100MS
        except Exception as e:
            print(e)
            attempt += 1
            if attempt < exceptions_attempts_count:
                self.tsl2591_setup(attempt)
            else:
                self.modules['tsl'] = False

    def read_value(self):
        n = 1
        while n < 6:
            lux = self.tsl2591_setup.lux
            if lux is not None:
                self.sensors_indications['light'] = lux
                return lux
            n += 1
            time.sleep(1.5)
        else:
            self.logger.logging(sensors_indications=self.sensors_indications,
                                error="Issue with light sensor")

    def on_off(self, lights_list, lights_number=0):
        # Switch on 'light_number' lights
        for light in range(lights_number):
            GPIO.output(lights_list[light], GPIO.LOW)
        # Switch off rest of lights
        for light in range(lights_number, len(lights_list)):
            GPIO.output(lights_list[light], GPIO.HIGH)


