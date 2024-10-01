import unittest
import periodicStatusReport
from tests.testConfiguration import TestConfiguration
from datetime import datetime
from datetime import datetime, timedelta
import periodicStatusReport
from notification.notification import Notification

class ServerStatusTests(unittest.TestCase):
    def testStatusReport(self):
       staticConfig = TestConfiguration({})
       dynamicConfig = TestConfiguration({})
       report = periodicStatusReport.getServerStatus(staticConfig, dynamicConfig, lambda: datetime(2022, 2, 18, 8, 57, 0), lambda device: "")
       self.assertIsNotNone(report)

    def testNoLoggingIfIntervalNotYetOver(self):
        keyValuePairs = {}
        timestamp = datetime.now() - timedelta(hours=23)
        timestampString = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        keyValuePairs['periodicStatusReport|lastReport'] = timestampString
        
        staticConfig = TestConfiguration({})
        dynamicConfig = TestConfiguration(keyValuePairs)

        report = periodicStatusReport.getServerStatus(staticConfig, dynamicConfig, datetime.now, lambda device: "")

        self.assertIsNone(report)
        self.assertEqual(dynamicConfig.get('periodicStatusReport', 'lastReport', None), timestampString)

    def testLoggingIfIntervalIsOver(self):
        timeFormat = '%Y-%m-%d %H:%M:%S'
        keyValuePairs = {}
        timestamp = datetime.now() - timedelta(hours=25)
        timestampString = timestamp.strftime(timeFormat)
        keyValuePairs['periodicStatusReport|lastReport'] = timestampString
        
        staticConfig = TestConfiguration({})
        dynamicConfig = TestConfiguration(keyValuePairs)

        report = periodicStatusReport.getServerStatus(staticConfig, dynamicConfig, datetime.now, lambda device: "")

        self.assertIs(type(report), Notification)
        newTimestamp = datetime.strptime(dynamicConfig.get('periodicStatusReport', 'lastReport', None), timeFormat)

        self.assertTrue((datetime.now() - newTimestamp).total_seconds() < 10)
