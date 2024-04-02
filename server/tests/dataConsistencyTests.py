import unittest

import dataConsistency
import logging
from tests.testConfiguration import TestConfiguration
from datetime import datetime

class DataConsistencyTests(unittest.TestCase):
    def testParseScrubOutput(self):
        output0 = '''UUID:             xyz
        Scrub started:    Sat Feb 19 10:48:15 2022
        Status:           running
        Duration:         0:04:05
        Time left:        15:48:21
        ETA:              Sun Feb 20 02:40:43 2022
        Total to scrub:   17.48TiB
        Bytes scrubbed:   76.73GiB  (0.43%)
        Rate:             320.69MiB/s
        Error summary:    no errors found'''
        self.assertEqual(dataConsistency._parseScrubOutput(output0), 'running')

        output1 = '''UUID:             xyz
        Scrub started:    Sat Feb 19 10:48:15 2022
        Status:           aborted
        Duration:         0:06:07
        Total to scrub:   17.48TiB
        Rate:             321.81MiB/s
        Error summary:    no errors found'''
        self.assertEqual(dataConsistency._parseScrubOutput(output1), 'aborted')

        output2 = '''UUID:             xyz
        Scrub started:    Tue Feb 22 14:46:08 2022
        Status:           finished
        Duration:         0:00:20
        Total to scrub:   3.34GiB
        Rate:             170.86MiB/s
        Error summary:    no errors found'''
        self.assertEqual(dataConsistency._parseScrubOutput(output2), 'finished')


    def testNoCheckConsistencyWithinInterval(self):
        config = TestConfiguration({'dataConsistency|fileSystem': '/mnt/testdata', 'dataConsistency|lastScrub': '2022-01-01 00:00:00', 'dataConsistency|interval': '3600'})
        result = dataConsistency.verifyDataConsistency(config, lambda: datetime(2022, 1, 1, 0, 5, 0), lambda fs: None, lambda fs: 'Status: finished')
        self.assertIsNone(result)

    def testCheckConsistencyAfterIntervalPassed(self):
        config = TestConfiguration({'dataConsistency|fileSystem': '/mnt/testdata', 'dataConsistency|lastScrub': '2022-01-01 00:00:00', 'dataConsistency|interval': '3600'})
        result = dataConsistency.verifyDataConsistency(config, lambda: datetime(2022, 1, 1, 1, 5, 0), lambda fs: None, lambda fs: 'Status: finished')
        self.assertTrue('finished' in result)

    def testErrorOnAbort(self):
        logging.disable('ERROR')
        config = TestConfiguration({'dataConsistency|fileSystem': '/mnt/testdata', 'dataConsistency|lastScrub': '2022-01-01 00:00:00', 'dataConsistency|interval': '3600'})
        result = dataConsistency.verifyDataConsistency(config, lambda: datetime(2022, 1, 1, 1, 5, 0), lambda fs: None, lambda fs: 'Status: aborted')
        self.assertTrue('aborted' in result)

    hours = 0
    def testTimeout(self):
        global hours
        hours = 0
        def getCurrentTime():
            global hours
            hours += 1
            return datetime(2022, 1, 2, hours, 0, 0)

        config = TestConfiguration({'dataConsistency|fileSystem': '/mnt/testdata', 'dataConsistency|lastScrub': '2022-01-01 00:00:00', 'dataConsistency|interval': '3600'})
        result = dataConsistency.verifyDataConsistency(config, getCurrentTime, lambda fs: None, lambda fs: 'Status: running')
        self.assertTrue('running' in result)

    def testErrorInScrubbing(self):
        logging.disable('ERROR')
        config = TestConfiguration({'dataConsistency|fileSystem': '/mnt/testdata', 'dataConsistency|lastScrub': '2022-01-01 00:00:00', 'dataConsistency|interval': '3600'})
        result = dataConsistency.verifyDataConsistency(config, lambda: datetime(2022, 1, 1, 1, 5, 0), lambda fs: None, lambda fs: '')
        self.assertTrue('Unknown status' in result)

        

