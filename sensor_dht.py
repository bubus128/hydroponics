from sensor import Sensor
import time
import adafruit_dht
import board


class SensorDht(Sensor):
    def __init__(self):
        self.dht_devices = [adafruit_dht.DHT11(board.D17),  adafruit_dht.DHT11(board.D27)]
        super().__init__()

    def readTemperature(self):
        while True:
            try:
                tmp_temperature1 = self.dht_devices[0].temperature
                if tmp_temperature1 is None:
                    continue
                tmp_temperature2 = self.dht_devices[1].temperature
                if tmp_temperature2 is None:
                    continue
                temperature = (tmp_temperature1+tmp_temperature2)/2
                print(f"Temperature: {temperature}")
                return temperature

            except RuntimeError as error:
                print(error.args[0])
                time.sleep(1.5)
                continue

            except Exception as error:
                print(error)
                continue

    def readHumidity(self):
        while True:
            try:
                tmp_humidity1 = self.dht_devices[0].humidity
                if tmp_humidity1 is None:
                    continue
                tmp_humidity2 = self.dht_devices[1].humidity
                if tmp_humidity2 is None:
                    continue
                humidity = (tmp_humidity1+tmp_humidity2)/2
                print(f"Humidity: {humidity} %")
                return humidity

            except RuntimeError as error:
                print(error.args[0])
                time.sleep(1.5)
                continue

            except Exception as error:
                print(error)
                continue

    def read(self):
        return {
            'temperature': self.readTemperature(),
            'humidity': self.readHumidity()
        }
