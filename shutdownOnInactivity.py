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
INTERFACE = 'enp1s0'
MINIMUM_SPEED = 15 #kB/s
SAMPLES = 5
MAX_SSH_SESSION_AGE = 21600 #6h in seconds

def isSSHSessionActive():
    whoPattern = re.compile('(?P<userName>[^ ]+)\\s+(?P<session>[^ ]+)\\s+(?P<time>[^ ]+ [^ ]+)\\s+(?P<comment>.*)')
    whoOutput = getoutput('who')

    activeSessionFound = False

    if whoOutput == "":
        logging.info('No SSH sessions found.')
        return activeSessionFound

    for whoLine in whoOutput.split('\n'):
        match = whoPattern.match(whoLine)

        if not match:
            raise Exception(f'Could not parse output of who ("{whoLine}" as one line of "{whoOutput}")')
        
        sessionStart = dateutil.parser.parse(match.group('time'))
        sessionAge = datetime.now() - sessionStart

        logging.info(f'Found session {match.group("userName")} ({match.group("session")}) started at {sessionStart} (Comment: "{match.group("comment")}").')
        if sessionAge.seconds <= MAX_SSH_SESSION_AGE:
            activeSessionFound = True
        else:
            logging.info(f'Session is {sessionAge.seconds}s old. Hence it is considered dead.')

    return activeSessionFound
    

def isNetworkActive():
    accumulatedSpeed = 0
    for sample in range(SAMPLES):
        # Sum downstream and upstream and add with previous speed value
        # {print $1} use just downstream
        # {print $2} use just upstream
        # {print $1+$2} use sum of downstream and upstream
        speed = float(getoutput("ifstat -i %s 1 1 | awk '{print $1+$2}' | sed -n '3p'" % INTERFACE))
        accumulatedSpeed += speed
        logging.info(f'Sample {sample} for network traffic: {speed}kB/s')
        time.sleep(INTERVAL)

    # Calculate average speed from all retries
    averageSpeed = accumulatedSpeed / float(SAMPLES)
    logging.info(f'Average network traffic: {averageSpeed}kB/s')
                
    # If average speed is below minimum speed - suspend
    return averageSpeed > MINIMUM_SPEED


def worker(configFilePath):
    while True:
        try:
            time.sleep(LONG_INTERVAL)
           
            #Check configuration 
            if configFilePath is not None:
                config = configparser.ConfigParser()
                with open(configFilePath, 'r') as configFile:
                    config.read_file(configFile)
                isEnabled = config.get('shutdownOnInactivity', 'enabled') == 'True'
            else:
                isEnabled = True

            #Check inactivity
            if isEnabled and not isSSHSessionActive() and not isNetworkActive():
                logging.info('Shutting down...')
                os.system("sudo shutdown 0")
                time.sleep(LONG_INTERVAL) 
            # Else reset calculations and wait for longer to retry calculation
            else:
                time.sleep(LONG_INTERVAL)
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            time.sleep(LONG_INTERVAL)

if __name__ == "__main__":
    logFilePath = os.path.join('/var', 'log', 'shutdownOnInteractivity.log')

    #Command-line arguments
    if len(sys.argv) > 1:
        configFilePath = sys.argv[1] 

        config = configparser.ConfigParser()
        with open(configFilePath) as configFile:
            config.read_file(configFile)
        logFilePath = config.get('shutdownOnInactivity', 'logFilePath', fallback=logFilePath)
        
    logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO, handlers=[logging.FileHandler(logFilePath), logging.StreamHandler(sys.stdout)])
            

    logging.info('Starting...')

    worker(configFilePath)
