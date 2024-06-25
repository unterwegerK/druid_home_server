#!/usr/bin/env python3
#provides a status report in constants intervals
from datetime import datetime, MINYEAR
import logging
from os import path
from subprocess import getoutput
from configuration import StaticSection, DynamicSection
from periodicTaskConfiguration import PeriodicTaskConfiguration

def getServerStatus(staticConfig, dynamicConfig, getCurrentTime=datetime.now):
    staticSection = StaticSection(staticConfig, 'periodicStatusReport')
    dynamicSection = DynamicSection(dynamicConfig, 'periodicStatusReport')
    DEFAULT_INTERVAL = 24 * 60 * 60
    FORMAT = '%Y-%m-%d %H:%M:%S'
    LAST_REPORT_KEY = 'lastReport'

    interval = staticSection.getint('interval', DEFAULT_INTERVAL)

    with PeriodicTaskConfiguration(dynamicSection, LAST_REPORT_KEY, interval, getCurrentTime) as periodicReport:
        if periodicReport.periodicTaskIsDue:
            rebootHeader = 'The following reboot times have been logged:'
            reboots = getoutput('last -x reboot | head -n 8 | cut -d " " -f 1,8-')
            
            #btrfs filesystem usage /media/data/
            btrfsFileSystem = staticSection.get('btrfsFileSystem', None)
            availableSpaceHeader = 'The following disk space is available:'
            availableSpace = 'No btrfs file-system specified...' if btrfsFileSystem is None else getoutput(f'btrfs filesystem usage {btrfsFileSystem} | head -n10 | grep "Free\|Used"')

            return f'{rebootHeader}\n{reboots}\n\n{availableSpaceHeader}\n{availableSpace}'
        else:
            return None

