#!/usr/bin/env python3
#provides a status report in constants intervals
from datetime import datetime, MINYEAR
import logging
from os import path
from subprocess import getstatusoutput
from configuration import StaticSection, DynamicSection
from periodicTaskConfiguration import PeriodicTaskConfiguration
from notification.notification import Notification, Severity
    

def updatePackages(staticConfig, dynamicConfig, update, getCurrentTime):
    staticSection = StaticSection(staticConfig, 'packageSystem')
    dynamicSection = DynamicSection(dynamicConfig, 'packageSystem')
    DEFAULT_INTERVAL = 7 * 24 * 60 * 60
    LAST_UPDATE_KEY = 'lastUpdate'

    interval = staticSection.getint('interval', DEFAULT_INTERVAL)

    with PeriodicTaskConfiguration(dynamicSection, LAST_UPDATE_KEY, interval, getCurrentTime) as periodicCheck:
        if periodicCheck.periodicTaskIsDue:
            (status, output) = update()
            if status == 0:
                return Notification('Package update', output, Severity.INFO)
            else:
                logging.error(output)
                return Notification('Error during package update', output, Severity.ERROR)
        else:
            return None

