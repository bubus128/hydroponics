import time

import adafruit_dht
import board

# Initial the dht device, with data pin connected to pin17
dht_device = adafruit_dht.DHT11(board.D17)

while(True):
    try:
        humidity = dht_device.humidity
        print(f"Humidity: {humidity} %")
        dht_device.exit()
        break

    except RuntimeError as error:
        print(error.args[0])
        time.sleep(1.5)
        continue

    except Exception as error:
        dht_device.exit()
        raise error
