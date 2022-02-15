#!/usr/bin/env python3
#provides a status report in constants intervals
from datetime import datetime, MINYEAR
from os import path
from subprocess import getoutput

def getServerStatus(config):
    scriptName = path.splitext(path.basename(__file__))[0]
    DEFAULT_INTERVAL = 24 * 60 * 60
    FORMAT = '%y-%m-%d %H:%M:%S'
    LAST_REPORT_KEY = 'lastReport'

    interval = config.getint(scriptName, 'interval', DEFAULT_INTERVAL)
    lastReportTimestamp = datetime.strptime(config.get(scriptName, LAST_REPORT_KEY, '0001-01-01 00:00:00'), FORMAT)
    now = datetime.now()

    timeSinceLastReport = now - lastReportTimestamp
    
    if timeSinceLastReport.total_seconds() >= interval:
        header = 'The following reboot times have been logged:'
        reboots = getoutput('last -x reboot | head -n 10')

        config.set(scriptName, LAST_REPORT_KEY, now.strftime(FORMAT))
        return f'{header}\n{reboots}\n'
    else:
        return None

