import time

import adafruit_dht
import board

# Initial the dht device, with data pin connected to pin17
dht_device = adafruit_dht.DHT11(board.D17)
humidity = dht_device.humidity

while True:
    try:
        temperature = dht_device.temperature
        print(f"Temperature: {temperature}")

    except RuntimeError as error:
        print(error.args[0])
        time.sleep(1.0)
        continue

    except Exception as error:
        dht_device.exit()
        raise error

    time.sleep(2.0)
