from Sensor import Sensor
import time


class TdsSensor(Sensor):

    def __init__(self):
        self.arduino_addr = 0x7
        super().__init__()

    def read(self):
        for i in range(10):
            try:
                tds_reads = []
                for i in range(20):
                    self.bus.write_byte(self.arduino_addr, 6)           # Switch to the tds sensor
                    self.bus.read_byte(self.arduino_addr)
                    tds_read = self.bus.read_byte(self.arduino_addr)          # Read high half of tds value and shift by 8
                    tds_read += self.bus.read_byte(self.arduino_addr)*2**8    # Read and add low half of tds value
                    tds_reads.append(tds_read)
                    time.sleep(0.05)
                tds_reads.sort()
                tds_reads = tds_reads[5:15]
                tds = sum(tds_reads)/len(tds_reads)
                return tds
            except:
                try:
                    self.bus.read_byte(self.arduino_addr)
                    self.bus.read_byte(self.arduino_addr)
                    self.bus.read_byte(self.arduino_addr)
                except:
                    time.sleep(0.5)
                    continue
        return -1
