#!/usr/bin/env python3
#base for a cronjob that runs continously and performs regular actions
from configuration import Configuration
import emailNotification
import logging
from os import path
import sys
import shutdownOnInactivity
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

    logging.info('Starting...')

    while True:
        try:
            time.sleep(ITERATION_INTERVAL)

            with Configuration(configFile) as config:
                if config.isValid():
                    notifications = []
                    #backup
                    #scrubbing
                    #daily notification

                    if len(notifications) > 0:
                        emailNotification.sendMail(config, notifications)

                    shutdownOnInactivity.worker(config)

        except Exception as e:
            logging.error(f'Error occurred: {e}')
            
