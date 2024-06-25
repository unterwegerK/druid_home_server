#!/usr/bin/env python3
#provides a status report in constants intervals
from datetime import datetime, MINYEAR
import logging
from os import path
from subprocess import getstatusoutput
from configuration import StaticSection, DynamicSection
from periodicTaskConfiguration import PeriodicTaskConfiguration

def _updateAptPackages():
    return getstatusoutput('apt-get update && apt-get upgrade -y')
    

def updatePackages(config, getCurrentTime=datetime.now, update=_updateAptPackages):
    staticSection = StaticSection(config, 'packageSystem')
    dynamicSection = DynamicSection(config, 'packageSystem')
    DEFAULT_INTERVAL = 7 * 24 * 60 * 60
    FORMAT = '%Y-%m-%d %H:%M:%S'
    LAST_UPDATE_KEY = 'lastUpdate'

    interval = staticSection.getint('interval', DEFAULT_INTERVAL)

    with PeriodicTaskConfiguration(dynamicSection, LAST_UPDATE_KEY, interval, getCurrentTime) as periodicCheck:
        if periodicCheck.periodicTaskIsDue:
            (status, output) = update()
            if output == 0:
                message = output
            else:
                message = f'Error during package update!\n{output}'
                logging.error(message)
            return message
        else:
            return None

