from sensor import Sensor
import time

class PhSensor(Sensor):
    def __init__(self):
        self.arduino_addr = 0x7
        super().__init__()

    def read(self):
        self.bus.write_byte(self.arduino_addr, 5)  # Switch to the ph sensor
        ph_reads = []
        for i in range(20):
            ph_reads.append(self.bus.read_byte(self.arduino_addr)/10)
            time.sleep(0.05)
        ph_reads.sort()
        ph_reads = ph_reads[5:15]
        ph = sum(ph_reads)/len(ph_reads)
        return ph



