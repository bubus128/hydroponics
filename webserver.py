from http.server import HTTPServer, BaseHTTPRequestHandler


Dict = {"temperature": "28",
        "humidity": "0",
        "pH_level": "0",
        "tds_level": "0",
        "light": "15",

        "turn_on_heater" : "ok",
        "turn_on_cooling" :"ok",
        "turn_off_heater" : "ok",
        "turn_off_cooling" :"ok",
        }

class hydroponicsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('content-typ', 'text/html')
        self.end_headers()
        dividedPath = self.path.split("/")
        if dividedPath[1] == "get":
            if dividedPath[2] == "temperature":
                self.wfile.write(str(15).encode())
            elif dividedPath[2] == "humidity":
                self.wfile.write("maa1a".encode())
            elif dividedPath[2] == "ph":
                self.wfile.write("maa2a".encode())
            elif dividedPath[2] == "tds":
                self.wfile.write("maa3a".encode())
            elif dividedPath[2] == "light":
                self.wfile.write("maa4a".encode())


def initDevices():
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
            
def main():
    PORT = 8000
    server = HTTPServer(('',PORT), hydroponicsHandler)
    #server.initDevices()
    print('Server running on port %s' % PORT)
    server.serve_forever()
        
if __name__ == '__main__':
    main()