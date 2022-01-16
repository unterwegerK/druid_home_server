#!/usr/bin/env python3
#starting point taken from https://askubuntu.com/questions/105536/tool-to-shutdown-system-when-there-is-no-network-traffic

import os, time, sys
import logging
from subprocess import getoutput

logFile = os.path.join('var', 'log', 'shutdownOnNetworkInteractivity.log')
logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO, handlers=[logging.FileHandler(logFile), logging.StreamHandler(sys.stdout)])

INTERVAL = 2
LONG_INTERVAL = 300
INTERFACE = 'enp1s0'
MINIMUM_SPEED = 15 #kB/s
SAMPLES = 5

def worker ():
    while True:
        try:
            time.sleep(LONG_INTERVAL)

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

            logging.info(f'who: {getoutput("who")}-----')

            # Calculate average speed from all retries
            averageSpeed = accumulatedSpeed / float(SAMPLES)
            logging.info(f'Average network traffic: {averageSpeed}kB/s')
                
            # If average speed is below minimum speed - suspend
            if averageSpeed < MINIMUM_SPEED:
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
    logging.info('Starting...')
    worker()
