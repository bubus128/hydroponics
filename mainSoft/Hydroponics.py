from os import error
from modules.LightModule import LightModule
from Logger import Logger
from PeristalticPump import PeristalticPump
from sensors.PhSensor import PhSensor
from SyringePump import SyringePump
from sensors.LightSensor import LightSensor
from sensors.DhtSensor import DhtSensor
from sensors.TdsSensor import TdsSensor
from modules.Module import Module
import RPi.GPIO as GPIO
import time
import glob
import os
import json
from datetime import datetime


class Hydroponics:
    # Consts
    day_of_phase = 0
    phase = 'resting'
    day_phase = 'day'
    log_file = None
    fertilizer_dosing = False

    def __init__(self):
        '''
        1. Read configuration files
        2. Initialize modules and sensors
        3. Initialize GPIO pins
        4. Read last log file (if exists)
        '''
        self.readconfigsFromJsons()
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

    def changePhase(self):
        """
        1. Reconfigure to the next phase
        2. Wait for fertilizers to change
        """
        phases_list = list(self.indications_limits.keys())
        phase_num = phases_list.index(self.phase)
        phase_num = (phase_num + 1) % len(phases_list)
        self.day_of_phase = 1
        self.phase = phases_list[phase_num]
        input('change fertilizers to {} phase and press ENTER'.format(self.phase))
        self.logger.changePhase(self.phase)

    def readConfigsFromJsons(self):
        """Read configuration files"""
        list_of_files = glob.glob('./mainSoft/configs/*.json')
        for path in list_of_files:
            with open(path) as file:
                tmp_dict = dict(json.load(file))
                for key, value in tmp_dict.items():
                    setattr(self, key, value)

    def nextDay(self):
        """Increase day counter and change pahse if needed"""
        if self.day_of_phase >= self.phase_duration[self.phase]:
            self.changePhase()
        else:
            self.day_of_phase += 1
        self.logger.nextDay()

    def waterSetup(self):
        """
        1. Wait for the water level to adjust
        2. Stabilize the ph level
        3. Wait for the strawberries to be planted
        """
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
        """Check Ph value and dose ph regulators if needed"""
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
        """Check Ph value and dose fertilizers if needed"""
        ph = self.ph_sensor.read()
        if ph == -1:
            return self.codes['correct']
        self.sensors_indications['ph'] = ph
        if ph > self.indications_limits[self.phase]['ph']['standard'] + \
                self.indications_limits[self.phase]['ph']['hysteresis']:
            self.ph_minus_pump.dosing(1)
            self.logger.logging(sensors_indications=self.sensors_indications, message="dosing ph- (1)")
            return self.codes['to_high']
        elif ph < self.indications_limits[self.phase]['ph']['standard'] - \
                self.indications_limits[self.phase]['ph']['hysteresis']:
            self.ph_plus_pump.dosing(1)
            self.logger.logging(sensors_indications=self.sensors_indications, message="dosing ph+ (1)")
            return self.codes['to_low']
        else:
            return self.codes['correct']

    def tdsControl(self):
        """Check tds value and dose fertilizer if needed"""
        tds = self.tds_sensor.read()
        if tds == -1:
            return self.codes['correct']
        self.sensors_indications['tds'] = tds
        tds_limit = self.indications_limits[self.phase]['tds']['standard'] if self.fertilizer_dosing else self.indications_limits[self.phase]['tds']['standard'] - self.indications_limits[self.phase]['tds']['hysteresis']
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
        """Check temperature and switch fan and/or cooling if needed"""
        temperature = self.sensor_dht.readTemperature()
        self.sensors_indications['temperature'] = temperature
        if temperature > self.indications_limits[self.phase]['temperature'][self.logger.getDayPhase()]['standard'] + \
                self.indications_limits[self.phase]['temperature'][self.logger.getDayPhase()]['hysteresis']:
            self.cooling.switch(True)
            self.fan.switch(True)
        elif temperature <= self.indications_limits[self.phase]['temperature'][self.logger.getDayPhase()]['standard']:
            self.cooling.switch(False)
            self.fan.switch(False)
        else:
            self.cooling.switch(True)

    def humidityControl(self):
        """Check humidity and switch fan and/or atomizer if needed"""
        humidity = self.sensor_dht.readHumidity()
        self.sensors_indications['humidity'] = humidity
        if humidity < self.indications_limits[self.phase]['humidity']['standard'] - \
                self.indications_limits[self.phase]['humidity']['hysteresis']:
            self.atomizer.switch(True)
        elif humidity > self.indications_limits[self.phase]['humidity']['standard'] + \
                self.indications_limits[self.phase]['humidity']['hysteresis']:
            self.fan.switch(True)
            self.atomizer.switch(False)
        else:
            self.atomizer.switch(False)

    def grow(self):
        """Controll all parameters in infinite loop"""
        ph_delay = 0
        fertilizer_delay = 0
        while True:
            if self.modules_switches['temperature']:
                self.temperatureControl()
            if self.modules_switches['humidity']:
                self.humidityControl()
            if self.modules_switches['PH']:
                if ph_delay == 0:
                    if self.phControl() != self.codes['correct']:
                        ph_delay = self.ph_delay
                else:
                    ph_delay -= self.loop_delay
            if self.modules_switches['TDS']:
                if fertilizer_delay == 0:
                    if self.tdsControl() != self.codes['correct']:
                        fertilizer_delay = self.fertilizer_delay
                else:
                    fertilizer_delay -= self.loop_delay
            if self.modules_switches['lights']:
                self.dayCycleControl()
            self.logger.logging(sensors_indications=self.sensors_indications, print_only=True)
            time.sleep(self.loop_delay)
