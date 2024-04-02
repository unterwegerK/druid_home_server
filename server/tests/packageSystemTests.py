import unittest

import logging
from tests.testConfiguration import TestConfiguration
from datetime import datetime
import packageSystem

class PackageSystemTests(unittest.TestCase):
    def testNoUpdateInInterval(self):
        config = TestConfiguration({'packageSystem|lastUpdate': '2022-01-01 00:00:00', 'packageSystem|interval': '3600'})
        result = packageSystem.updatePackages(config, lambda: datetime(2022, 1, 1, 0, 5, 0), lambda: (0, 'Output'))
        self.assertIsNone(result)

    def testUpdateAfterIntervalPassed(self):
        config = TestConfiguration({'packageSystem|lastUpdate': '2022-01-01 00:00:00', 'packageSystem|interval': '3600'})
        result = packageSystem.updatePackages(config, lambda: datetime(2022, 1, 1, 1, 5, 0), lambda: (0, 'Output'))
        self.assertTrue('Output' in result)

 
    def testErrorOutput(self):
        logging.disable('ERROR')
        config = TestConfiguration({'packageSystem|lastUpdate': '2022-01-01 00:00:00', 'packageSystem|interval': '3600'})
        result = packageSystem.updatePackages(config, lambda: datetime(2022, 1, 1, 1, 5, 0), lambda: (8, 'Output'))
        self.assertTrue('Error' in result)
        self.assertTrue('Output' in result)
