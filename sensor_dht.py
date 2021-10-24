from sensor import Sensor
import time


class SensorDht(Sensor):
    def __init__(self):
        super().__init__()

    def read(self, sensor_type):
        n = 1
        while n < 6:
            from_first_sensor = self.dht_devices[0].locals()[sensor_type]  # podmiana nazwa metody z stringa na metode
            from_second_sensor = self.dht_devices[1].locals()[sensor_type]
            if from_first_sensor is not None and from_second_sensor is not None:
                value = (from_first_sensor + from_second_sensor) / 2
                self.sensors_indications[value] = value
                return value
            time.sleep(1.5)
            n += 1
        else:
            self.logger.logging(sensors_indications=self.sensors_indications,
                                error="Issue with temperature/humidity sensor")
