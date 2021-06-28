import time

import board
import adafruit_tsl2591

i2c = board.I2C()
sensor = adafruit_tsl2591.TSL2591(i2c)

while True:
    try:
        lux = sensor.lux
        print(f"Total light: {lux}lux")

    except RuntimeError as error:
        print(error.args[0])
        time.sleep(1.5)
        continue

    except Exception as error:
        sensor.exit()
        raise error

    time.sleep(2.0)
