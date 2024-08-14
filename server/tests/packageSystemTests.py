import unittest

import logging
from tests.testConfiguration import TestConfiguration
from datetime import datetime
import packageSystem

class PackageSystemTests(unittest.TestCase):
    def testNoUpdateInInterval(self):
        staticConfiguration = TestConfiguration({'packageSystem|interval': '3600'})
        dynamicConfiguration = TestConfiguration({'packageSystem|lastUpdate': '2022-01-01 00:00:00'})
        result = packageSystem.updatePackages(staticConfiguration, dynamicConfiguration, lambda: (0, 'Output'), lambda: datetime(2022, 1, 1, 0, 5, 0))
        self.assertIsNone(result)

    def testUpdateAfterIntervalPassed(self):
        staticConfiguration = TestConfiguration({'packageSystem|interval': '3600'})
        dynamicConfiguration = TestConfiguration({'packageSystem|lastUpdate': '2022-01-01 00:00:00'})
        result = packageSystem.updatePackages(staticConfiguration, dynamicConfiguration, lambda: (0, 'Output'), lambda: datetime(2022, 1, 1, 1, 5, 0))
        self.assertTrue('Output' in result.message)

 
    def testErrorOutput(self):
        logging.disable('ERROR')
        staticConfiguration = TestConfiguration({'packageSystem|interval': '3600'})
        dynamicConfiguration = TestConfiguration({'packageSystem|lastUpdate': '2022-01-01 00:00:00'})
        result = packageSystem.updatePackages(staticConfiguration, dynamicConfiguration, lambda: (8, 'Output'), lambda: datetime(2022, 1, 1, 1, 5, 0))
        self.assertTrue('Error' in result.header)
        self.assertTrue('Output' in result.message)
