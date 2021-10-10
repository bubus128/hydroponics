import RPi.GPIO as GPIO
import json
import time
from datetime import datetime
import adafruit_tsl2591
import adafruit_dht
import board
import glob
import os
from smbus import SMBus


class Hydroponics:
    # TODO
    consts = {
        'fertilizer_ml_per_second': 1.83,
        'loop_delay': 10,
        'fertilizer_delay': 60,
        'ph_delay': 120,
        'exceptions_attempts_count': 10
    }
    log = {
        'timer': None,
        'day': 0,
        'phase': 'Flowering',
        'day_phase': 'day'
    }
    log_file = None
    '''
    True -> module enabled
    False -> module disabled
    '''
    modules = {
        'temperature': True,
        'humidity': True,
        'PH': True,
        'TDS': False,
        'water_level': False,
        'lights': True,
        'tsl': True
    }
    codes = {
        'to_low': 1,
        'to_high': 2,
        'correct': 0
    }
    daily_light_cycle = {
        'flowering': {
            'ON': 6,
            'OFF': 18
        },
        'growth': {
            'ON': 3,
            'OFF': 21
        }
    }
    gpi_pins_dict = {
        'atomizer': 4,
        'cooling': 14,
        'fan': 15
    }
    pumps = {
        'ph+': 1,
        'ph-': 2,
        'boost': 3,
        'fertilizer_A': 18,
        'fertilizer_B': 23
    }
    sensors_indications = {
        'ph': None,
        'tds': None,
        'light': None,
        'temperature': None,
        'humidity': None
    }
    indication_limits = {
        'flowering': {
            'ph': {
                'standard': 6.1,
                'hysteresis': 0.2
            },
            'tds': {
                'standard': 1050,
                'hysteresis': 200
            },
            'light': {
                'standard': 1,
                'hysteresis': 1
            },
            'temperature': {
                'day': {
                    'standard': 26,
                    'hysteresis': 3
                },
                'night': {
                    'standard': 24,
                    'hysteresis': 3
                }
            },
            'humidity': {
                'standard': 70,
                'hysteresis': 5
            }
        }
    }
    lights_list = [0, 5, 6, 11, 13, 19]
    arduino_addr = 0x7  # Arduino nano address
    bus = SMBus(1)

    def __init__(self):
        self.log['timer'] = datetime.now()
        self.nextDay()

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        # Lights 
        for pin in self.lights_list:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)

        # Atomizer
        GPIO.setup(self.gpi_pins_dict['atomizer'], GPIO.OUT)
        GPIO.output(self.gpi_pins_dict['atomizer'], GPIO.LOW)  # Off

        # Cooling
        GPIO.setup(self.gpi_pins_dict['cooling'], GPIO.OUT)
        GPIO.output(self.gpi_pins_dict['cooling'], GPIO.HIGH)  # Off

        # Fan
        GPIO.setup(self.gpi_pins_dict['fan'], GPIO.OUT)
        GPIO.output(self.gpi_pins_dict['fan'], GPIO.HIGH)  # Off

        # Fertilizer pumps 
        GPIO.setup(self.pumps['fertilizer_A'], GPIO.OUT)
        GPIO.setup(self.pumps['fertilizer_B'], GPIO.OUT)
        GPIO.output(self.pumps['fertilizer_A'], GPIO.HIGH)
        GPIO.output(self.pumps['fertilizer_B'], GPIO.HIGH)

        # Relay (unallocated)
        GPIO.setup(9, GPIO.OUT)
        GPIO.setup(10, GPIO.OUT)

        # Off
        GPIO.output(9, GPIO.HIGH)
        GPIO.output(10, GPIO.HIGH)

        # TSL2591 setup
        self.tsl2591Setup()

        # DTH11 setup
        self.dht_devices = [adafruit_dht.DHT11(board.D17), adafruit_dht.DHT11(board.D27)]

        if len(os.listdir('/home/pi/Desktop/logs')) == 0:
            self.waterSetup()
        else:
            list_of_files = glob.glob('/home/pi/Desktop/logs/*')
            latest_file = max(list_of_files, key=os.path.getctime)
            with open(latest_file) as f:
                lines = f.readlines()
            for line in lines:
                if "day" in line:
                    day = lines
                elif "phase" in line:
                    phase = lines
                else:
                    continue

            self.log['day'] = day
            self.log['phase'] = phase

        self.mainLoop()

    def tsl2591Setup(self, attempt=0):
        try:
            i2c = board.I2C()
            self.tsl2591_sensor = adafruit_tsl2591.TSL2591(i2c)
            adafruit_tsl2591.GAIN_LOW  # Set gain to low (stron light measuring)
            adafruit_tsl2591.INTEGRATIONTIME_100MS
        except Exception as e:
            print(e)
            attempt += 1
            if attempt < self.consts['exceptions_attempts_count']:
                self.tsl2591Setup(attempt)
            else:
                self.modules['tsl'] = False

    def nextDay(self):
        self.log['day'] += 1
        self.log_file = '../logs/'
        self.log_file += datetime.now().strftime("%d %b %Y ")
        self.log_file += '.txt'

    def waterSetup(self):
        self.logging(message="filling with water")
        input('pour the water and press ENTER')
        # self.waterFillUp()
        self.logging(message="filling done")
        self.logging(message='setting water ph level')
        while self.phControl() != self.codes['correct']:
            time.sleep(self.consts['ph_delay'])
        self.logging(message='ph level set')
        input("plant strawberries and press ENTER")
        self.logging(message="strawberries planted")

    def dayCycleControl(self):
        current_time = datetime.now()
        if self.log['timer'].hour > current_time.hour:
            self.nextDay()
        self.log['timer'] = current_time
        current_hour = current_time.hour
        if self.daily_light_cycle['flowering']['ON'] <= current_hour < self.daily_light_cycle['flowering']['OFF']:
            self.log['day_phase'] = 'night'
            self.lightControl(0)
        else:
            self.log['day_phase'] = 'day'
            self.lightControl(len(self.lights_list))

    def lightControl(self, lights_number=0):
        # Switch on 'light_number' lights
        for light in range(lights_number):
            GPIO.output(self.lights_list[light], GPIO.LOW)
            # Switch off rest of lights
        for light in range(lights_number, len(self.lights_list)):
            GPIO.output(self.lights_list[light], GPIO.HIGH)

    def readTemperature(self):
        while True:
            try:
                tmp_temperature1 = self.dht_devices[0].temperature
                if tmp_temperature1 is None:
                    continue
                tmp_temperature2 = self.dht_devices[1].temperature
                if tmp_temperature2 is None:
                    continue
                temperature = (tmp_temperature1 + tmp_temperature2) / 2
                print(f"Temperature: {temperature}")
                self.sensors_indications['temperature'] = temperature
                return temperature

            except RuntimeError as error:
                print(error.args[0])
                time.sleep(1.5)
                continue

            except Exception as e:
                self.logging(error=e)
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
                humidity = (tmp_humidity1 + tmp_humidity2) / 2
                print(f"Humidity: {humidity} %")
                self.sensors_indications['humidity'] = humidity
                return humidity

            except RuntimeError as error:
                print(error.args[0])
                time.sleep(1.5)
                continue

            except Exception as error:
                self.logging(error=error)
                continue

    def phControl(self):
        ph = self.readPH()
        self.logging(message="ph={}".format(ph))
        if ph > self.indication_limits['flowering']['ph']['standard'] + \
                self.indication_limits['flowering']['ph']['hysteresis']:
            self.dosing('ph-', 1)
            self.logging(message="dosing ph- (1)")
            return self.codes['to_high']
        elif ph < self.indication_limits['flowering']['ph']['standard'] - \
                self.indication_limits['flowering']['ph']['hysteresis']:
            self.dosing('ph+', 1)
            self.logging(message="dosing ph+ (1)")
            return self.codes['to_low']
        else:
            return self.codes['correct']

    def tdsControl(self):
        tds = self.readTDS()
        self.logging("tds={}".format(tds))
        if tds < self.indication_limits['flowering']['tds']['standard'] - \
                self.indication_limits['flowering']['tds']['hysteresis']:
            self.fertilizerDosing(tds)
            return self.codes['to_low']
        else:
            return self.codes['correct']

    def dosing(self, substance, dose):
        pump = self.pumps[substance]
        data = [pump, dose]
        self.bus.write_block_data(self.arduino_addr, 0, data)

    def fertilizerDoseCalculation(self, tds):
        pass

    def fertilizerDosing(self, tds):
        dose = self.fertilizerDoseCalculation(tds)
        delay = dose / self.consts['fertilizer_ml_per_second']
        self.logging(message="dosing {}ml of fertilizer")
        GPIO.output(self.pumps['fertilizer_A'], GPIO.LOW)
        GPIO.output(self.pumps['fertilizer_B'], GPIO.LOW)
        time.sleep(delay)
        GPIO.output(self.pumps['fertilizer_A'], GPIO.HIGH)
        GPIO.output(self.pumps['fertilizer_B'], GPIO.HIGH)

    def readPH(self):
        self.bus.write_byte(self.arduino_addr, 5)  # switch to the ph sensor
        ph_reads = []
        for i in range(20):
            ph_reads.append(self.bus.read_byte(self.arduino_addr) / 10)
            time.sleep(0.05)
        ph_reads.sort()
        ph_reads = ph_reads[5:15]
        ph = sum(ph_reads) / len(ph_reads)
        self.sensors_indications['ph'] = ph
        return ph

    def readTDS(self):
        tds_reads = []
        for i in range(20):
            self.bus.write_byte(self.arduino_addr, 6)  # switch to the tds sensor
            self.bus.read_byte(self.arduino_addr)
            tds_read = self.bus.read_byte(self.arduino_addr)  # read high half of tds value and shift by 8
            tds_read += self.bus.read_byte(self.arduino_addr) * 2 ** 8  # read and add low half of tds value
            tds_reads.append(tds_read)
            time.sleep(0.05)
        tds_reads.sort()
        tds_reads = tds_reads[5:15]
        tds = sum(tds_reads) / len(tds_reads)
        self.sensors_indications['tds'] = tds
        return tds

    def readLightIntensity(self):
        while True:
            try:
                lux = self.tsl2591_sensor.lux  # Measure light intensity
                self.sensors_indications['light'] = lux  # Write light intensity to the sensors_indications dict
                return lux

            except RuntimeError as error:
                print(error.args[0])
                time.sleep(1.5)
                continue

            except Exception as error:
                self.logging(error=error)
                continue

    def atomization(self, switch):
        if switch:
            GPIO.output(self.gpi_pins_dict['atomizer'], GPIO.HIGH)  # Turn atomizer on
        else:
            GPIO.output(self.gpi_pins_dict['atomizer'], GPIO.LOW)  # Turn atomizer back off

    def ventylation(self, switch=False):
        if switch:
            GPIO.output(self.gpi_pins_dict['fan'], GPIO.LOW)
        else:
            GPIO.output(self.gpi_pins_dict['fan'], GPIO.HIGH)

    def cooling(self, switch=False):
        if switch:
            GPIO.output(self.gpi_pins_dict['cooling'], GPIO.LOW)
        else:
            GPIO.output(self.gpi_pins_dict['cooling'], GPIO.HIGH)

    def temperatureControl(self):
        temperature = self.readTemperature()
        if temperature > self.indication_limits['flowering']['temperature'][self.log['day_phase']]['standard'] + \
                self.indication_limits['flowering']['temperature'][self.log['day_phase']]['hysteresis']:
            self.cooling(switch=True)
            self.ventylation(switch=True)
        elif temperature <= self.indication_limits['flowering']['temperature'][self.log['day_phase']]['standard']:
            self.cooling(switch=False)
            self.ventylation(switch=False)
        else:
            self.ventylation(switch=False)

    def humidityControl(self):
        humidity = self.readHumidity()
        if humidity < self.indication_limits['flowering']['humidity']['standard'] - \
                self.indication_limits['flowering']['humidity']['hysteresis']:
            self.atomization(switch=True)
        elif humidity > self.indication_limits['flowering']['humidity']['standard'] + \
                self.indication_limits['flowering']['humidity']['hysteresis']:
            self.ventylation(switch=True)
            self.atomization(switch=False)
        else:
            self.atomization(switch=False)

    def logging(self, error=None, message=None):
        self.log['timer'] = datetime.now()
        log = self.log
        log['sensors_indications'] = self.sensors_indications
        if message is not None:
            print(message)
            log['message'] = message
        if error is not None:
            print("----------ERROR----------")
            print(error)
            print("----------ERROR----------")
            log['error'] = error
        with open(log['timer'], 'w') as jfile:
            json.dump(log, jfile)

    def logging(self, error=None, message=None):
        try:
            log = open(self.log_file, 'a')
            if message is not None:
                print(message)
                log.write(message)
            else:
                self.log['timer'] = datetime.now()
                if error is None:
                    for key, value in self.log.items():
                        print(key, ' : ', value)
                        log.write('{} : {}\n'.format(key, value))
                    print("sensors indications:")
                    log.write("sensors indications:")
                    for key, value in self.sensors_indications.items():
                        if key == 'ph':
                            value = self.sensors_indications['ph']
                        print(key, ' : ', value)
                        log.write('{} : {}\n'.format(key, value))
                else:
                    print("----------ERROR----------")
                    print(error)
                    print("----------ERROR----------")
                    print(self.log)
                    log.write("----------ERROR----------\n")
                    log.write(error)
                    log.write("----------ERROR----------\n")
                    log.write('\n')
                    for key, value in self.log.items():
                        if key == 'ph':
                            value = self.sensors_indications['ph']
                        print(key, ' : ', value)
                        log.write('{} : {}\n'.format(key, value))
            log.write('\n\n')
            print('\n\n')
        finally:
            log.close()

    def mainLoop(self):
        ph_delay = 0
        fertilizer_delay = 0
        while True:
            if self.modules['temperature']:
                self.temperatureControl()
            if self.modules['humidity']:
                self.humidityControl()
            if self.modules['PH']:
                if ph_delay == 0:
                    if self.phControl() != self.codes['correct']:
                        ph_delay = self.consts['ph_delay']
                else:
                    ph_delay -= self.consts['loop_delay']
                    fertilizer_delay
            if self.modules['TDS']:
                if fertilizer_delay == 0:
                    if self.tdsControl() != self.codes['correct']:
                        fertilizer_delay = self.consts['fertilizer_delay']
                else:
                    fertilizer_delay -= self.consts['loop_delay']
            if self.modules['lights']:
                self.dayCycleControl()
            self.logging()
            time.sleep(self.consts['loop_delay'])


if __name__ == "__main__":
    plantation = Hydroponics()
