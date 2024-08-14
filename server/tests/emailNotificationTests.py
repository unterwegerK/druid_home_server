import unittest
from tests.mocks import TestSender
from tests.testConfiguration import TestConfiguration
import notification.emailNotification as emailNotification
from notification.notification import Notification, Severity

class EMailNotificationTests(unittest.TestCase):
    def testSocketError(self):
        config = TestConfiguration(
        {
            'emailNotification|user': 'testuser', 
            'emailNotification|password': 'password',
            'emailNotification|smtpServer':'testserver',
            'emailNotification|receivers':'unknownreceivers',
            'emailNotification|serverDisplayName':'druidServer'
        })

        sender = TestSender()
        emailNotification.sendMail(config, ['Notification1'], sender)
        self.assertEqual(len(sender.sendEMails), 1)
        self.assertEqual(sender.sendEMails[0][0], 'testserver')
        self.assertEqual(sender.sendEMails[0][1], 'testuser')
        self.assertEqual(sender.sendEMails[0][2], 'password')
        self.assertEqual(sender.sendEMails[0][3],'unknownreceivers')
        self.assertEqual(sender.sendEMails[0][4], 'Status of druidServer')

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
