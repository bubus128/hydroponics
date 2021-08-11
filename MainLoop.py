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
    log={
        'timer':None,
        'day':0,
        'sensors_indications':None,
        'phase':'Flowering',
        'day_phase':'day'
    }
    log_file=None
    '''
    True -> module enabled
    False -> module disabled
    '''
    modules={
        'temperature':True,
        'humidity':True,
        'PH':True,
        'TDS':False,
        'water_level':False,
        'lights':True
    }
    codes={
        'to_low':1,
        'to_high':2,
        'correct':0
    }
    daily_light_cycle={
        'flowering':{
            'OFF':[21,22,23,0,1,2,3,4]
        },
        'growth':{
            'OFF':[21,22,23,0,1,2,3,4]
        }
    }
    gpi_pins_dict={
        'atomizer':4,
        'cooling':14,
        'fan':15
    }
    pumps={
        'ph+':1,
        'ph-':2,
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
                'hysteresis':0.2
                },
            'tds':{
                'standard':1050,
                'hysteresis':200
                },
            'light':{
                'standard':1,
                'hysteresis':1
                },
            'temperature':{
                'day':{
                    'standard':26,
                    'hysteresis':3
                },
                'night':{
                    'standard':24,
                    'hysteresis':3
                }
                },
            'humidity':{
                'standard':70,
                'hysteresis':5
                }
            }
    }
    water_setup_enabled=False
    lights_list=[0,5,6,11,13,19]
    arduino_addr = 0x7 #arduino nano adress
    bus =SMBus(1)

    def __init__(self):
        self.log['timer']=datetime.now()
        self.nextDay()

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
        self.dht_devices = [adafruit_dht.DHT11(board.D17),adafruit_dht.DHT11(board.D27)]

        if self.water_setup_enabled:
            self.waterSetup()
        self.mainLoop()
    
    def nextDay(self):
        self.log['day']+=1
        self.log_file='../logs/'
        self.log_file+=datetime.now().strftime("%d %b %Y ")
        self.log_file+='.txt'

    def waterSetup(self):
        self.logging(message="filling with water")
        print('pour the water')
        self.waterFillUp()
        self.logging(message="filling done")
        self.logging(message='setting water ph level')
        while self.phControl()!=self.codes['correct']:
            time.sleep(30)
        self.logging(message='ph level set')
        input("plant strawberries and press ENTER")
        self.logging(message="strawberries planted")
        
    def waterFillUp(self):
        fill=0
        while fill<100:
            fill=self.readWaterLevel()
            print("water level: {}%".format(fill))
            time.sleep(1)

    def dayCycleControl(self):
        current_time=datetime.now()
        if self.log['timer'].hour>current_time.hour:
            self.nextDay()
        self.log['timer']=current_time
        current_hour=current_time.hour
        if current_hour in self.daily_light_cycle['flowering']['OFF']:
            self.log['day_phase']='night'
            self.lightControl(0)
        else:
            self.log['day_phase']='day'
            self.lightControl(len(self.lights_list))

    def lightControl(self,lights_number=0):
        # Switch on 'light_number' lights
        for light in range(lights_number):
            GPIO.output(self.lights_list[light], GPIO.LOW) 
        # Switch off rest of lights
        for light in range(lights_number,len(self.lights_list)):
            GPIO.output(self.lights_list[light], GPIO.HIGH)

    def readTemperature(self):
        while(True):
            try:
                temperature = 0
                tmp_temperature= self.dht_devices[0].temperature
                if tmp_temperature is None:
                    continue
                temperature+=tmp_temperature
                tmp_temperature= self.dht_devices[1].temperature
                if tmp_temperature is None:
                    continue
                temperature+=tmp_temperature
                temperature/=2
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
                humidity = 0
                tmp_humidity= self.dht_devices[0].humidity
                if tmp_humidity is None:
                    continue
                humidity+=tmp_humidity
                tmp_humidity= self.dht_devices[1].humidity
                if tmp_humidity is None:
                    continue
                humidity+=tmp_humidity
                humidity/=2
                print(f"Humidity: {humidity} %")
                self.sensors_indications['humidity']=humidity
                return humidity

            except RuntimeError as error:
                print(error.args[0])
                time.sleep(1.5)
                continue

            except Exception as error:
                raise error

    def phControl(self):
        self.readPH()
        ph=self.sensors_indications['ph']
        if ph>self.indication_limits['flowering']['ph']['standard']+self.indication_limits['flowering']['ph']['hysteresis']:
            self.dosing(self.pumps['ph-'],1)
            self.logging(message="dosing ph- (1)")
            return self.codes['to_high']
        elif ph<self.indication_limits['flowering']['ph']['standard']-self.indication_limits['flowering']['ph']['hysteresis']:
            self.dosing(self.pumps['ph+'],1)
            self.logging(message="dosing ph+ (1)")
            return self.codes['to_low']
        else:
            return self.codes['correct']

    def tdsControl(self):
        self.readTDS()

    def dosing(self, substance, dose):
        pump=self.pumps[substance]
        data=[pump,dose]
        self.bus.write_block_data(self.arduino_addr,0,data)

    def readPH(self):
        self.bus.write_byte(self.arduino_addr,5) # switch to the ph sensor
        ph=self.bus.read_byte(self.arduino_addr)/10
        self.sensors_indications['ph']=ph
        return ph
    
    def readTDS(self):
        self.bus.write_byte(self.arduino_addr,6) # switch to the tds sensor
        return self.bus.read_byte(self.arduino_addr)/10

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
        temperature=self.readTemperature()
        #avg_temp=(self.sensors_indications['temperature1']+self.sensors_indications['temperature2'])/2
        if temperature>self.indication_limits['flowering']['temperature'][self.log['day_phase']]['standard']+self.indication_limits['flowering']['temperature'][self.log['day_phase']]['hysteresis']:
            self.cooling(switch=True)
            self.ventylation(switch=True)
        elif temperature<=self.indication_limits['flowering']['temperature'][self.log['day_phase']]['standard']:
            self.cooling(switch=False)
            self.ventylation(switch=False)
        else:
            self.ventylation(switch=False)

    def humidityControl(self):
        humidity=self.readHumidity()
        #avg_hum=(self.sensors_indications['humidity1']+self.sensors_indications['humidity2'])/2
        if humidity<self.indication_limits['flowering']['humidity']['standard']-self.indication_limits['flowering']['humidity']['hysteresis']:
            self.atomization(switch=True)
            #self.ventylation(switch=False)
        elif humidity>self.indication_limits['flowering']['humidity']['standard']+self.indication_limits['flowering']['humidity']['hysteresis']:
            self.ventylation(switch=True)
            self.atomization(switch=False)
        else :
            self.atomization(switch=False)
            #self.ventylation(switch=False)

    def logging(self, error=None, message=None):
        try:
            log=open(self.log_file,'a')
            if message is not None:
                print(message)
                log.write(message)
            else:
                self.log['timer']=datetime.now()
                self.log['sensors_indications']=self.sensors_indications
                if error is None:
                    for key,value in self.log.items():
                        print(key, ' : ', value)
                        log.write('{} : {}\n'.format(key,value))
                else:
                    print("----------ERROR----------")
                    print(error)
                    print(self.log)
                    print("----------ERROR----------")
                    log.write("----------ERROR----------\n")
                    log.write(error)
                    log.write('\n')
                    for key,value in self.log.items():
                        print(key, ' : ', value)
                        log.write('{} : {}\n'.format(key,value))
                    log.write("----------ERROR----------\n")
            log.write('\n\n')
            print('\n\n')
        finally:
            log.close()

    def mainLoop(self):
        while(True):
            if self.modules['temperature']:
                self.temperatureControl()
            if self.modules['humidity']:
                self.humidityControl()
            if self.modules['PH']:
                self.phControl()
            if self.modules['TDS']:
                self.tdsControl()
            if self.modules['lights']:
                self.dayCycleControl()
            self.logging()
            time.sleep(10)

        
if __name__ == "__main__":
    plantation=Hydroponics()
       