from Logger import Logger
import time

import adafruit_dht
import board
import json
import RPi.GPIO as GPIO

# f = open('data.json')


class Sensor:
    sensors_indications = {
        'ph': None,
        'tds': None,
        'light': None,
        'temperature': None,
        'humidity': None
    }   # this should go to json or separate file

    gpi_pins_dict = {
        'atomizer': 4,
        'cooling': 14,
        'fan': 15
    }   # this should go to json or separate file

    def __init__(self):
        #self.data_json = json.load(f)
        self.logger = Logger()
        self.dht_devices = [adafruit_dht.DHT11(board.D17), adafruit_dht.DHT11(board.D27)]

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

    def light_control(self, lights_list, lights_number=0):
        # Switch on 'light_number' lights
        for light in range(lights_number):
            GPIO.output(lights_list[light], GPIO.LOW)
        # Switch off rest of lights
        for light in range(lights_number, len(lights_list)):
            GPIO.output(lights_list[light], GPIO.HIGH)

    def read_temperature(self):
        n = 1
        while n < 6:
            temp_from_first_sensor = self.dht_devices[0].temperature
            temp_from_second_sensor = self.dht_devices[1].temperature
            n += 1
            if temp_from_first_sensor is not None and temp_from_second_sensor is not None:
                temperature = (temp_from_first_sensor + temp_from_second_sensor) / 2
                self.sensors_indications['temperature'] = temperature
                return temperature
        else:
            self.logger.logging(sensors_indications=self.sensors_indications,
                                error="Issue with temperature sensor")

    def read_humidity(self):
        n = 1
        while n < 6:
            humidity_from_first_sensor = self.dht_devices[0].humidity
            humidity_from_second_sensor = self.dht_devices[1].humidity
            n += 1
            if humidity_from_first_sensor is not None and humidity_from_second_sensor is not None:
                humidity = (humidity_from_first_sensor + humidity_from_second_sensor) / 2
                self.sensors_indications['humidity'] = humidity
                return humidity
        else:
            self.logger.logging(sensors_indications=self.sensors_indications,
                                error="Issue with humidity sensor")





