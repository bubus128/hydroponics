from os import error
from LightModule import LightModule
from Logger import Logger
from PeristalticPump import PeristalticPump
from PhSensor import PhSensor
from SyringePump import SyringePump
from LightSensor import LightSensor
from DhtSensor import DhtSensor
from TdsSensor import TdsSensor
from Module import Module
import RPi.GPIO as GPIO
import time
import glob
import os
import json
from datetime import datetime


class Hydroponics:
    # Consts
    cooling_pin = 14
    fan_pin = 15
    atomizer_pin = 4
    loop_delay = 10
    fertilizer_delay = 60
    ph_delay = 120
    exceptions_attempts_count = 10
    ph_plus_pump_num = 2
    ph_minus_pump_num = 1
    booster_pump_num = 3
    fertilizer_a_pump_pin = 18
    fertilizer_b_pump_pin = 23
    day_of_phase = 0
    phase = 'resting'
    day_phase = 'day'
    log_file = None
    lights_list = [0, 5, 6, 11, 13, 19]
    arduino_addr = 0x7  # Arduino nano address
    fertilizer_dosing = False

    def __init__(self):
        self.readDataFromJsons()
        self.logger = Logger()
        self.sensor_light = LightSensor()
        self.sensor_dht = DhtSensor()
        self.tds_sensor = TdsSensor()
        self.ph_sensor = PhSensor()
        self.cooling = Module(self.cooling_pin)
        self.fan = Module(self.fan_pin)
        self.atomizer = Module(self.atomizer_pin, on_state='HIGH')
        self.light_module = LightModule(self.lights_list)
        self.fertilizer_pump_a = PeristalticPump(self.fertilizer_a_pump_pin)
        self.fertilizer_pump_b = PeristalticPump(self.fertilizer_b_pump_pin)
        self.ph_plus_pump = SyringePump(self.ph_plus_pump_num)
        self.ph_minus_pump = SyringePump(self.ph_minus_pump_num)

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Relay (unallocated)
        GPIO.setup(9, GPIO.OUT)
        GPIO.setup(10, GPIO.OUT)

        # Off
        GPIO.output(9, GPIO.HIGH)
        GPIO.output(10, GPIO.HIGH)

        last_log = self.logger.getLastLog()
        if not last_log:
            print('log file not found')
            self.nextDay()
            self.waterSetup()
        else:
            print('log file found')
            self.day_of_phase = last_log['day_of_phase']
            self.phase = last_log['phase']

        while True:
            try:
                self.mainLoop()
            except Exception as e:
                self.logger.logging(sensors_indications=None, error=e)

    def changePhase(self):
        phases_list = list(self.indication_limits.keys())
        phase_num = phases_list.index(self.phase)
        phase_num = (phase_num + 1) % len(phases_list)
        self.day_of_phase = 1
        self.phase = phases_list[phase_num]
        #self.phase = 'flowering' if self.phase == 'growth' else 'growth'
        input('change fertilizers to {} phase and press ENTER'.format(self.phase))
        self.logger.changePhase(self.phase)

    def readDataFromJsons(self):
        list_of_files = glob.glob('./data-files/*.json')
        for path in list_of_files:
            with open(path) as file:
                tmp_dict = dict(json.load(file))
                for key, value in tmp_dict.items():
                    if value == "None":
                        value = None
                name = os.path.splitext(os.path.basename(path))[0]
                setattr(self, name, tmp_dict)

    def nextDay(self):
        if self.day_of_phase >= self.phase_duration[self.phase]:
            self.changePhase()
        else:
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
        if self.logger.getTimer().minute < current_time.minute:
            self.logger.logging(sensors_indications=self.sensors_indications)
        if self.logger.getTimer().hour > current_time.hour:
            self.nextDay()
        elif self.logger.getTimer().hour < current_time.hour:
            self.logger.takePhoto()
        self.logger.updateTime()
        current_hour = current_time.hour
        if self.daily_light_cycle[self.phase]['ON'] <= current_hour < self.daily_light_cycle[self.phase]['OFF']:
            self.logger.day()
            self.light_module.switch('ON')
        else:
            self.logger.night()
            self.light_module.switch('OFF')

    def phControl(self):
        ph = self.ph_sensor.read()
        if ph == -1:
            return self.codes['correct']
        self.sensors_indications['ph'] = ph
        if ph > self.indication_limits[self.phase]['ph']['standard'] + \
                self.indication_limits[self.phase]['ph']['hysteresis']:
            self.ph_minus_pump.dosing(1)
            self.logger.logging(sensors_indications=self.sensors_indications, message="dosing ph- (1)")
            return self.codes['to_high']
        elif ph < self.indication_limits[self.phase]['ph']['standard'] - \
                self.indication_limits[self.phase]['ph']['hysteresis']:
            self.ph_plus_pump.dosing(1)
            self.logger.logging(sensors_indications=self.sensors_indications, message="dosing ph+ (1)")
            return self.codes['to_low']
        else:
            return self.codes['correct']

    def tdsControl(self):
        tds = self.tds_sensor.read()
        if tds == -1:
            return self.codes['correct']
        self.sensors_indications['tds'] = tds
        tds_limit = self.indication_limits[self.phase]['tds']['standard'] if self.fertilizer_dosing else self.indication_limits[self.phase]['tds']['standard'] - self.indication_limits[self.phase]['tds']['hysteresis']
        if tds < tds_limit:
            self.fertilizer_dosing = True
            dose = 1
            self.fertilizer_pump_a.dosing(dose)
            self.fertilizer_pump_b.dosing(dose)
            self.logger.logging(sensors_indications=self.sensors_indications,
                                message="dosing {}ml of fertilizer".format(dose))
            return self.codes['to_low']
        else:
            self.fertilizer_dosing = False
            return self.codes['correct']

    def temperatureControl(self):
        temperature = self.sensor_dht.readTemperature()
        self.sensors_indications['temperature'] = temperature
        if temperature > self.indication_limits[self.phase]['temperature'][self.logger.getDayPhase()]['standard'] + \
                self.indication_limits[self.phase]['temperature'][self.logger.getDayPhase()]['hysteresis']:
            self.cooling.switch(True)
            self.fan.switch(True)
        elif temperature <= self.indication_limits[self.phase]['temperature'][self.logger.getDayPhase()]['standard']:
            self.cooling.switch(False)
            self.fan.switch(False)
        else:
            self.cooling.switch(True)

    def humidityControl(self):
        humidity = self.sensor_dht.readHumidity()
        self.sensors_indications['humidity'] = humidity
        if humidity < self.indication_limits[self.phase]['humidity']['standard'] - \
                self.indication_limits[self.phase]['humidity']['hysteresis']:
            self.atomizer.switch(True)
        elif humidity > self.indication_limits[self.phase]['humidity']['standard'] + \
                self.indication_limits[self.phase]['humidity']['hysteresis']:
            self.fan.switch(True)
            self.atomizer.switch(False)
        else:
            self.atomizer.switch(False)

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
            if self.modules['TDS']:
                if fertilizer_delay == 0:
                    if self.tdsControl() != self.codes['correct']:
                        fertilizer_delay = self.fertilizer_delay
                else:
                    fertilizer_delay -= self.loop_delay
            if self.modules['lights']:
                self.dayCycleControl()
            self.logger.logging(sensors_indications=self.sensors_indications, print_only=True)
            time.sleep(self.loop_delay)


if __name__ == "__main__":
    plantation = Hydroponics()
