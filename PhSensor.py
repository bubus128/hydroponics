from Sensor import Sensor
import time


class PhSensor(Sensor):
    def __init__(self):
        super().__init__()

    def read(self):
        for i in range(10):
            try:
                self.bus.write_byte(self.arduino_addr, 5)  # Switch to the ph sensor
                ph_reads = []
                for i in range(20):
                    ph_reads.append(self.bus.read_byte(self.arduino_addr)/10)
                    time.sleep(0.05)
                ph_reads.sort()
                ph_reads = ph_reads[5:15]
                ph = sum(ph_reads)/len(ph_reads)
                return ph
            except:
                try:
                    self.bus.read_byte(self.arduino_addr)
                except:
                    time.sleep(0.5)
                    continue
        return -1
