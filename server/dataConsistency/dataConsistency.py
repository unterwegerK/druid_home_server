#!/usr/bin/env python3
#provides a status report in constants intervals
from datetime import datetime, MINYEAR
import logging
from periodicTaskConfiguration import PeriodicTaskConfiguration
from dataConsistency import dataConsistencyConfigurationParser
from configuration import StaticSection, DynamicSection
from notification import Notification, Severity
    
def _scrubBackupVolume(fileSystem, timeout, btrfsScrubbing, getCurrentTime):
    btrfsScrubbing.startScrubbing(fileSystem)

    startTime = getCurrentTime()

    scrubOutput = None
    finished = False
    while not finished:
        scrubOutput = btrfsScrubbing.getScrubStatus(fileSystem) 
        status = btrfsScrubbing.parseScrubOutput(scrubOutput)
        
        if status == 'aborted':
            errorMessage = f'Scrubbing was aborted with the following output:\n--------\n{scrubOutput}\n--------'
            logging.error(errorMessage)
            return errorMessage

        if status == 'finished':
            return f'Scrubbing successful with the following output:\n--------\n{scrubOutput}\n--------'

        if status == 'running' and (getCurrentTime() - startTime).total_seconds() >= timeout:
            errorMessage = f'Timeout during scrubbing. Last output:\n--------\n{scrubOutput}\n--------'
            logging.error(errorMessage)
            return errorMessage

        if status != 'running':
            errorMessage = f'Unknown status of scrubbing. Last output:\n--------\n{scrubOutput}\n--------'
            logging.error(errorMessage)
            return errorMessage

def _performScrubbings(staticConfiguration, dynamicConfiguration, btrfsScrubbing, getCurrentTime):
    DEFAULT_INTERVAL = 23 * 24 * 60 * 60
    DEFAULT_TIMEOUT = 5 * 60 * 60
    LAST_SCRUB_KEY = 'lastScrub'

    staticSection = StaticSection(staticConfiguration, 'dataConsistency')
    dynamicSection = DynamicSection(dynamicConfiguration, 'dataConsistency')
    
    timeout = staticSection.getint('scrubTimeout', DEFAULT_TIMEOUT)
    interval = staticSection.getint('scrubInterval', DEFAULT_INTERVAL)

    messages = []
    with PeriodicTaskConfiguration(dynamicSection, LAST_SCRUB_KEY, interval, getCurrentTime) as periodicCheck:
        if periodicCheck.periodicTaskIsDue:

            backupVolumes = dataConsistencyConfigurationParser.getBackupVolumes(staticConfiguration)

            for fileSystem in backupVolumes:
                message = _scrubBackupVolume(fileSystem, timeout, btrfsScrubbing, getCurrentTime)
                if not message is None:
                    messages.append(message)

    return messages

def _checkDevice(backupDevice, btrfsChecking):
    output = btrfsChecking.checkDevice(backupDevice)
    (numberOfErrors, header, message) = btrfsChecking.parseCheckOutput(output)
    return Notification(header, message, Severity.ERROR if numberOfErrors > 0 else Severity.INFO)

def _performBtrfsCheck(staticConfiguration, dynamicConfiguration, btrfsChecking, getCurrentTime):
    DEFAULT_INTERVAL = 31 * 24 * 60 * 60
    LAST_CHECK_KEY = 'lastCheck'

    staticSection = StaticSection(staticConfiguration, 'dataConsistency')
    dynamicSection = DynamicSection(dynamicConfiguration, 'dataConsistency')
    
    interval = staticSection.getint('checkInterval', DEFAULT_INTERVAL)

    suspendCommand = staticSection.get('suspendCommand', None)

    if suspendCommand is None:
        return [Message('Key suspendCommand must be defined in section dataConsistency', Severity.ERROR)]

    messages = []
    with PeriodicTaskConfiguration(dynamicSection, LAST_CHECK_KEY, interval, getCurrentTime) as periodicCheck:
        if periodicCheck.periodicTaskIsDue:
            
            backupDevices = dataConsistencyConfigurationParser.getBackupDevices(staticSection)

            btrfsChecking.suspend(suspendCommand)

            for backupDevice in backupDevices:
                messages.append(_checkDevice(backupDevice, btrfsChecking))

    return messages
   

def verifyDataConsistency(staticConfiguration, dynamicConfiguration, btrfsScrubbing, btrfsChecking, getCurrentTime=datetime.now):
    messages = []

    messages.extend(_performScrubbings(staticConfiguration, dynamicConfiguration, btrfsScrubbing, getCurrentTime))

    messages.extend(_performBtrfsCheck(staticConfiguration, dynamicConfiguration, btrfsChecking, getCurrentTime))

    return messages


