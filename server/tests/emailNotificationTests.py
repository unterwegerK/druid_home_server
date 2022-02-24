import unittest
import socket

from tests.testConfiguration import TestConfiguration
import emailNotification

class EMailNotificationTests(unittest.TestCase):
    def test(self):
        config = TestConfiguration(
        {
            'emailNotification|user': 'testuser', 
            'emailNotification|password': 'password',
            'emailNotification|smtpServer':'testserver',
            'emailNotification|receivers':'unknownreceivers'
        })
        self.assertRaises(socket.gaierror, lambda:emailNotification.sendMail(config, ['Notification1']))
