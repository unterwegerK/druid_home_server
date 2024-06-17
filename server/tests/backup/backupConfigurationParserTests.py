import unittest
from tests.testConfiguration import TestConfiguration
from backup.backupConfigurationParser import getBackupVolumes



class BackupTests(unittest.TestCase):

    def testParsingOfTwoVolumes(self):
        kvps = {}

        #Section backup
        kvps['backup|numberofvolumes'] = '2'

        #First backup volume
        kvps['backupVolume0|filesystem'] = '/media/data0'
        kvps['backupVolume0|subvolume'] = '/media/data0/subv'
        kvps['backupVolume0|snapshotsdirectory'] = '/media/data0/snapshots'
        kvps['backupVolume0|yearstokeep'] = '5'
        kvps['backupVolume0|monthstokeep'] = '12'
        kvps['backupVolume0|daystokeep'] = '31'
        kvps['backupVolume0|lastbackup'] = '1990-05-20 18:46:22'

        #Second backup volume
        kvps['backupVolume1|filesystem'] = '/media/data1'
        kvps['backupVolume1|subvolume'] = '/media/data1/subv'
        kvps['backupVolume1|snapshotsdirectory'] = '/media/data1/snapshots'
        kvps['backupVolume1|yearstokeep'] = '0'
        kvps['backupVolume1|monthstokeep'] = '24'
        kvps['backupVolume1|daystokeep'] = '64'
        kvps['backupVolume1|lastbackup'] = '1999-12-31 23:59:59'

        configuration = TestConfiguration(kvps)

        backupVolumes = list(getBackupVolumes(configuration))
        
        self.assertEquals(len(backupVolumes), 2)
        self.assertEquals(backupVolumes[0][0].fileSystemRoot, '/media/data0')
        self.assertEquals(backupVolumes[0][0].subvolume, '/media/data0/subv')
        self.assertEquals(backupVolumes[0][0].snapshotsDirectory, '/media/data0/snapshots')
        self.assertEquals(backupVolumes[0][1].yearsToKeep, 5)
        self.assertEquals(backupVolumes[0][1].monthsToKeep, 12)
        self.assertEquals(backupVolumes[0][1].daysToKeep, 31)

        self.assertEquals(backupVolumes[1][0].fileSystemRoot, '/media/data1')
        self.assertEquals(backupVolumes[1][0].subvolume, '/media/data1/subv')
        self.assertEquals(backupVolumes[1][0].snapshotsDirectory, '/media/data1/snapshots')
        self.assertEquals(backupVolumes[1][1].yearsToKeep, 0)
        self.assertEquals(backupVolumes[1][1].monthsToKeep, 24)
        self.assertEquals(backupVolumes[1][1].daysToKeep, 64)
