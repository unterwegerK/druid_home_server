#!/usr/bin/env python3
#provides a status report in constants intervals
from datetime import datetime, MINYEAR
import logging
from os import path
from subprocess import getoutput
import re

def _startScrubbing():
    getoutput(f'btrfs scrub start {fileSystem}')

def _parseScrubOutput(scrubOutput):    
    if m := re.search(r'\s*Status:\s*([a-zA-Z0-9_]*)', scrubOutput):
        return m.group(1)

def _getScrubStatus(fileSystem):
    return getoutput(f'btrfs scrub status {fileSystem}')
        

def verifyDataConsistency(config, getCurrentTime=datetime.now, startScrubbing=_startScrubbing, getScrubStatus=_getScrubStatus):
    scriptName = path.splitext(path.basename(__file__))[0]
    DEFAULT_INTERVAL = 14 * 24 * 60 * 60
    DEFAULT_TIMEOUT = 5 * 60 * 60
    FORMAT = '%Y-%m-%d %H:%M:%S'
    LAST_SCRUB_KEY = 'lastScrub'

    fileSystem = config.get(scriptName, 'fileSystem', None)
    if fileSystem is None:
        errorMessage = f'fileSystem has to be specified for section {scriptName}'
        logging.error(errorMessage)
        return errorMessage
    
    timeout = config.getint(scriptName, 'timeout', DEFAULT_TIMEOUT)

    interval = config.getint(scriptName, 'interval', DEFAULT_INTERVAL)
    lastScrubTimestamp = datetime.strptime(config.get(scriptName, LAST_SCRUB_KEY, '0001-01-01 00:00:00'), FORMAT)
    now = getCurrentTime()
    timeSinceLastScrubbing = now - lastScrubTimestamp

    if timeSinceLastScrubbing.total_seconds() >= interval:
        config.set(scriptName, LAST_SCRUB_KEY, now.strftime(FORMAT))

        startScrubbing(fileSystem)

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

            if status == 'running' and (getCurrentTime() - now).total_seconds() >= timeout:
                errorMessage = f'Timeout during scrubbing. Last output:\n--------\n{scrubOutput}\n--------'
                logging.error(errorMessage)
                return errorMessage

            if status != 'running':
                errorMessage = f'Unknown status of scrubbing. Last output:\n--------\n{scrubOutput}\n--------'
                logging.error(errorMessage)
                return errorMessage

    return None

