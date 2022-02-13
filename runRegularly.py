#!/usr/bin/env python3
#Sends e-mail with boot log once a day
import configparser
import logging
from os import path
import sys

ITERATION_INTERVAL = 300

if __name__ == '__main__':
    scriptName = path.splitext(path.basename(__file__))[0]

    #Command-line arguments
    if len(sys.argv) > 1:
        configFile = sys.argv[1]
    else:
        raise Exception("Config-file path required.")

    config = configparser.ConfigParser()
    config.read_file(open(configFile))
    logFilePath = config.get(scriptName, 'logFilePath')

    logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO, handlers=[logging.FileHandler(logFilePath), logging.StreamHandler(sys.stdout)])

    logging.info('Starting...')

    while True:
        try:
            time.sleep(ITERATION_INTERVAL)

            #backup
            #scrubbing
            #send e-mail

            shutdownOnInactivity.worker(configfile)

        except Exception as e:
            logging.error(f'Error occurred: {e}')
            
