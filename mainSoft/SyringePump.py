from smbus import SMBus


class SyringePump:
    def __init__(self, number):
        """Initialize smbus connection with arduino"""
        self.arduino_addr = 0x7
        self.bus = SMBus(1)
        self.number = number

    def dosing(self, dose):
        """Dose the right amount of liquid

        Keyword arguments:
        dose -- liquid dose in ml of to be dosed
        """
        data = [self.number, dose]
        self.bus.write_block_data(self.arduino_addr, 0, data)
