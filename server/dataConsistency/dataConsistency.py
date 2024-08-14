#!/usr/bin/env python3
#provides a status report in constants intervals
from datetime import datetime, MINYEAR
import logging
from periodicTaskConfiguration import PeriodicTaskConfiguration
from dataConsistency import dataConsistencyConfigurationParser
from configuration import StaticSection, DynamicSection
from notification.notification import Notification, Severity
    
def _scrubFileSystem(fileSystem, timeout, btrfsScrubbing, getCurrentTime):
    btrfsScrubbing.startScrubbing(fileSystem)

    startTime = getCurrentTime()

    scrubOutput = None
    finished = False
    while not finished:
        scrubOutput = btrfsScrubbing.getScrubStatus(fileSystem) 
        status = btrfsScrubbing.parseScrubOutput(scrubOutput)
        
        if status == 'aborted':
            errorMessage = f'Scrubbing was aborted for file system {fileSystem} with the following output:\n--------\n{scrubOutput}\n--------'
            logging.error(errorMessage)
            return (Severity.ERROR, 'Scrub aborted', errorMessage)

        if status == 'finished':
            return (Severity.INFO, 'Btrfs Scrub', f'Scrubbing successful with the following output:\n--------\n{scrubOutput}\n--------')

        if status == 'running' and (getCurrentTime() - startTime).total_seconds() >= timeout:
            errorMessage = f'Timeout during scrubbing. Last output:\n--------\n{scrubOutput}\n--------'
            logging.error(errorMessage)
            return (Severity.ERROR, 'Timeout during scrub', errorMessage)

        if status != 'running':
            errorMessage = f'Unknown status of scrubbing. Last output:\n--------\n{scrubOutput}\n--------'
            logging.error(errorMessage)
            return (Severity.ERROR, 'Unknown scrub status', errorMessage)

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

            backupFileSystems = dataConsistencyConfigurationParser.getBackupFileSystems(staticConfiguration)

            for backupFileSystem in backupFileSystems:
                (severity, header, message) = _scrubFileSystem(backupFileSystem, timeout, btrfsScrubbing, getCurrentTime)
                if not message is None:
                    messages.append(Notification(header, message, severity))

    return messages

def _checkDevice(backupDevice, btrfsChecking):
    (exitcode, output) = btrfsChecking.checkDevice(backupDevice)
    btrfsChecking.containsErrors(output)
    header = 'Btrfs Check'
    if (exitcode != 0 or btrfsChecking.containsErrors(output)):
        return Notification(header, f'Btrfs check failed for device {backupDevice}:\n' + output, Severity.ERROR)
    else:
        return Notification(header, output, Severity.INFO)

def _performBtrfsCheck(staticConfiguration, dynamicConfiguration, btrfsChecking, getCurrentTime):
    DEFAULT_INTERVAL = 31 * 24 * 60 * 60
    LAST_CHECK_KEY = 'lastCheck'

    staticSection = StaticSection(staticConfiguration, 'dataConsistency')
    dynamicSection = DynamicSection(dynamicConfiguration, 'dataConsistency')
    
    interval = staticSection.getint('checkInterval', DEFAULT_INTERVAL)

    suspendCommand = staticSection.get('suspendCommand', None)

    if suspendCommand is None:
        return [Notification('Btrfs Check', 'Key suspendCommand must be defined in section dataConsistency', Severity.ERROR)]

    messages = []
    with PeriodicTaskConfiguration(dynamicSection, LAST_CHECK_KEY, interval, getCurrentTime) as periodicCheck:
        if periodicCheck.periodicTaskIsDue:
            
            backupFileSystems = dataConsistencyConfigurationParser.getBackupFileSystems(staticConfiguration)

            logging.info(f'Running suspend command {suspendCommand}')
            btrfsChecking.suspend(suspendCommand)

            for backupFileSystem in backupFileSystems:
                messages.append(_checkDevice(backupFileSystem, btrfsChecking))

    return messages
   

def verifyDataConsistency(staticConfiguration, dynamicConfiguration, btrfsScrubbing, btrfsChecking, getCurrentTime):
    messages = []

    messages.extend(_performScrubbings(staticConfiguration, dynamicConfiguration, btrfsScrubbing, getCurrentTime))

    messages.extend(_performBtrfsCheck(staticConfiguration, dynamicConfiguration, btrfsChecking, getCurrentTime))

    return messages


