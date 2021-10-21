from sensor import Sensor
import RPi.GPIO as GPIO


class SensorConditions(Sensor):
    def __init__(self):
        super().__init__()

    def on_off(self, sensor_type, switch=False):   # type can be: atomizer, fan, cooling
        if sensor_type == "fan" or "cooling":
            if switch:
                GPIO.output(self.gpi_pins_dict[sensor_type], GPIO.LOW)
            else:
                GPIO.output(self.gpi_pins_dict[sensor_type], GPIO.HIGH)
        elif sensor_type == "atomizer":
            if switch:
                GPIO.output(self.gpi_pins_dict['atomizer'], GPIO.HIGH)  # Turn atomizer on
            else:
                GPIO.output(self.gpi_pins_dict['atomizer'], GPIO.LOW)  # Turn atomizer back off