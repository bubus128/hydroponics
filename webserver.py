from http.server import HTTPServer, BaseHTTPRequestHandler
from LightModule import LightModule
from Logger import Logger
from PhSensor import PhSensor
from sensor_light import SensorLight
from sensor_dht import SensorDht
from TdsSensor import TdsSensor
from Module import Module
import RPi.GPIO as GPIO
import sys
import time
from datetime import datetime
from smbus import SMBus

Dict = {"temperature": "28",
        "humidity": "0",
        "pH_level": "0",
        "tds_level": "0",
        "light": "15",

        "turn_on_heater": "ok",
        "turn_on_cooling": "ok",
        "turn_off_heater": "ok",
        "turn_off_cooling": "ok",
        }


class Hydroponics():
    cooling_pin = 14
    fan_pin = 15
    atomizer_pin = 4
    fertilizer_ml_per_second = 1.83
    loop_delay = 10
    fertilizer_delay = 60
    ph_delay = 120
    exceptions_attempts_count = 10

    lights_list = [0, 5, 6, 11, 13, 19]

    pumps = {
        'ph+': 2,
        'ph-': 1,
        'boost': 3,
        'fertilizer_A': 18,
        'fertilizer_B': 23
    }

    def __init__(self):
        self.logger = Logger()
        self.sensor_light = SensorLight()
        self.sensor_dht = SensorDht()
        self.tds_sensor = TdsSensor()
        self.ph_sensor = PhSensor()
        self.cooling = Module(self.cooling_pin)
        self.fan = Module(self.fan_pin)
        self.atomizer = Module(self.atomizer_pin, on_state='HIGH')
        self.light_module = LightModule(self.lights_list)

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Fertilizer pumps
        GPIO.setup(self.pumps['fertilizer_A'], GPIO.OUT)
        GPIO.setup(self.pumps['fertilizer_B'], GPIO.OUT)
        GPIO.output(self.pumps['fertilizer_A'], GPIO.HIGH)
        GPIO.output(self.pumps['fertilizer_B'], GPIO.HIGH)

        # Relay (unallocated)
        GPIO.setup(9, GPIO.OUT)
        GPIO.setup(10, GPIO.OUT)

        # Off
        GPIO.output(9, GPIO.HIGH)
        GPIO.output(10, GPIO.HIGH)

        # print(self.sensor_dht.readTemperature())
        print(self.ph_sensor.read())


hydroponics = Hydroponics()


class hydroponicsHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('content-typ', 'text/html')
        self.end_headers()
        dividedPath = self.path.split("/")
        if dividedPath[1] == "get":
            if dividedPath[2] == "temperature":
                self.wfile.write(str(hydroponics.sensor_dht.readTemperature()).encode())
            elif dividedPath[2] == "humidity":
                self.wfile.write(str(hydroponics.sensor_dht.readHumidity()).encode())
            elif dividedPath[2] == "ph":
                self.wfile.write(str(hydroponics.ph_sensor.read()).encode())
            elif dividedPath[2] == "tds":
                self.wfile.write(str(hydroponics.tds_sensor.read()).encode())
            elif dividedPath[2] == "light":
                self.wfile.write(str(hydroponics.sensor_light.read()).encode())
        elif dividedPath[1] == "dose":
            if dividedPath[2] == 'ph':  # dose/ph/[SUBSTANCE]/[DOSE]
                substance = dividedPath[3]
                dose = int(dividedPath[4])
                pump = hydroponics.pumps[substance]
                data = [pump, dose]
                hydroponics.bus.write_block_data(hydroponics.arduino_addr, 0, data)
                self.wfile.write("OK".encode())  # TODO
            elif dividedPath[2] == 'fertilizer':
                dose = 1
                delay = dose / hydroponics.fertilizer_ml_per_second
                GPIO.output(hydroponics.pumps['fertilizer_A'], GPIO.LOW)
                GPIO.output(hydroponics.pumps['fertilizer_B'], GPIO.LOW)
                time.sleep(delay)
                GPIO.output(hydroponics.pumps['fertilizer_A'], GPIO.HIGH)
                GPIO.output(hydroponics.pumps['fertilizer_B'], GPIO.HIGH)
                self.wfile.write("OK".encode())  # TODO
        elif dividedPath[1] == 'switch':
            if dividedPath[2] == 'temperature':
                if dividedPath[3] == 'decrease':
                    hydroponics.cooling.switch(True)
                    hydroponics.fan.switch(True)
                    self.wfile.write("OK".encode())  # TODO
                elif dividedPath[3] == 'increase':
                    hydroponics.cooling.switch(False)
                    hydroponics.fan.switch(False)
                    self.wfile.write("OK".encode())  # TODO
            elif dividedPath[2] == 'humidity':
                if dividedPath[3] == 'decrease':
                    hydroponics.fan.switch(True)
                    hydroponics.atomizer.switch(False)
                    self.wfile.write("OK".encode())  # TODO
                elif dividedPath[3] == 'increase':
                    hydroponics.atomizer.switch(True)
                    self.wfile.write("OK".encode())  # TODO


if __name__ == '__main__':
    PORT = 8080
    server = HTTPServer(('', PORT), hydroponicsHandler)
    print('Server running on port %s' % PORT)
    server.serve_forever()