from smbus import SMBus
import time

addr = 0x7 #arduino nano adress
bus =SMBus(1)

tds=bus.read_byte(addr)
print(tds)
bus.write_byte(addr,5)
time.sleep(1)
ph=bus.read_byte(addr)
print(ph)