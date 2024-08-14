#!/usr/bin/env python3
#base for a cronjob that runs continously and performs regular actions
import os
from backup import backup
from configuration import StaticConfiguration, DynamicConfiguration
from dataConsistency import dataConsistency
from os import path
from subprocess import getoutput, getstatusoutput
from datetime import datetime
import time
from dataConsistency.btrfsChecking import BtrfsChecking
from dataConsistency.btrfsScrubbing import BtrfsScrubbing
from backup.btrfsSnapshotting import BtrfsSnapshotting
import logging
import sys
import packageSystem
import periodicStatusReport
import notification.emailNotification as emailNotification
from notification.emailSender import EMailSender
import shutdown

ITERATION_INTERVAL = 3

class Factory:
    def getFilesystemScrubbing():
        return BtrfsScrubbing()
    
    def getFilesystemChecking():
        return BtrfsChecking()
    
    def getCurrentTimeFunctor():
        return datetime.now
    
    def getPackageUpdater():
        return lambda: getstatusoutput('apt-get update && apt-get upgrade -y')
                               
    def getSnapshotting(self, fileSystem, subvolume, snapshotsDirectory):
        return BtrfsSnapshotting(fileSystem, subvolume, snapshotsDirectory)
    
    def getEMailSender(self):
        return EMailSender()
    
    def getUserSessionFunctor(self):
        return lambda: getoutput('who')
    
    def getNetworkTrafficFunctor(self):
        def _getAveragedNetworkTraffic(interface):    
            SAMPLES = 5
            accumulatedSpeed = 0
            for sample in range(5):
                # Sum downstream and upstream and add with previous speed value
                # {print $1} use just downstream
                # {print $2} use just upstream
                # {print $1+$2} use sum of downstream and upstream
                speed = float(getoutput("ifstat -i %s 1 1 | awk '{print $1+$2}' | sed -n '3p'" % interface))
                accumulatedSpeed += speed
                logging.info(f'Sample {sample} for network traffic: {speed}kB/s')
                time.sleep(2)

            # Calculate average speed from all retries
            averageSpeed = accumulatedSpeed / float(SAMPLES)
        return _getAveragedNetworkTraffic
    
    def getShutdownFunctor(self):
        def _shutdown():
            os.system("sudo shutdown 0")
            time.sleep(60) 
        return _shutdown

def performUpdates(staticConfig, dynamicConfig, factory):
    notifications = []
    currentTimeFunctor = factory.getCurrentTimeFunctor()

    logging.info('Updating snapshots')
    backupReport = backup.updateSnapshots(staticConfig, dynamicConfig, factory, currentTimeFunctor)
    notifications.extend(backupReport)

    logging.info('Updating system')
    updateReport = packageSystem.updatePackages(staticConfig, dynamicConfig, factory.getPackageUpdater(), currentTimeFunctor)
    if updateReport is not None: notifications.append(updateReport)
    
    logging.info('Checking consistency')
    consistencyReport = dataConsistency.verifyDataConsistency(staticConfig, dynamicConfig, factory.getFilesystemScrubbing(), factory.getFilesystemChecking(), currentTimeFunctor)
    notifications.extend(consistencyReport)

    logging.info('Assembling status report')
    statusReport = periodicStatusReport.getServerStatus(staticConfig, dynamicConfig, factory.getCurrentTimeFunctor())
    if statusReport is not None: notifications.append(statusReport)

    if len(notifications) > 0:
        logging.info(f'Sending {len(notifications)} notifications via e-mail.')
        emailNotification.sendMail(staticConfig, notifications, factory.getEMailSender())

    logging.info('Checking for shutdown')
    shutdown.shutdownOnInactivity(
        staticConfig, 
        factory.getCurrentTimeFunctor(), 
        factory.getUserSessionsFunctor(), 
        factory.getNetworkTrafficFunctor(),
        factory.getShutdownFunctor())


if __name__ == '__main__':
    scriptName = path.splitext(path.basename(__file__))[0]

    #Command-line arguments
    if len(sys.argv) > 2:
        staticConfigFile = sys.argv[1]
        dynamicConfigFile = sys.argv[2]
    else:
        raise Exception('Paths for static and dynamic configuration required.')

    staticConfig = StaticConfiguration(staticConfigFile)
    logFilePath = staticConfig.get('logging', 'logFilePath', f'/var/log/{scriptName}.log')
    logLevel = staticConfig.get('logging', 'level', 'INFO')

    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO[logLevel], handlers=[logging.FileHandler(logFilePath), logging.StreamHandler(sys.stdout)])

    logging.info('===========')
    logging.info('Starting...')

    while True:
        try:
            time.sleep(ITERATION_INTERVAL)

            with DynamicConfiguration(dynamicConfigFile) as dynamicConfig:
                if staticConfig.isValid() and dynamicConfig.isValid():
                    performUpdates(staticConfig, dynamicConfig, Factory())
                else:
                    if not staticConfig.isValid():
                        logging.error(f'The config file {staticConfigFile} could not be found.')
                    if not dynamicConfig.isValid():
                        logging.error(f'The config file {dynamicConfigFile} could not be found.')

        except Exception as e:
            logging.exception(f'Error occurred: {e}')
            
