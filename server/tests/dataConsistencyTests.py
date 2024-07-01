import unittest

import dataConsistency.dataConsistency as dataConsistency
from dataConsistency.btrfsScrubbing import BtrfsScrubbing
from dataConsistency.btrfsChecking import BtrfsChecking
import logging
from tests.testConfiguration import TestConfiguration
from datetime import datetime

class TestScrubbing:
    def __init__(self, output):
        self.output = output

    def startScrubbing(self, fileSystem):
        pass

    def getScrubStatus(self, fileSystem):
        return self.output
            
    def parseScrubOutput(self, scrubOutput):    
        return scrubOutput

class ScrubTests(unittest.TestCase):
    def testParseScrubOutput(self):
        testee = BtrfsScrubbing()
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
        self.assertEqual(testee.parseScrubOutput(output0), 'running')

        output1 = '''UUID:             xyz
        Scrub started:    Sat Feb 19 10:48:15 2022
        Status:           aborted
        Duration:         0:06:07
        Total to scrub:   17.48TiB
        Rate:             321.81MiB/s
        Error summary:    no errors found'''
        self.assertEqual(testee.parseScrubOutput(output1), 'aborted')

        output2 = '''UUID:             xyz
        Scrub started:    Tue Feb 22 14:46:08 2022
        Status:           finished
        Duration:         0:00:20
        Total to scrub:   3.34GiB
        Rate:             170.86MiB/s
        Error summary:    no errors found'''
        self.assertEqual(testee.parseScrubOutput(output2), 'finished')


    def testNoCheckConsistencyWithinInterval(self):
        staticConfig = TestConfiguration({'backup|numberofvolumes': '1', 'backupVolume0|filesystem': '/mnt/testdata', 'dataConsistency|scrubInterval': '3600'})
        dynamicConfig = TestConfiguration({'dataConsistency|lastScrub': '2022-01-01 00:00:00'})
        messages = dataConsistency._performScrubbings(staticConfig, dynamicConfig, TestScrubbing('Status: finished'), lambda: datetime(2022, 1, 1, 0, 5, 0), )
        self.assertTrue(len(messages) == 0, messages)

    def testCheckConsistencyAfterIntervalPassed(self):
        staticConfig = TestConfiguration({'backup|numberofvolumes': '1', 'backupVolume0|filesystem': '/mnt/testdata', 'dataConsistency|scrubInterval': '3600'})
        dynamicConfig = TestConfiguration({'dataConsistency|lastScrub': '2022-01-01 00:00:00'})
        messages = dataConsistency._performScrubbings(staticConfig, dynamicConfig, TestScrubbing('Status: finished'), lambda: datetime(2022, 1, 1, 1, 5, 0))
        self.assertIn('finished', messages[0])

    def testErrorOnAbort(self):
        logging.disable('ERROR')
        staticConfig = TestConfiguration({'backup|numberofvolumes': '1', 'backupVolume0|filesystem': '/mnt/testdata', 'dataConsistency|scrubInterval': '3600'})
        dynamicConfig = TestConfiguration({'dataConsistency|lastScrub': '2022-01-01 00:00:00'})
        messages = dataConsistency._performScrubbings(staticConfig, dynamicConfig, TestScrubbing('Status: aborted'), lambda: datetime(2022, 1, 1, 1, 5, 0), )
        self.assertIn('aborted', messages[0])

    hours = 0
    def testTimeout(self):
        global hours
        hours = 0
        def getCurrentTime():
            global hours
            hours += 1
            return datetime(2022, 1, 2, hours, 0, 0)

        staticConfig = TestConfiguration({'backup|numberofvolumes': '1', 'backupVolume0|filesystem': '/mnt/testdata', 'dataConsistency|scrubInterval': '3600'})
        dynamicConfig = TestConfiguration({'dataConsistency|lastScrub': '2022-01-01 00:00:00'})
        messages = dataConsistency._performScrubbings(staticConfig, dynamicConfig, TestScrubbing('Status: running'), getCurrentTime)
        self.assertIn('running', messages[0])

    def testErrorInScrubbing(self):
        logging.disable('ERROR')
        staticConfig = TestConfiguration({'backup|numberofvolumes': '1', 'backupVolume0|filesystem': '/mnt/testdata', 'dataConsistency|scrubInterval': '3600'})
        dynamicConfig = TestConfiguration({'dataConsistency|lastScrub': '2022-01-01 00:00:00'})
        messages = dataConsistency._performScrubbings(staticConfig, dynamicConfig, TestScrubbing(''), lambda: datetime(2022, 1, 1, 1, 5, 0))
        self.assertIn('Unknown status', messages[0])

        



class CheckTests(unittest.TestCase):
    def testParsingOutputWithoutError(self):
        output = '''Opening filesystem to check...
                    Checking filesystem on /dev/sdx4
                    UUID: 97775164-1c74-4930-86f8-e52e97bde5ef
                    [1/7] checking root items
                    [2/7] checking extents
                    [3/7] checking free space cache
                    [4/7] checking fs roots
                    [5/7] checking only csums items (without verifying data)
                    [6/7] checking root refs
                    [7/7] checking quota groups skipped (not enabled on this FS)
                    found 1234567890 bytes used, no error found
                    total csum bytes: 123450
                    total tree bytes: 1234561
                    total fs tree bytes: 1234562
                    total extent tree bytes: 1234563
                    btree space waste bytes: 1234564
                    file data blocks allocated: 12345678
                    referenced 1234567'''
        
        testee = BtrfsChecking()

        self.assertFalse(testee.containsError(output))


    def testParsingOutputWithError1(self):
        output = '''ERROR: errors found in fs roots
                    found 1234567890 bytes used, error(s) found
                    total csum bytes: 123450
                    total tree bytes: 123451
                    total fs tree bytes: 123452
                    total extent tree bytes: 123453
                    btree space waste bytes: 123454
                    file data blocks allocated: 12345678
                    referenced 1234567'''
        
        testee = BtrfsChecking()

        self.assertTrue(testee.containsError(output))

    def testParsingOutputWithError2(self):
        output = '''found 1234567890 bytes used, error(s) found
                    total csum bytes: 123450
                    total tree bytes: 123451
                    total fs tree bytes: 123452
                    total extent tree bytes: 123453
                    btree space waste bytes: 123454
                    file data blocks allocated: 12345678
                    referenced 1234567'''
        
        testee = BtrfsChecking()

        self.assertTrue(testee.containsError(output))

    def testParsingOutputWithError3(self):
        output = '''ERROR: errors found in fs roots
                    total csum bytes: 123450
                    total tree bytes: 123451
                    total fs tree bytes: 123452
                    total extent tree bytes: 123453
                    btree space waste bytes: 123454
                    file data blocks allocated: 12345678
                    referenced 1234567'''
        
        testee = BtrfsChecking()

        self.assertTrue(testee.containsError(output))

    def testParsingAmbigiousOutput(self):
        output = '''total csum bytes: 123450
                    total tree bytes: 123451
                    total fs tree bytes: 123452
                    total extent tree bytes: 123453
                    btree space waste bytes: 123454
                    file data blocks allocated: 12345678
                    referenced 1234567'''
        
        testee = BtrfsChecking()

        self.assertIsNone(testee.containsError(output))

