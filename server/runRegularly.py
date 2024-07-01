#!/usr/bin/env python3
#base for a cronjob that runs continously and performs regular actions
from backup import backup
from configuration import StaticConfiguration, StaticSection, DynamicConfiguration, DynamicSection
from dataConsistency import dataConsistency
import emailNotification
import packageSystem
import periodicStatusReport
import logging
from os import path
import sys
import shutdown
import time
from dataConsistency.btrfsChecking import BtrfsChecking
from dataConsistency.btrfsScrubbing import BtrfsScrubbing

ITERATION_INTERVAL = 300

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

    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO, handlers=[logging.FileHandler(logFilePath), logging.StreamHandler(sys.stdout)])

    logging.info('===========')
    logging.info('Starting...')

    while True:
        try:
            time.sleep(ITERATION_INTERVAL)

            with DynamicConfiguration(dynamicConfigFile) as dynamicConfig:
                if staticConfig.isValid() and dynamicConfig.isValid():
                    notifications = []

                    logging.info('Updating snapshots')
                    backupReport = backup.updateSnapshots(staticConfig, dynamicConfig)
                    notifications.extend(backupReport)
        
                    logging.info('Updating system')
                    updateReport = packageSystem.updatePackages(staticConfig, dynamicConfig)
                    if updateReport is not None: notifications.append(updateReport)
                    
                    logging.info('Checking consistency')
                    consistencyReport = dataConsistency.verifyDataConsistency(staticConfig, dynamicConfig, BtrfsScrubbing(), BtrfsChecking())
                    notifications.extend(consistencyReport)

                    logging.info('Assembling status report')
                    statusReport = periodicStatusReport.getServerStatus(staticConfig, dynamicConfig)
                    if statusReport is not None: notifications.append(statusReport)

                    if len(notifications) > 0:
                        logging.info(f'Sending {len(notifications)} notifications via e-mail.')
                        emailNotification.sendMail(staticConfig, notifications)

                    logging.info('Checking for shutdown')
                    shutdown.shutdownOnInactivity(staticConfig)
                else:
                    if not staticConfig.isValid():
                        logging.error(f'The config file {staticConfigFile} could not be found.')
                    if not dynamicConfig.isValid():
                        logging.error(f'The config file {dynamicConfigFile} could not be found.')

        except Exception as e:
            logging.exception(f'Error occurred: {e}')
            
