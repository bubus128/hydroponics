import RPi.GPIO as GPIO
import sys
import time


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
    lights_list={0,5,6,11,13,19}

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

    def lightControl(self,lights_number=0):
        # Switch on 'light_number' lights
        for light in range(lights_number):
            GPIO.output(self.light_list[light], GPIO.HIGH) 
        # Switch off rest of lights
        for light in range(lights_number,len(self.lights_list)):
            GPIO.output(self.light_list[light], GPIO.LOW)

    def readPH(self):
        # TODO: PH sensor indication read
        pass
    
    def readTDS(self):
        # TODO: TDS sensor indication read
        pass

    def readLightIntensity(self):
        # TODO: Light intesity read (in lux)
        pass

    def atomization(self,delay):
        GPIO.output(self.gpi_pins_dict['atomizer'], GPIO.HIGH) #turn atomizer on
        time.sleep(delay) # wait (delay) seconds
        GPIO.output(self.gpi_pins_dict['atomizer'], GPIO.LOW) #turn atomizer back off

    def ventylation(self):
        # TODO: Ventylation
        pass

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
       pass
        