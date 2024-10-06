import unittest
import periodicStatusReport
from tests.testConfiguration import TestConfiguration
from datetime import datetime
from datetime import datetime, timedelta
import periodicStatusReport
from notification.notification import Notification, Severity

class ServerStatusTests(unittest.TestCase):
    format = '%Y-%m-%d %H:%M:%S'

    def _getConfigs(self, hoursSinceLastReport):
        staticKeyValuePairs = {}
        staticKeyValuePairs['backup|numberofvolumes'] = 1
        staticKeyValuePairs['backupVolume0|filesystem'] = '/mnt/fs1'
        staticKeyValuePairs['backupVolume0|subvolume'] = 'mnt/fs1/subvol0'

        dynamicKeyValuePairs = {}
        timestamp = datetime.now() - timedelta(hours=hoursSinceLastReport)
        timestampString = timestamp.strftime(self.format)
        dynamicKeyValuePairs['periodicStatusReport|lastReport'] = timestampString

        staticConfig = TestConfiguration(staticKeyValuePairs)
        dynamicConfig = TestConfiguration(dynamicKeyValuePairs)

        return (staticConfig, dynamicConfig)

    def testNoLoggingIfIntervalNotYetOver(self):
        (staticConfig, dynamicConfig) = self._getConfigs(23)

        timestamp = dynamicConfig.get('periodicStatusReport', 'lastReport', None)

        report = periodicStatusReport.getServerStatus(staticConfig, dynamicConfig, datetime.now, lambda device: (0, ""))

        self.assertIsNone(report)
        self.assertEqual(dynamicConfig.get('periodicStatusReport', 'lastReport', None), timestamp)

    def testLoggingIfIntervalIsOver(self):
        (staticConfig, dynamicConfig) = self._getConfigs(25)

        report = periodicStatusReport.getServerStatus(staticConfig, dynamicConfig, datetime.now, lambda device: (0, ""))

        self.assertIs(type(report), Notification)
        self.assertEqual(report.severity, Severity.INFO)
        newTimestamp = datetime.strptime(dynamicConfig.get('periodicStatusReport', 'lastReport', None), self.format)

        self.assertTrue((datetime.now() - newTimestamp).total_seconds() < 10)

    def testErrorNotificationOnErrorDuringUsageRetrieval(self):
        (staticConfig, dynamicConfig) = self._getConfigs(25)

        report = periodicStatusReport.getServerStatus(staticConfig, dynamicConfig, datetime.now, lambda device: (1, "Unknown error"))

        self.assertEqual(report.severity, Severity.ERROR)
