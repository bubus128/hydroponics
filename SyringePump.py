from smbus import SMBus


class SyringePump:
    def __init__(self, number):
        self.arduino_addr = 0x7
        self.bus = SMBus(1)
        self.number = number

    def dosing(self, dose):
        data = [self.number, dose]
        self.bus.write_block_data(self.arduino_addr, 0, data)
