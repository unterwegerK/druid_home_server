#provides a status report in constants intervals
from datetime import datetime, MINYEAR
import logging
from subprocess import getoutput
from configuration import StaticSection, DynamicSection
from dataConsistency import dataConsistencyConfigurationParser
from periodicTaskConfiguration import PeriodicTaskConfiguration
from notification.notification import Notification, Severity

def getServerStatus(staticConfig, dynamicConfig, getCurrentTime, getFileSystemUsage):
    staticSection = StaticSection(staticConfig, 'periodicStatusReport')
    dynamicSection = DynamicSection(dynamicConfig, 'periodicStatusReport')
    DEFAULT_INTERVAL = 24 * 60 * 60
    LAST_REPORT_KEY = 'lastReport'

    interval = staticSection.getint('interval', DEFAULT_INTERVAL)

    with PeriodicTaskConfiguration(dynamicSection, LAST_REPORT_KEY, interval, getCurrentTime) as periodicReport:
        if periodicReport.periodicTaskIsDue:
            rebootHeader = 'The following reboot times have been logged:'
            reboots = getoutput('last -x reboot | head -n 8 | cut -d " " -f 1,8-')
            
            backupFileSystem = dataConsistencyConfigurationParser.getBackupFileSystems(staticConfig)

            entries = []
            for backupFileSystem in backupFileSystem:
                availableSpaceHeader = f'The following disk space is available for {backupFileSystem}:'
                availableSpace = getFileSystemUsage(backupFileSystem)
                entries.append(f'{availableSpaceHeader}\n{availableSpace}')
            availableSpaceEntries = '\n\n'.join(entries)

            return Notification('Status Report', f'{rebootHeader}\n{reboots}\n\n{availableSpaceEntries}', Severity.INFO)
        else:
            return None

