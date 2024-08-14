from datetime import datetime
import unittest
import druidServer
from tests.integration.integrationTestFactory import IntegrationTestFactory
from tests.integration.stringBasedDynamicConfiguration import StringBasedDynamicConfiguration
from tests.integration.stringBasedStaticConfiguration import StringBasedStaticConfiguration

#This tests one iteration of checks on two backup volumes (/mnt/fs0/data and /mnt/fs1/data) with the following expected results
#
# - For both volumes a new snapshot is created
# - For fs0 one snapshot is removed due to daystokeep
# - For fs1 three snapshots are removed. One each due to daystokeep, monthstokeep, and yearstokeep
# - Scrubbing fails on fs0
# - Check fails on fs1
# - Package update fails

class IntegrationTests(unittest.TestCase):
    def testPerformUpdates(self):
        staticConfigurationContent = '''
    [backup]
    numberofvolumes=2

    [backupVolume0]
    filesystem=/mnt/fs0
    subvolume=/mnt/fs0/data
    snapshotsdirectory=/mnt/fs0/snapshots
    yearstokeep=1234
    monthstokeep=120
    daystokeep=365

    [backupVolume1]
    filesystem=/mnt/fs1
    subvolume=/mnt/fs1/data
    snapshotsdirectory=/mnt/fs1/snapshots
    yearstokeep=1
    monthstokeep=2
    daystokeep=12

    [dataConsistency]
    suspendCommand=suspend.sh

    [emailNotification]
    smtpserver=smtp.mail.invalid
    user=invalidUser
    password=myInvalidPassword
    serverdisplayname=druidServer
    receivers=tobenotified@mail.invalid

    [shutdownOnInactivity]
    networkInterface=eth0
    '''

        dynamicConfigurationContent = '''
    [backupVolume0]
    lastbackup=2021-12-30 22:15:47

    [backupVolume1]
    lastbackup=2021-12-25 21:17:45

    [dataConsistency]
    lastScrub=2021-11-30 23:59:59
    lastCheck=2021-10-23 01:01:01
    '''

        staticConfiguration = StringBasedStaticConfiguration(staticConfigurationContent)
        dynamicConfiguration = StringBasedDynamicConfiguration(dynamicConfigurationContent)
        
        factory = IntegrationTestFactory(
            currentTime=lambda: datetime(2022, 1, 1, 1, 5, 0),
            scrubbingOutputs={
                '/mnt/fs0': """UUID:             xxxxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxx
                                     Scrub started:    Sat Aug 10 22:22:14 2024
                                     Status:           aborted
                                     Duration:         0:00:10
                                     Time left:        0:38:01
                                     ETA:              Sat Aug 10 23:00:30 2024
                                     Total to scrub:   10.25GiB
                                     Bytes scrubbed:   48.78MiB  (0.44%)
                                     Rate:             4.38MiB/s
                                     Error summary:    no errors found""",
                '/mnt/fs1': """UUID:             xxxxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxx
                                     Scrub started:    Sat Aug 10 22:22:14 2024
                                     Status:           finished
                                     Duration:         0:00:10
                                     Time left:        0:38:01
                                     ETA:              Sat Aug 10 23:00:30 2024
                                     Total to scrub:   10.25GiB
                                     Bytes scrubbed:   48.78MiB  (0.44%)
                                     Rate:             4.38MiB/s
                                     Error summary:    no errors found"""
                },
            checkOutputs={
                '/mnt/fs0': 'found 567890 bytes used, no error found',
                '/mnt/fs1': 'error found'
                },
            existingSnapshots={
                '/mnt/fs0/data': [('/mnt/fs0/snapshots/2020-12-30 01:00:00', datetime(2020, 12, 30, 1, 0, 0)), 
                                  ('/mnt/fs0/snapshots/2020-12-31 01:00:00', datetime(2020, 12, 31, 1, 0, 0)),
                                  ('/mnt/fs0/snapshots/2021-12-30 01:00:00', datetime(2021, 12, 30, 1, 0, 0)), 
                                  ('/mnt/fs0/snapshots/2021-12-31 01:00:00', datetime(2021, 12, 31, 1, 0, 0))],
                '/mnt/fs1/data': [('/mnt/fs1/snapshots/2021-05-01 01:00:00', datetime(2021,  5,  1, 1, 0, 0)),
                                  ('/mnt/fs1/snapshots/2021-12-01 01:00:00', datetime(2021, 12,  1, 1, 0, 0)), 
                                  ('/mnt/fs1/snapshots/2021-12-02 01:00:00', datetime(2021, 12,  2, 1, 0, 0)),
                                  ('/mnt/fs1/snapshots/2021-12-21 01:00:00', datetime(2021, 12, 21, 1, 0, 0)), 
                                  ('/mnt/fs1/snapshots/2021-12-22 01:00:00', datetime(2021, 12, 22, 1, 0, 0))]})

        druidServer.performUpdates(staticConfiguration, dynamicConfiguration, factory)

        eMailContent = factory.eMailSender.sendEMails[0][-1]

        #Check backup
        #Fs0
        self.assertEqual(dynamicConfiguration.get("backupVolume0", "lastbackup", None), "2022-01-01 01:05:00")
        self.assertIn('Created snapshot /mnt/fs0/snapshots/2022-01-01 01:05:00', eMailContent)
        self.assertIn('Deleted snapshot /mnt/fs0/snapshots/2020-12-31 01:00:00', eMailContent)
        self.assertEqual(eMailContent.count('Deleted snapshot /mnt/fs0'), 1)

        #Fs1
        self.assertEqual(dynamicConfiguration.get("backupVolume1", "lastbackup", None), "2022-01-01 01:05:00")
        self.assertIn('Created snapshot /mnt/fs1/snapshots/2022-01-01 01:05:00', eMailContent)
        self.assertIn('Deleted snapshot /mnt/fs1/snapshots/2021-05-01 01:00:00', eMailContent)
        self.assertIn('Deleted snapshot /mnt/fs1/snapshots/2021-12-02 01:00:00', eMailContent)
        self.assertIn('Deleted snapshot /mnt/fs1/snapshots/2021-12-21 01:00:00', eMailContent)
        self.assertEqual(eMailContent.count('Deleted snapshot /mnt/fs1'), 3)

        #Check package update
        self.assertEqual(dynamicConfiguration.get("packageSystem", "lastupdate", None), "2022-01-01 01:05:00")
        self.assertIn('Error during package update', eMailContent)

        #Check data consistency
        self.assertEqual(dynamicConfiguration.get("dataConsistency", "lastScrub", None), "2022-01-01 01:05:00")
        self.assertEqual(dynamicConfiguration.get("dataConsistency", "lastCheck", None), "2022-01-01 01:05:00")

        #Scrub fails on Fs0
        self.assertIn('Scrubbing was aborted for file system /mnt/fs0 with the following output', eMailContent)
        self.assertNotIn('Scrubbing was aborted for file system /mnt/fs1 with the following output', eMailContent)

        #Check fails on Fs1
        self.assertNotIn('Btrfs check failed for device /mnt/fs0', eMailContent)
        self.assertIn('Btrfs check failed for device /mnt/fs1', eMailContent)
