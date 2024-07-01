import unittest
import socket

from tests.testConfiguration import TestConfiguration
import emailNotification
from notification import Notification, Severity

class EMailNotificationTests(unittest.TestCase):
    def testSocketError(self):
        config = TestConfiguration(
        {
            'emailNotification|user': 'testuser', 
            'emailNotification|password': 'password',
            'emailNotification|smtpServer':'testserver',
            'emailNotification|receivers':'unknownreceivers'
        })
        self.assertRaises(socket.gaierror, lambda:emailNotification.sendMail(config, ['Notification1']))

    def testNotificationConcatenation(self):
        notifications = [
            'StringNotification1',
            Notification('ErrorHeader1', 'ErrorMessage1', Severity.ERROR),
            Notification('InfoHeader', 'InfoMessage', Severity.INFO),
            Notification('ErrorHeader2', 'ErrorMessage2', Severity.ERROR),
            'StringNotification2'
        ]

        expectedResult = \
"""ERROR: ErrorHeader1
ERROR: ErrorHeader2

==== ErrorHeader1 (ERROR) ====
ErrorMessage1

==== ErrorHeader2 (ERROR) ====
ErrorMessage2

==== InfoHeader (INFO) ====
InfoMessage

=====================
StringNotification1

=====================
StringNotification2
"""

        self.maxDiff = None
        self.assertEqual(emailNotification._concatenateNotifications(notifications), expectedResult)
