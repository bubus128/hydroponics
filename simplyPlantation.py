from mainSoft.Hydroponics import Hydroponics
import time

if __name__ == "__main__":
    plantation = Hydroponics()
    while True:
        try:
            plantation.grow()
        except Exception as e:
            plantation.logger.logging(sensors_indications=None, error=e)
