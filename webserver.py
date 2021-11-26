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
        self.logger = Logger()
        last_log = self.logger.getLastLog()
        if not last_log:
            print('log file not found')
            self.nextDay()
            self.waterSetup()
        else:
            print('log file found')
            self.day_of_phase = last_log['day_of_phase']
            self.phase = last_log['phase']
        self.fertilizer_pump_a = PeristalticPump(self.fertilizer_a_pump_pin)
        self.fertilizer_pump_b = PeristalticPump(self.fertilizer_b_pump_pin)
        self.ph_plus_pump = SyringePump(self.ph_plus_pump_num)
        self.ph_minus_pump = SyringePump(self.ph_minus_pump_num)
        self.sensors_indications = {
                    "ph": "None",
                    "tds": "None",
                    "light": "None",
                    "temperature": "None",
                    "humidity": "None"
                    }

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
            temperature = hydroponics.sensor_dht.readTemperature()
            self.wfile.write(str(temperature).encode())
            hydroponics.sensors_indications['temperature'] = temperature
        elif divided_path[1] == "humidity":
            humidity = hydroponics.sensor_dht.readHumidity()
            self.wfile.write(str(humidity).encode())
            hydroponics.sensors_indications['humidity'] = humidity
        elif divided_path[1] == "ph":
            ph = hydroponics.ph_sensor.read()
            self.wfile.write(str(ph).encode())
            hydroponics.sensors_indications['ph'] = ph
        elif divided_path[1] == "tds":
            tds = hydroponics.tds_sensor.read()
            self.wfile.write(str(tds).encode())
            hydroponics.sensors_indications['tds'] = tds
        elif divided_path[1] == "light":
            light = hydroponics.sensor_light.read()
            self.wfile.write(str(light).encode())
            hydroponics.sensors_indications['light'] = light

    def do_POST(self):
        self.send_response(200)
        self.send_header('content-typ', 'text/html')
        self.end_headers()
        divided_path = self.path.split("/")
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = post_data.decode('utf-8')
        print(data)

        if divided_path[1] == "takePhoto":
            hydroponics.logger.takePhoto()
            self.wfile.write("OK".encode())  

        elif divided_path[1].startswith("logData"):
            if hydroponics.logger.log['phase'] != data and data != '':
                hydroponics.logger.changePhase(data)
            current_time = datetime.now()
            if hydroponics.logger.getTimer().hour > current_time.hour:
                hydroponics.logger.nextDay()
            hydroponics.logger.logging(sensors_indications=hydroponics.sensors_indications, print_only=False)
            self.wfile.write("OK".encode())  

        elif divided_path[1].startswith("changeDayPhase"):
            if data == 'day':
                hydroponics.logger.day()
            elif data == 'night':
                hydroponics.logger.night()

        elif divided_path[1].startswith("dose"):
            if data == 'ph-':
                hydroponics.ph_minus_pump.dosing(1)
                self.wfile.write("OK".encode())  
            elif data == 'ph+':
                hydroponics.ph_plus_pump.dosing(1)
                self.wfile.write("OK".encode())  
            elif data == 'fertilizer':
                hydroponics.fertilizer_pump_a.dosing(1)
                hydroponics.fertilizer_pump_b.dosing(1)
                self.wfile.write("OK".encode())  

        elif divided_path[1].startswith("temperature"):
            if data == 'decrease':
                hydroponics.cooling.switch(True)
                hydroponics.fan.switch(True)
                self.wfile.write("OK".encode())  
            elif data == 'increase':
                hydroponics.cooling.switch(False)
                hydroponics.fan.switch(False)
                self.wfile.write("OK".encode())  
            elif data == 'remain':
                hydroponics.fan.switch(False)
                self.wfile.write("OK".encode())  

        elif divided_path[1].startswith('humidity'):
            if data == 'decrease':
                hydroponics.fan.switch(True)
                hydroponics.atomizer.switch(False)
                self.wfile.write("OK".encode())  
            elif data == 'increase':
                hydroponics.atomizer.switch(True)
                self.wfile.write("OK".encode())  
            elif data == 'remain':
                hydroponics.atomizer.switch(False)
                self.wfile.write("OK".encode())  

        elif divided_path[1].startswith("light"):
            if data == 'on':
                hydroponics.light_module.switch('ON')
                self.wfile.write("OK".encode())  
            elif data == 'off':
                hydroponics.light_module.switch('OFF')
                self.wfile.write("OK".encode())  


if __name__ == '__main__':
    PORT = 8080
    server = HTTPServer(('', PORT), HydroponicsHandler)
    print('Server running on port %s' % PORT)
    server.serve_forever()
