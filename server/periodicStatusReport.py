#!/usr/bin/env python3
#provides a status report in constants intervals
from datetime import datetime, MINYEAR
import logging
from os import path
from subprocess import getoutput

def getServerStatus(config, getCurrentTime=datetime.now):
    scriptName = path.splitext(path.basename(__file__))[0]
    DEFAULT_INTERVAL = 24 * 60 * 60
    FORMAT = '%Y-%m-%d %H:%M:%S'
    LAST_REPORT_KEY = 'lastReport'

    interval = config.getint(scriptName, 'interval', DEFAULT_INTERVAL)
    lastReportTimestamp = datetime.strptime(config.get(scriptName, LAST_REPORT_KEY, '0001-01-01 00:00:00'), FORMAT)
    now = getCurrentTime()

    timeSinceLastReport = now - lastReportTimestamp

    if timeSinceLastReport.total_seconds() >= interval:
        rebootHeader = 'The following reboot times have been logged:'
        reboots = getoutput('last -x reboot | head -n 8 | cut -d " " -f 1,8-')
        
        #btrfs filesystem usage /media/data/
        btrfsFileSystem = config.get(scriptName, 'btrfsFileSystem', None)
        availableSpaceHeader = 'The following disk space is available:'
        availableSpace = 'No btrfs file-system specified...' if btrfsFileSystem is None else getoutput(f'btrfs filesystem usage {btrfsFileSystem} | head -n10 | grep "Free\|Used"')

        config.set(scriptName, LAST_REPORT_KEY, now.strftime(FORMAT))
        return f'{rebootHeader}\n{reboots}\n\n{availableSpaceHeader}\n{availableSpace}'
    else:
        return None

