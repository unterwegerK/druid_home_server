#!/usr/bin/env python3
#provides a status report in constants intervals
from datetime import datetime, MINYEAR
import logging
from os import path
from subprocess import getoutput
import re
from periodicTaskConfiguration import PeriodicTaskConfiguration
from configuration import Section
from dataConsistency import dataConsistencyConfigurationParser

def _startScrubbing(fileSystem):
    getoutput(f'btrfs scrub start {fileSystem}')

def _getScrubStatus(fileSystem):
    return getoutput(f'btrfs scrub status {fileSystem}')
        
def _parseScrubOutput(scrubOutput):    
    if m := re.search(r'\s*Status:\s*([a-zA-Z0-9_]*)', scrubOutput):
        return m.group(1)
    return None
    
def _scrubBackupVolume(section, fileSystem, getCurrentTime, startScrubbing, getScrubStatus):
    DEFAULT_INTERVAL = 14 * 24 * 60 * 60
    DEFAULT_TIMEOUT = 5 * 60 * 60
    LAST_SCRUB_KEY = 'lastScrub'
    
    timeout = section.getint('timeout', DEFAULT_TIMEOUT)

    interval = section.getint('interval', DEFAULT_INTERVAL)

    with PeriodicTaskConfiguration(section, LAST_SCRUB_KEY, interval, getCurrentTime) as periodicCheck:
        if periodicCheck.periodicTaskIsDue:
            startScrubbing(fileSystem)

            startTime = getCurrentTime()

            scrubOutput = None
            finished = False
            while not finished:
                scrubOutput = getScrubStatus(fileSystem) 
                status = _parseScrubOutput(scrubOutput)
                
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

    return None

def verifyDataConsistency(configuration, getCurrentTime=datetime.now, startScrubbing=_startScrubbing, getScrubStatus=_getScrubStatus):
    backupVolumes = dataConsistencyConfigurationParser.getBackupVolumes(configuration)
    messages = []

    for fileSystem, section in backupVolumes:
        message = _scrubBackupVolume(section, fileSystem, getCurrentTime, startScrubbing, getScrubStatus)
        if not message is None:
            messages.append(message)

    return '\n'.join(messages)


