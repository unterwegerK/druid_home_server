#!/usr/bin/env python3
#provides a status report in constants intervals
from datetime import datetime, MINYEAR
import logging
from os import path
from subprocess import getstatusoutput

def _updateAptPackages():
    return getstatusoutput('apt-get update && apt-get upgrade -y')
    

def updatePackages(config, getCurrentTime=datetime.now, update=_updateAptPackages):
    scriptName = path.splitext(path.basename(__file__))[0]
    DEFAULT_INTERVAL = 7 * 24 * 60 * 60
    FORMAT = '%Y-%m-%d %H:%M:%S'
    LAST_UPDATE_KEY = 'lastUpdate'

    interval = config.getint(scriptName, 'interval', DEFAULT_INTERVAL)
    lastUpdateTimestamp = datetime.strptime(config.get(scriptName, LAST_UPDATE_KEY, '0001-01-01 00:00:00'), FORMAT)
    now = getCurrentTime()

    timeSinceLastUpdate = now - lastUpdateTimestamp

    if timeSinceLastUpdate.total_seconds() >= interval:
        config.set(scriptName, LAST_UPDATE_KEY, now.strftime(FORMAT))

        (status, output) = update()
        if output == 0:
            message = output
        else:
            message = f'Error during package update!\n{output}'
            logging.error(message)
        return message
    else:
        return None

