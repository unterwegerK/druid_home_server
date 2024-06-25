#!/usr/bin/env python3
#base for a cronjob that runs continously and performs regular actions
from backup import backup
from configuration import StaticConfiguration, StaticSection, DynamicConfiguration, DynamicSection
import dataConsistency
import emailNotification
import packageSystem
import periodicStatusReport
import logging
from os import path
import sys
import shutdown
import time

ITERATION_INTERVAL = 300

if __name__ == '__main__':
    scriptName = path.splitext(path.basename(__file__))[0]

    #Command-line arguments
    if len(sys.argv) > 2:
        staticConfigFile = sys.argv[1]
        dynamicConfigFile = sys.argv[2]
    else:
        raise Exception('Paths for static and dynamic configuration required.')

    with StaticConfiguration(staticConfigFile) as staticConfig:
        logFilePath = staticConfigFile.get(scriptName, 'logFilePath', f'/var/log/{scriptName}.log')

    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO, handlers=[logging.FileHandler(logFilePath), logging.StreamHandler(sys.stdout)])

    logging.info('===========')
    logging.info('Starting...')

    while True:
        try:
            time.sleep(ITERATION_INTERVAL)

            with StaticConfiguration(staticConfigFile) as staticConfig, DynamicConfiguration(dynamicConfigFile) as dynamicConfig:
                if staticConfigFile.isValid() and dynamicConfigFile.isValid():
                    notifications = []

                    backupReport = backup.updateSnapshots(staticConfig, dynamicConfig)
                    if backupReport is not None: notifications.append(backupReport)
        
                    updateReport = packageSystem.updatePackages(staticConfig, dynamicConfig)
                    if updateReport is not None: notifications.append(updateReport)
                    
                    consistencyReport = dataConsistency.verifyDataConsistency(staticConfig, dynamicConfig)
                    if consistencyReport is not None: notifications.append(consistencyReport)

                    statusReport = periodicStatusReport.getServerStatus(staticConfig, dynamicConfig)
                    if statusReport is not None: notifications.append(statusReport)

                    if len(notifications) > 0:
                        logging.info(f'Sending {len(notifications)} notifications via e-mail.')
                        emailNotification.sendMail(staticConfig, notifications)

                    shutdown.shutdownOnInactivity(staticConfig)

        except Exception as e:
            logging.exception(f'Error occurred: {e}')
            
