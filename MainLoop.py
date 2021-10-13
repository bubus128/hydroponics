from Logger import Logger
import RPi.GPIO as GPIO
import sys
import time
from datetime import datetime
import adafruit_tsl2591
import adafruit_dht
import board
from smbus import SMBus


class Hydroponics:

    # Consts
    fertilizer_ml_per_second = 1.83
    loop_delay = 10
    fertilizer_delay = 60,
    ph_delay = 120,
    exceptions_attempts_count = 10,
    phase_duration = {
        'flowering': 56,
        'growth': 14
    }
    day_of_phase = 0
    phase = 'growth'
    day_phase = 'day'
    log_file = None
    '''
    True -> module enabled
    False -> module disabled
    '''
    modules = {
        'temperature': True,
        'humidity': True,
        'PH': True,
        'TDS': True,
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
        'ph+': 2,
        'ph-': 1,
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
            'days': 56,
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
            },
        'growth': {
            'days': 14,
            'ph': {
                'standard': 6.1,
                'hysteresis': 0.2
                },
            'tds': {
                'standard': 700,
                'hysteresis': 100
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
        self.logger = Logger()

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
        self.dht_devices = [adafruit_dht.DHT11(board.D17),adafruit_dht.DHT11(board.D27)]

        if not self.logger.getLastLog():
            print('log file not found')
            self.nextDay()
            self.waterSetup()
        else:
            print('log file found')
            
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
            if attempt < self.exceptions_attempts_count:
                self.tsl2591Setup(attempt)
            else:
                self.modules['tsl'] = False

    def changePchase(self):
        self.day_of_phase = 0
        self.phase = 'flowering' if self.phase == 'growth' else 'growth'
        input('change fertilizers to {} phase and press ENTER'.format(self.phase))
        self.logger.changePhase(self.phase)

    def nextDay(self):
        if self.day_of_phase == self.phase_duration:
            self.changePhase()
        self.day_of_phase += 1
        self.logger.nextDay()

    def waterSetup(self):
        self.logger.logging(sensors_indications=self.sensors_indications, message="filling with water")
        input('pour the water and press ENTER')
        # self.waterFillUp()
        self.logger.logging(sensors_indications=self.sensors_indications, message="filling done")
        self.logger.logging(sensors_indications=self.sensors_indications, message='setting water ph level')
        while self.phControl() != self.codes['correct']:
            time.sleep(self.ph_delay)
        self.logger.logging(sensors_indications=self.sensors_indications, message='ph level set')
        input("plant strawberries and press ENTER")
        self.logger.logging(sensors_indications=self.sensors_indications, message="strawberries planted")

    def dayCycleControl(self):
        current_time = datetime.now()
        if self.logger.getTimer().hour > current_time.hour:
            self.nextDay()
        self.logger.updateTime()
        current_hour = current_time.hour
        if self.daily_light_cycle['flowering']['ON'] <= current_hour < self.daily_light_cycle['flowering']['OFF']:
            self.logger.night()
            self.lightControl(0)
        else:
            self.logger.day()
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
                temperature = (tmp_temperature1+tmp_temperature2)/2
                print(f"Temperature: {temperature}")
                self.sensors_indications['temperature'] = temperature
                return temperature

            except RuntimeError as error:
                print(error.args[0])
                time.sleep(1.5)
                continue

            except Exception as error:
                self.logger.logging(sensors_indications=self.sensors_indications, error=error)
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
                self.sensors_indications['humidity'] = humidity
                return humidity

            except RuntimeError as error:
                print(error.args[0])
                time.sleep(1.5)
                continue

            except Exception as error:
                self.logger.logging(sensors_indications=self.sensors_indications, error=error)
                continue

    def phControl(self): 
        ph = self.readPH()
        if ph > self.indication_limits['flowering']['ph']['standard'] +\
                self.indication_limits['flowering']['ph']['hysteresis']:
            self.dosing('ph-', 1)
            self.logger.logging(sensors_indications=self.sensors_indications, message="dosing ph- (1)")
            return self.codes['to_high']
        elif ph < self.indication_limits['flowering']['ph']['standard'] -\
                self.indication_limits['flowering']['ph']['hysteresis']:
            self.dosing('ph+', 1)
            self.logger.logging(sensors_indications=self.sensors_indications, message="dosing ph+ (1)")
            return self.codes['to_low']
        else:
            return self.codes['correct']

    def tdsControl(self):
        tds = self.readTDS()
        if tds < self.indication_limits['flowering']['tds']['standard'] -\
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
        #todo
        pass

    def fertilizerDosing(self,tds):
        dose = 1 #self.fertilizerDoseCalculation(tds)
        delay = dose/self.fertilizer_ml_per_second
        self.logger.logging(sensors_indications=self.sensors_indications, message="dosing {}ml of fertilizer")
        GPIO.output(self.pumps['fertilizer_A'], GPIO.LOW)
        GPIO.output(self.pumps['fertilizer_B'], GPIO.LOW)
        time.sleep(delay)
        GPIO.output(self.pumps['fertilizer_A'], GPIO.HIGH)
        GPIO.output(self.pumps['fertilizer_B'], GPIO.HIGH)

    def readPH(self):
        self.bus.write_byte(self.arduino_addr, 5)  # Switch to the ph sensor
        ph_reads = []
        for i in range(20):
            ph_reads.append(self.bus.read_byte(self.arduino_addr)/10)
            time.sleep(0.05)
        ph_reads.sort()
        ph_reads = ph_reads[5:15]
        ph = sum(ph_reads)/len(ph_reads)
        self.sensors_indications['ph'] = ph
        return ph
    
    def readTDS(self):
        tds_reads = []
        for i in range(20):
            self.bus.write_byte(self.arduino_addr, 6)               # Switch to the tds sensor
            self.bus.read_byte(self.arduino_addr)
            tds_read = self.bus.read_byte(self.arduino_addr)          # Read high half of tds value and shift by 8
            tds_read += self.bus.read_byte(self.arduino_addr)*2**8    # Read and add low half of tds value
            tds_reads.append(tds_read)
            time.sleep(0.05)
        tds_reads.sort()
        tds_reads = tds_reads[5:15]
        tds = sum(tds_reads)/len(tds_reads)
        self.sensors_indications['tds'] = tds
        return tds

    def readLightIntensity(self):
        while True:
            try:
                lux = self.tsl2591_sensor.lux               # Measure light intensity
                self.sensors_indications['light'] = lux     # Write light intensity to the sensors_indications dict
                return lux

            except RuntimeError as error:
                print(error.args[0])
                time.sleep(1.5)
                continue

            except Exception as error:
                self.logger.logging(sensors_indications=self.sensors_indications, error=error)
                continue

    def atomization(self, switch):
        if switch:
            GPIO.output(self.gpi_pins_dict['atomizer'], GPIO.HIGH)  # Turn atomizer on
        else:
            GPIO.output(self.gpi_pins_dict['atomizer'], GPIO.LOW)   # Turn atomizer back off

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
        if temperature > self.indication_limits['flowering']['temperature'][self.logger.getDayPhase()]['standard'] +\
                self.indication_limits['flowering']['temperature'][self.logger.getDayPhase()]['hysteresis']:
            self.cooling(switch=True)
            self.ventylation(switch=True)
        elif temperature <= self.indication_limits['flowering']['temperature'][self.logger.getDayPhase()]['standard']:
            self.cooling(switch=False)
            self.ventylation(switch=False)
        else:
            self.ventylation(switch=False)

    def humidityControl(self):
        humidity = self.readHumidity()
        if humidity < self.indication_limits['flowering']['humidity']['standard'] -\
                self.indication_limits['flowering']['humidity']['hysteresis']:
            self.atomization(switch=True)
        elif humidity > self.indication_limits['flowering']['humidity']['standard'] +\
                self.indication_limits['flowering']['humidity']['hysteresis']:
            self.ventylation(switch=True)
            self.atomization(switch=False)
        else:
            self.atomization(switch=False)

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
                        ph_delay = self.ph_delay
                else:
                    ph_delay -= self.loop_delay
                    fertilizer_delay
            if self.modules['TDS']:
                if fertilizer_delay == 0:
                    if self.tdsControl() != self.codes['correct']:
                        fertilizer_delay = self.fertilizer_delay
                else:
                    fertilizer_delay -= self.loop_delay
            if self.modules['lights']:
                self.dayCycleControl()
            self.logger.logging(sensors_indications=self.sensors_indications)
            time.sleep(self.loop_delay)

        
if __name__ == "__main__":
    plantation = Hydroponics()
