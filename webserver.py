from http.server import HTTPServer, BaseHTTPRequestHandler
from LightModule import LightModule
from Logger import Logger
from PhSensor import PhSensor
from LightSensor import LightSensor
from DhtSensor import DhtSensor
from TdsSensor import TdsSensor
from PeristalticPump import PeristalticPump
from Module import Module
from SyringePump import SyringePump
import RPi.GPIO as GPIO
from datetime import datetime
from picamera import PiCamera
import time



class Hydroponics:
    cooling_pin = 14
    fan_pin = 15
    atomizer_pin = 4
    fertilizer_ml_per_second = 1.83
    loop_delay = 10
    fertilizer_delay = 60
    ph_delay = 120
    exceptions_attempts_count = 10
    ph_plus_pump_num = 2
    ph_minus_pump_num = 1
    booster_pump_num = 3
    fertilizer_a_pump_pin = 18
    fertilizer_b_pump_pin = 23


    lights_list = [0, 5, 6, 11, 13, 19]


    def __init__(self):
        self.sensor_light = LightSensor()
        self.sensor_dht = DhtSensor()
        self.tds_sensor = TdsSensor()
        self.ph_sensor = PhSensor()
        self.cooling = Module(self.cooling_pin)
        self.fan = Module(self.fan_pin)
        self.atomizer = Module(self.atomizer_pin, on_state='HIGH')
        self.light_module = LightModule(self.lights_list)
        self.camera = PiCamera()
        self.fertilizer_pump_a = PeristalticPump(self.fertilizer_a_pump_pin)
        self.fertilizer_pump_b = PeristalticPump(self.fertilizer_b_pump_pin)
        self.ph_plus_pump = SyringePump(self.ph_plus_pump_num)
        self.ph_minus_pump = SyringePump(self.ph_minus_pump_num)

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)


        # Relay (unallocated)
        GPIO.setup(9, GPIO.OUT)
        GPIO.setup(10, GPIO.OUT)

        # Off
        GPIO.output(9, GPIO.HIGH)
        GPIO.output(10, GPIO.HIGH)



hydroponics = Hydroponics()


class HydroponicsHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('content-typ', 'text/html')
        self.end_headers()
        divided_path = self.path.split("/")
        if divided_path[1] == "temperature":
            self.wfile.write(str(hydroponics.sensor_dht.readTemperature()).encode())
        elif divided_path[1] == "humidity":
            self.wfile.write(str(hydroponics.sensor_dht.readHumidity()).encode())
        elif divided_path[1] == "ph":
            self.wfile.write(str(hydroponics.ph_sensor.read()).encode())
        elif divided_path[1] == "tds":
            self.wfile.write(str(hydroponics.tds_sensor.read()).encode())
        elif divided_path[1] == "light":
            self.wfile.write(str(hydroponics.sensor_light.read()).encode())

    def do_POST(self):
        self.send_response(200)
        self.send_header('content-typ', 'text/html')
        self.end_headers()
        divided_path = self.path.split("/")

        if divided_path[1] == "takePhoto":
            timer = datetime.now().strftime("%m.%d.%Y, %H:%M:%S")
            photo_dir = "../airflow_photos/{}.jpg".format(timer)
            hydroponics.camera.start_preview()
            time.sleep(1)
            hydroponics.camera.capture(photo_dir)
            hydroponics.camera.stop_preview()
            self.wfile.write("OK".encode())  # TODO

        elif divided_path[1] == "dose":
            if divided_path[2] == 'ph-':
                hydroponics.ph_minus_pump.dosing(1)
                self.wfile.write("OK".encode())  # TODO
            if divided_path[2] == 'ph+':
                hydroponics.ph_plus_pump.dosing(1)
                self.wfile.write("OK".encode())  # TODO
            elif divided_path[2] == 'fertilizer':
                hydroponics.fertilizer_pump_a.dosing(1)
                hydroponics.fertilizer_pump_b.dosing(1)
                self.wfile.write("OK".encode())  # TODO

        elif divided_path[1] == 'manage':
            if divided_path[2] == 'temperature':
                if divided_path[3] == 'decrease':
                    hydroponics.cooling.switch(True)
                    hydroponics.fan.switch(True)
                    self.wfile.write("OK".encode())  # TODO
                elif divided_path[3] == 'increase':
                    hydroponics.cooling.switch(False)
                    hydroponics.fan.switch(False)
                    self.wfile.write("OK".encode())  # TODO
                elif divided_path[3] == 'remain':
                    hydroponics.fan.switch(False)
                    self.wfile.write("OK".encode())  # TODO
            elif divided_path[2] == 'humidity':
                if divided_path[3] == 'decrease':
                    hydroponics.fan.switch(True)
                    hydroponics.atomizer.switch(False)
                    self.wfile.write("OK".encode())  # TODO
                elif divided_path[3] == 'increase':
                    hydroponics.atomizer.switch(True)
                    self.wfile.write("OK".encode())  # TODO
                elif divided_path[3] == 'remain':
                    hydroponics.atomizer.switch(False)
                    self.wfile.write("OK".encode())  # TODO

        elif divided_path[1] == "light":
            if divided_path[2] == 'on':
                hydroponics.light_module.switch('ON')
                self.wfile.write("OK".encode())  # TODO
            elif divided_path[2] == 'off':
                hydroponics.light_module.switch('OFF')
                self.wfile.write("OK".encode())  # TODO


if __name__ == '__main__':
    PORT = 8080
    server = HTTPServer(('', PORT), HydroponicsHandler)
    print('Server running on port %s' % PORT)
    server.serve_forever()
