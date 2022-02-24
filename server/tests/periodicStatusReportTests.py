import unittest

import periodicStatusReport
from tests.testConfiguration import TestConfiguration
from datetime import datetime

class ServerStatusTests(unittest.TestCase):
    def testStatusReport(self):
       config = TestConfiguration({})
       report = periodicStatusReport.getServerStatus(config, lambda: datetime(2022, 2, 18, 8, 57, 0))
       self.assertIsNotNone(report)
