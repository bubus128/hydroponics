import json
import os
import glob
from datetime import datetime
import time
from picamera import PiCamera


class Logger:
    log = {
        'timer': None,
        'day': 0,
        'phase': 'growth',
        'day_phase': 'day',
        'day_of_phase': 0
    }
    error_header = "----------ERROR----------"

    def __init__(self):
        """
        1. Set the timer
        2. Initialize the camera
        """
        self.log['timer'] = datetime.now()
        self.camera = PiCamera()

    def getLastLog(self):
        """Load last log file and set parameters"""
        list_of_files = glob.glob('../logs/*.json')
        if len(list_of_files) == 0:
            return False
        else:
            latest_file = max(list_of_files, key=os.path.getctime)
            with open(latest_file) as json_file:
                log = json.load(json_file)
                self.log['day'] = log['day']
                self.log['phase'] = log['phase']
                self.log['day_phase'] = log['day_phase']
                self.log['day_of_phase'] = log['day_of_phase']
            return self.log

    def changePhase(self, phase):
        """Change the phase
        
        Keyword arguments:
        phase -- phase to switch
        """
        self.log['phase'] = phase
        self.log['day_of_phase'] = 0

    def nextDay(self):
        """Switch to the next day"""
        self.log['day'] += 1
        self.log['day_of_phase'] += 1

    def getTimer(self):
        """Return current timer"""
        return self.log['timer']

    def updateTime(self):
        """Timer update"""
        self.log['timer'] = datetime.now()

    def day(self):
        """Set day phase to day"""
        self.log['day_phase'] = 'day'

    def night(self):
        """Set day phase to night"""
        self.log['day_phase'] = 'night'

    def getDayPhase(self):
        """Return current day phase"""
        return self.log['day_phase']

    def logging(self, sensors_indications, error=None, message=None, print_only=False):
        """Create a log and save it"""
        self.updateTime()
        if error is not None:
            err_dir = '../error_logs/day_{}_phase_{}.json'.format(self.log['day'], self.log['phase'])
            print("{}\n{}\n{}".format(self.error_header, str(error), self.error_header))
            with open(err_dir, 'w') as ep:
                error_dict = {str(self.log['timer'].strftime("%m.%d.%Y, %H:%M:%S")): error}
                json.dump(error_dict, ep)
        else:
            log = self.log.copy()
            log['timer'] = log['timer'].strftime("%m.%d.%Y, %H:%M:%S")
            if message is not None:
                log['message'] = message
            self.printer(log)
            self.printer(sensors_indications)
            if not print_only:
                log_dir = '../logs/{}.json'.format(log['timer'])
                log['sensors_indications'] = sensors_indications
                with open(log_dir, 'w') as fp:
                    json.dump(log, fp)

    def takePhoto(self):
        """Take a photo and save it"""
        timer = self.log['timer'].strftime("%m.%d.%Y, %H:%M:%S")
        photo_dir = "../photos/{}.jpg".format(timer)
        self.camera.start_preview()
        time.sleep(3)
        self.camera.capture(photo_dir)
        self.camera.stop_preview()

    @staticmethod
    def printer(dictionary):
        """Print given dictionary in pattern 'key : value'
        
        Keyword arguments:
        dictionary -- dictionary to print
        """
        for key, value in dictionary.items():
            print(key, ' : ', value)
