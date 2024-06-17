#!/usr/bin/env python3
#base for a cronjob that runs continously and performs regular actions
from backup import backup
from configuration import Configuration, Section
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
    if len(sys.argv) > 1:
        configFile = sys.argv[1]
    else:
        raise Exception('Config-file path required.')

    with Configuration(configFile) as config:
        logFilePath = config.get(scriptName, 'logFilePath', f'/var/log/{scriptName}.log')

    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO, handlers=[logging.FileHandler(logFilePath), logging.StreamHandler(sys.stdout)])

    logging.info('===========')
    logging.info('Starting...')

    while True:
        try:
            time.sleep(ITERATION_INTERVAL)

            with Configuration(configFile) as config:
                if config.isValid():
                    notifications = []

                    backupReport = backup.updateSnapshots(Section(config, 'backup'))
                    if backupReport is not None: notifications.append(backupReport)
        
                    updateReport = packageSystem.updatePackages(config)
                    if updateReport is not None: notifications.append(updateReport)
                    
                    consistencyReport = dataConsistency.verifyDataConsistency(config)
                    if consistencyReport is not None: notifications.append(consistencyReport)

                    statusReport = periodicStatusReport.getServerStatus(config)
                    if statusReport is not None: notifications.append(statusReport)

                    if len(notifications) > 0:
                        logging.info(f'Sending {len(notifications)} notifications via e-mail.')
                        emailNotification.sendMail(config, notifications)

                    shutdown.shutdownOnInactivity(config)

        except Exception as e:
            logging.exception(f'Error occurred: {e}')
            
