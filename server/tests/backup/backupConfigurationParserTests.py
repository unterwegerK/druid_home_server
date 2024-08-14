import unittest
from tests.mocks import TestSnapshotting
from tests.testConfiguration import TestConfiguration
from backup.backupConfigurationParser import getBackupVolumes


class TestSnapshottingFactory:
    def getSnapshotting(self, fileSystem, subvolume, snapshotsDirectory):
        return TestSnapshotting(fileSystem, subvolume, snapshotsDirectory)

class BackupTests(unittest.TestCase):

    def testParsingOfTwoVolumes(self):
        staticKvps = {}
        dynamicKvps = {}

        #Section backup
        staticKvps['backup|numberofvolumes'] = '2'

        #First backup volume
        staticKvps['backupVolume0|filesystem'] = '/media/data0'
        staticKvps['backupVolume0|subvolume'] = '/media/data0/subv'
        staticKvps['backupVolume0|snapshotsdirectory'] = '/media/data0/snapshots'
        staticKvps['backupVolume0|yearstokeep'] = '5'
        staticKvps['backupVolume0|monthstokeep'] = '12'
        staticKvps['backupVolume0|daystokeep'] = '31'
        dynamicKvps['backupVolume0|lastbackup'] = '1990-05-20 18:46:22'

        #Second backup volume
        staticKvps['backupVolume1|filesystem'] = '/media/data1'
        staticKvps['backupVolume1|subvolume'] = '/media/data1/subv'
        staticKvps['backupVolume1|snapshotsdirectory'] = '/media/data1/snapshots'
        staticKvps['backupVolume1|yearstokeep'] = '0'
        staticKvps['backupVolume1|monthstokeep'] = '24'
        staticKvps['backupVolume1|daystokeep'] = '64'
        dynamicKvps['backupVolume1|lastbackup'] = '1999-12-31 23:59:59'

        staticConfiguration = TestConfiguration(staticKvps)
        dynamicConfiguration = TestConfiguration(dynamicKvps)

        backupVolumes = list(getBackupVolumes(staticConfiguration, dynamicConfiguration, TestSnapshottingFactory()))
        
        self.assertEqual(len(backupVolumes), 2)

        self.assertEqual(backupVolumes[0][0].fileSystemRoot, '/media/data0')
        self.assertEqual(backupVolumes[0][0].subvolume, '/media/data0/subv')
        self.assertEqual(backupVolumes[0][0].snapshotsDirectory, '/media/data0/snapshots')
        self.assertEqual(backupVolumes[0][1].yearsToKeep, 5)
        self.assertEqual(backupVolumes[0][1].monthsToKeep, 12)
        self.assertEqual(backupVolumes[0][1].daysToKeep, 31)

        self.assertEqual(backupVolumes[1][0].fileSystemRoot, '/media/data1')
        self.assertEqual(backupVolumes[1][0].subvolume, '/media/data1/subv')
        self.assertEqual(backupVolumes[1][0].snapshotsDirectory, '/media/data1/snapshots')
        self.assertEqual(backupVolumes[1][1].yearsToKeep, 0)
        self.assertEqual(backupVolumes[1][1].monthsToKeep, 24)
        self.assertEqual(backupVolumes[1][1].daysToKeep, 64)
