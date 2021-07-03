from smbus import SMBus
import time
import sys

'''
there must be 2 arguments
argument 1 = pump number
argument 2 = dose
'''

addr = 0x7 #arduino nano adress
bus =SMBus(1)
if len(sys.argv)==3:
    pump=int(sys.argv[1])
    dose=int(sys.argv[2])
    data=[pump,dose]
    bus.write_block_data(addr,0,data)
