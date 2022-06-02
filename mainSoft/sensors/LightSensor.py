from sensors.Sensor import Sensor
import adafruit_tsl2591
import board
import time


class LightSensor(Sensor):
    def __init__(self):
        super().__init__()
        attempts_count = 10
        for i in range(attempts_count):
            try:
                i2c = board.I2C()
                self.tsl2591_sensor = adafruit_tsl2591.TSL2591(i2c)
                self.tsl2591_sensor.gain = adafruit_tsl2591.GAIN_LOW  # Set gain to low (strong light measuring)
                self.tsl2591_sensor.integration_time = adafruit_tsl2591.INTEGRATIONTIME_100MS
            except Exception as e:
                print(e)
                continue
        print("tsl2591 init failed after {} attempts".format(attempts_count))

    def read(self):
        n = 1
        while n < 6:
            lux = self.tsl2591_sensor.lux
            if lux is not None:
                return lux
            n += 1
            time.sleep(1.5)
        else:
            print("Issue with light sensor")
