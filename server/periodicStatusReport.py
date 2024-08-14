#provides a status report in constants intervals
from datetime import datetime, MINYEAR
from subprocess import getoutput
from configuration import StaticSection, DynamicSection
from periodicTaskConfiguration import PeriodicTaskConfiguration
from notification.notification import Notification, Severity

def getServerStatus(staticConfig, dynamicConfig, getCurrentTime):
    staticSection = StaticSection(staticConfig, 'periodicStatusReport')
    dynamicSection = DynamicSection(dynamicConfig, 'periodicStatusReport')
    DEFAULT_INTERVAL = 24 * 60 * 60
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

            return Notification('Status Report', f'{rebootHeader}\n{reboots}\n\n{availableSpaceHeader}\n{availableSpace}', Severity.INFO)
        else:
            return None

