#!/usr/bin/env python3
#provides a status report in constants intervals
from datetime import datetime, MINYEAR
import logging
from os import path
from subprocess import getoutput
from configuration import Section
from periodicTaskConfiguration import PeriodicTaskConfiguration

def getServerStatus(config, getCurrentTime=datetime.now):
    section = Section(config, 'periodicStatusReport')
    DEFAULT_INTERVAL = 24 * 60 * 60
    FORMAT = '%Y-%m-%d %H:%M:%S'
    LAST_REPORT_KEY = 'lastReport'

    interval = section.getint('interval', DEFAULT_INTERVAL)

    with PeriodicTaskConfiguration(section, LAST_REPORT_KEY, interval, getCurrentTime) as periodicReport:
        if periodicReport.periodicTaskIsDue:
            rebootHeader = 'The following reboot times have been logged:'
            reboots = getoutput('last -x reboot | head -n 8 | cut -d " " -f 1,8-')
            
            #btrfs filesystem usage /media/data/
            btrfsFileSystem = section.get('btrfsFileSystem', None)
            availableSpaceHeader = 'The following disk space is available:'
            availableSpace = 'No btrfs file-system specified...' if btrfsFileSystem is None else getoutput(f'btrfs filesystem usage {btrfsFileSystem} | head -n10 | grep "Free\|Used"')

            return f'{rebootHeader}\n{reboots}\n\n{availableSpaceHeader}\n{availableSpace}'
        else:
            return None

