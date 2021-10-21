from Logger import Logger
import adafruit_dht
import board


class Sensor:
    def __init__(self):
        self.modules = {
            'temperature': True,
            'humidity': True,
            'PH': True,
            'TDS': True,
            'water_level': False,
            'lights': True,
            'tsl': True
        }
        self.sensors_indications = {  # should be in json or separate file
            'ph': None,
            'tds': None,
            'light': None,
            'temperature': None,
            'humidity': None
        }

        self.gpi_pins_dict = {
            'atomizer': 4,
            'cooling': 14,
            'fan': 15
        }
        self.logger = Logger()
        self.dht_devices = [adafruit_dht.DHT11(board.D17), adafruit_dht.DHT11(board.D27)]

    def read_value(self, **kwargs):
        pass







