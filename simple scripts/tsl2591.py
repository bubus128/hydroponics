import time

import board
import adafruit_tsl2591

i2c = board.I2C()
sensor = adafruit_tsl2591.TSL2591(i2c)
adafruit_tsl2591.GAIN_LOW #set gan to low (stron light measuring)
adafruit_tsl2591.INTEGRATIONTIME_100MS

while True:
    try:
        lux = sensor.lux
        print(f"Total light: {lux}lux")
        break

    except RuntimeError as error:
        print(error.args[0])
        time.sleep(1.5)
        continue

    except Exception as error:
        raise error