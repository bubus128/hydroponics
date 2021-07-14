import RPi.GPIO as GPIO
import sys
import time
import adafruit_tsl2591
import adafruit_dht
import board
from smbus import SMBus


class Hydroponics:

    # TODO
    daily_light_cycle=None
    gpi_pins_dict={
        'atomizer':4,
        'cooling':14,
        'fan':15
    }
    sensors_indications={
        'ph':None,
        'tds':None,
        'light':None,
        'temperature1':None,
        'temperature2':None,
        'humidity1':None,
        'humidity2':None
    }
    indication_limits={
        'ph':{
            'standard':1,
            "hysteresis":1
            },
        'tds':{
            'standard':1,
            "hysteresis":1
            },
        'light':{
            'standard':1,
            "hysteresis":1
            },
        'temperature':{
            'standard':1,
            "hysteresis":1
            },
        'humidity':{
            'standard':1,
            "hysteresis":1
            },
    }
    lights_list={0,5,6,11,13,19}
    addr = 0x7 #arduino nano adress
    bus =SMBus(1)

    def setup(self):
        GPIO.setmode(GPIO.BCM)
        # Lights 
        for pin in self.lights_list:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)

        # Atomizer
        GPIO.setup(self.gpi_pins_dict['atomizer'], GPIO.OUT)
        GPIO.output(self.gpi_pins_dict['atomizer'], GPIO.LOW) #Off

        # Cooling
        GPIO.setup(self.gpi_pins_dict['cooling'], GPIO.OUT)
        GPIO.output(self.gpi_pins_dict['cooling'], GPIO.HIGH) #Off

        # Fan
        GPIO.setup(self.gpi_pins_dict['fan'], GPIO.OUT)
        GPIO.output(self.gpi_pins_dict['fan'], GPIO.HIGH) #Off

        # Relay (unlocated)
        GPIO.setup(9, GPIO.OUT)
        GPIO.setup(10, GPIO.OUT)
        GPIO.setup(18, GPIO.OUT)
        GPIO.setup(23, GPIO.OUT)
        # Off
        GPIO.output(9, GPIO.HIGH)
        GPIO.output(10, GPIO.HIGH)
        GPIO.output(18, GPIO.HIGH)
        GPIO.output(23, GPIO.HIGH)  

        # TSL2591 setup
        i2c = board.I2C()
        self.tsl2591_sensor = adafruit_tsl2591.TSL2591(i2c)
        adafruit_tsl2591.GAIN_LOW #set gan to low (stron light measuring)
        adafruit_tsl2591.INTEGRATIONTIME_100MS      
        
        # DTH11 setup
        self.dht_device = adafruit_dht.DHT11(board.D17)

    def lightControl(self,lights_number=0):
        # Switch on 'light_number' lights
        for light in range(lights_number):
            GPIO.output(self.light_list[light], GPIO.HIGH) 
        # Switch off rest of lights
        for light in range(lights_number,len(self.lights_list)):
            GPIO.output(self.light_list[light], GPIO.LOW)

    def readTemperature(self):
        while(True):
            try:
                temperature = self.dht_device.temperature
                print(f"Temperature: {temperature}")
                self.sensors_indications['temperature']=temperature
                return temperature

            except RuntimeError as error:
                print(error.args[0])
                time.sleep(1.5)
                continue

            except Exception as error:
                raise error

    def readHumidity(self):
        while(True):
            try:
                humidity = self.dht_device.humidity
                print(f"Humidity: {humidity} %")
                return humidity

            except RuntimeError as error:
                print(error.args[0])
                time.sleep(1.5)
                continue

            except Exception as error:
                raise error

    def readPH(self):
        self.bus.write_byte(self.addr,5) # switch to the ph sensor
        return self.bus.read_byte(self.addr)
    
    def readTDS(self):
        self.bus.write_byte(self.addr,6) # switch to the tds sensor
        return self.bus.read_byte(self.addr)

    def readLightIntensity(self):
        while True:
            try:
                lux = self.tsl2591_sensor.lux           # Mesasure light intensity
                self.sensors_indications['light']=lux   # Write light intensity to the sensors_indications dict
                return lux

            except RuntimeError as error:
                print(error.args[0])
                time.sleep(1.5)
                continue

            except Exception as error:
                raise error

    def atomization(self,delay):
        GPIO.output(self.gpi_pins_dict['atomizer'], GPIO.HIGH) #turn atomizer on
        time.sleep(delay) # wait (delay) seconds
        GPIO.output(self.gpi_pins_dict['atomizer'], GPIO.LOW) #turn atomizer back off

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

    def mainLoop(self):
       '''
       TODO:
       1.Read all sensors indications
       2.Lights control
        -set lights based on daily light cycle
       3.Temperature control 
        -switch on/off cooling
       4.Humidity control 
        -switch on/off atomization
        -switch on/off ventilation
       5.Substances dosing
       6.Make a photo
       '''
       self.readPH()
       self.readTDS()
       self.readLightIntensity()
       self.readTemperature()
       self.readHumidity()
       pass
        