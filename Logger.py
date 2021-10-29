import json
import os
import glob
from datetime import datetime


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
        self.log['timer'] = datetime.now()

    def getLastLog(self):
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
            return True

    def changePhase(self, phase):
        self.log['phase'] = phase
        self.log['day_of_phase'] = 0

    def nextDay(self):
        self.log['day'] += 1
        self.log['day_of_phase'] += 1

    def getTimer(self):
        return self.log['timer']

    def updateTime(self):
        self.log['timer'] = datetime.now()

    def day(self):
        self.log['day_phase'] = 'day'

    def night(self):
        self.log['day_phase'] = 'night'

    def getDayPhase(self):
        return self.log['day_phase']

    def logging(self, sensors_indications, error=None, message=None, print_only=False):
        self.updateTime()
        if error is not None:
            err_dir = '../eroor_logs/day_{}_phase_{}.json'.format(self.log['day'],self.log['phase'])
            print("{}\n{}\n{}".format(self.error_header,str(error),self.error_header))
            with open(err_dir, 'w') as ep:
                error_dict = {str(self.log['timer']): error}
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

    @staticmethod
    def printer(dictionary):
        for key, value in dictionary.items():
            print(key, ' : ', value)
