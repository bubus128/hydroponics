import RPi.GPIO as GPIO
import sys
import time
from datetime import datetime
import adafruit_tsl2591
import adafruit_dht
import board
from smbus import SMBus


class Hydroponics:

    # TODO
    daily_light_cycle={
        'flowering':{
            'OFF':[21,22,23,0,1,2]
        },
        'growth':{
            'OFF':[21,22,23,0,1,2]
        }
    }
    gpi_pins_dict={
        'atomizer':4,
        'cooling':14,
        'fan':15
    }
    pumps={
        'ph_plus':1,
        'ph_minus':2,
        'boost':3,
        'fertilizer_A':4,
        'fertilizer_B':5
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
        'flowering':{
            'ph':{
                'standard':6.1,
                "hysteresis":0.2
                },
            'tds':{
                'standard':1050,
                "hysteresis":200
                },
            'light':{
                'standard':1,
                "hysteresis":1
                },
            'temperature':{
                'standard':25,
                "hysteresis":3
                },
            'humidity':{
                'standard':70,
                "hysteresis":5
                }
            }
    }
    lights_list={0,5,6,11,13,19}
    arduino_addr = 0x7 #arduino nano adress
    bus =SMBus(1)

    def __init__(self):
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

    def dayCycleControl(self):
        current_time=datetime.now().hour
        if current_time in self.daily_light_cycle['OFF']:
            self.lightControl(0)
        else:
            self.lightControl(len(self.lights_list))

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

    def dosing(self, substance, dose):
        pump=self.pumps[substance]
        data=[pump,dose]
        self.bus.write_block_data(self.arduino_addr,0,data)

    def readPH(self):
        self.bus.write_byte(self.arduino_addr,5) # switch to the ph sensor
        return self.bus.read_byte(self.arduino_addr)
    
    def readTDS(self):
        self.bus.write_byte(self.arduino_addr,6) # switch to the tds sensor
        return self.bus.read_byte(self.arduino_addr)

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

    def atomization(self,switch):
        if switch:
            GPIO.output(self.gpi_pins_dict['atomizer'], GPIO.HIGH) #turn atomizer on
        else:
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

    def temperatureControl(self):
        avg_temp=(self.sensors_indications['temperature1']+self.sensors_indications['temperature2'])/2
        if avg_temp>self.indication_limits['flowering']['temperature']['standard']+self.indication_limits['flowering']['temperature']['hysteresis']:
            self.cooling(switch=True)
        else:
            self.cooling(switch=False)

    def humidityControl(self):
        avg_hum=(self.sensors_indications['humidity1']+self.sensors_indications['humidity2'])/2
        if avg_hum<self.indication_limits['flowering']['humidity']['standard']-self.indication_limits['flowering']['humidity']['hysteresis']:
            self.atomization(switch=True)
            self.ventylation(switch=False)
        elif avg_hum>self.indication_limits['flowering']['humidity']['standard']+self.indication_limits['flowering']['humidity']['hysteresis']:
            self.ventylation(switch=True)
            self.atomization(switch=False)
        else :
            self.atomization(switch=False)
            self.ventylation(switch=False)

    def mainLoop(self):
        # 1.Read all sensors indications
        self.readPH()
        self.readTDS()
        self.readLightIntensity()
        self.readTemperature()
        self.readHumidity()
        # 2.Lights control
        self.dayCycleControl()
        # 3.Temperature control
        self.temperatureControl()
        # 4.Humidity control 
        self.humidityControl()
        # 5.Dosing substances
        
if __name__ == "__main__":
    plantation=Hydroponics()
       