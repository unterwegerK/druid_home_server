#!/usr/bin/env python3
#starting point taken from https://askubuntu.com/questions/105536/tool-to-shutdown-system-when-there-is-no-network-traffic

import configparser, os, time, sys
import logging
from subprocess import getoutput
import re
import dateutil.parser
from datetime import datetime

INTERVAL = 2
LONG_INTERVAL = 300
MINIMUM_SPEED = 15 #kB/s
MAX_SSH_SESSION_AGE = 21600 #6h in seconds

def isSSHSessionActive(getCurrentTime, getUserSessions):
    whoPattern = re.compile('(?P<userName>[^ ]+)\\s+(?P<session>[^ ]+)\\s+(?P<time>[^ ]+ [^ ]+)\\s+(?P<comment>.*)')
    whoOutput = getUserSessions()

    activeSessionFound = False

    if whoOutput == "":
        logging.info('No SSH sessions found.')
        return activeSessionFound

    for whoLine in whoOutput.split('\n'):
        match = whoPattern.match(whoLine)

        if not match:
            raise Exception(f'Could not parse output of who ("{whoLine}" as one line of "{whoOutput}")')
        
        sessionStart = dateutil.parser.parse(match.group('time'))
        sessionAge = getCurrentTime() - sessionStart

        logging.info(f'Found session {match.group("userName")} ({match.group("session")}) started at {sessionStart} (Comment: "{match.group("comment")}").')
        if sessionAge.seconds <= MAX_SSH_SESSION_AGE:
            activeSessionFound = True
        else:
            logging.info(f'Session is {sessionAge.seconds}s old. Hence it is considered dead.')

    return activeSessionFound
    

def isNetworkActive(networkInterface, getNetworkTraffic):
    averageSpeed = getNetworkTraffic(networkInterface)
    logging.info(f'Average network traffic: {averageSpeed}kB/s')
                
    # If average speed is below minimum speed - suspend
    return averageSpeed > MINIMUM_SPEED

def shutdownOnInactivity(config, getCurrentTime, getUserSessions, getNetworkTraffic, shutdown):
            isEnabled = config.getboolean('shutdownOnInactivity', 'enabled', True)
            networkInterface = config.get('shutdownOnInactivity', 'networkInterface', None)

            if networkInterface is None:
                 raise Exception('Key networkInterface must be defined in section shutdownOnInactivity.')

            #Check inactivity
            if isEnabled and not isSSHSessionActive(getCurrentTime, getUserSessions) and not isNetworkActive(networkInterface, getNetworkTraffic):
                logging.info('Shutting down...')
                shutdown()

