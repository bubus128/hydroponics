from Logger import Logger
from smbus import SMBus

class Sensor:
    def __init__(self):
        self.arduino_addr = 0x7
        self.bus = SMBus(1)

    def read(self):
        pass
