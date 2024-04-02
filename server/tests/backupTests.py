import unittest

import backup
import logging
from tests.testConfiguration import TestConfiguration
from datetime import datetime
import sys

class CreateSnapshotSpy:
    def createSnapshot(self, subvolume, snapshotDirectory):
        self.snapshotDirectory = snapshotDirectory
        return (0, 'Output')

class BackupTests(unittest.TestCase):

    def testCreateSnapshotsSuccessfully(self):
        testee = backup.Backup()
        spy = CreateSnapshotSpy()
        result = testee.takeSnapshot('/media/testdata/subvolume', '/media/testdata/snapshots', lambda:datetime(2020, 10, 1, 15, 34, 26), spy.createSnapshot)
        self.assertEqual(result, 'Output')
        self.assertEqual(str(spy.snapshotDirectory), '/media/testdata/snapshots/2020-10-01_15:34:26')

    def testCreateSnapshotsError(self):
        logging.disable('ERROR')
        testee = backup.Backup()
        result = testee.takeSnapshot('/media/testdata/subvolume', '/media/testdata/snapshots', lambda:datetime(2020,10,1, 15, 34, 26), lambda subvolume,snapshotsDir:(1, 'Output'))
        self.assertTrue('Error' in result)
        self.assertTrue('Output' in result)
    
    def testGetSnapshots(self):
        testee = backup.Backup()
        subvolumeList='''ID 123 gen 456 top level 1 path data0
        ID 789 gen 10 top level 2 path data1
        ID 11 gen 12 top level 3 path snapshots/2020-10-01_15:34:26
        ID 13 gen 14 top level 4 path snapshots/2022-01-10_00:01:02'''
        snapshots = list(testee.getSnapshots('/media/testdata', '/media/testdata/snapshots', lambda fs:subvolumeList.splitlines()))
        self.assertEqual(len(snapshots), 2)
        self.assertEqual(str(snapshots[0][0]), '/media/testdata/snapshots/2020-10-01_15:34:26')
        self.assertEqual(snapshots[0][1], datetime(2020, 10, 1, 15, 34, 26))
        self.assertEqual(str(snapshots[1][0]), '/media/testdata/snapshots/2022-01-10_00:01:02')
        self.assertEqual(snapshots[1][1], datetime(2022, 1, 10, 0, 1, 2))

    def testGetObsoleteSnapshotsOnlyFirstYear(self):
        testee = backup.Backup()
        snapshots = [
            ('2020-01-01_00:00:00', datetime(2020, 1, 1)),
            ('2020-02-01_00:00:00', datetime(2020, 2, 1)),
            ('2021-01-01_00:00:00', datetime(2021, 1, 1)),
            ('2021-02-01_00:00:00', datetime(2021, 2, 1)),
            ('2022-01-01_00:00:00', datetime(2022, 1, 1)),
            ('2022-02-01_00:00:00', datetime(2022, 2, 1))
        ]

        obsoleteSnapshots = list(testee.getObsoleteSnapshots(snapshots, 2, 0, 0, lambda: datetime(2022, 2, 1)))
        self.assertEqual(len(obsoleteSnapshots), 4)
        self.assertEqual(obsoleteSnapshots[0][1], datetime(2020, 1, 1))
        self.assertEqual(obsoleteSnapshots[1][1], datetime(2020, 2, 1))
        self.assertEqual(obsoleteSnapshots[2][1], datetime(2021, 2, 1))
        self.assertEqual(obsoleteSnapshots[3][1], datetime(2022, 2, 1))

    def testGetObsoleteSnapshotsDueToMonthInSameYear(self):    
        testee = backup.Backup()
        snapshots = [
            ('2020-01-01_00:00:00', datetime(2020, 1, 1)),
            ('2020-02-01_00:00:00', datetime(2020, 2, 1)),
            ('2020-03-01_00:00:00', datetime(2020, 3, 1)),
            ('2020-04-01_00:00:00', datetime(2020, 4, 1)),
        ]

        obsoleteSnapshots = list(testee.getObsoleteSnapshots(snapshots, 0, 4, 0, lambda: datetime(2020, 5, 1)))
        self.assertEqual(len(obsoleteSnapshots), 1)
        self.assertEqual(obsoleteSnapshots[0][1], datetime(2020, 1, 1))

    def testGetObsoleteSnapshotsDueToMonthInPreviousYear(self):    
        testee = backup.Backup()
        snapshots = [
            ('2020-11-01_00:00:00', datetime(2020, 11, 1)),
            ('2020-12-01_00:00:00', datetime(2020, 12, 1)),
            ('2021-01-01_00:00:00', datetime(2021, 1, 1)),
            ('2021-02-01_00:00:00', datetime(2021, 2, 1)),
        ]

        obsoleteSnapshots = list(testee.getObsoleteSnapshots(snapshots, 0, 3, 0, lambda: datetime(2021, 2, 1)))
        self.assertEqual(len(obsoleteSnapshots), 1)
        self.assertEqual(obsoleteSnapshots[0][1], datetime(2020, 11, 1))

    def testGetObsoleteSnapshotsDueToMonthInSeveralPreviousYears(self):    
        testee = backup.Backup()
        snapshots = [
            ('2019-11-01_00:00:00', datetime(2019, 11, 1)),
            ('2019-12-01_00:00:00', datetime(2019, 12, 1)),
            ('2020-01-01_00:00:00', datetime(2020, 1, 1)),
            ('2020-11-01_00:00:00', datetime(2020, 11, 1)),
            ('2020-12-01_00:00:00', datetime(2020, 12, 1)),
            ('2021-01-01_00:00:00', datetime(2021, 1, 1)),
        ]

        obsoleteSnapshots = list(testee.getObsoleteSnapshots(snapshots, 0, 14, 0, lambda: datetime(2021, 1, 1)))
        self.assertEqual(len(obsoleteSnapshots), 1)
        self.assertEqual(obsoleteSnapshots[0][1], datetime(2019, 11, 1))

    def testGetObsoleteSnapshotsDueToDaysInSameMonth(self):    
        testee = backup.Backup()
        snapshots = [
            ('2019-11-11_00:00:00', datetime(2019, 11, 11)),
            ('2019-11-11_20:00:00', datetime(2019, 11, 11, 20)), #Test partial days
            ('2019-11-12_00:00:00', datetime(2019, 11, 12)),
            ('2019-11-13_00:00:00', datetime(2019, 11, 13)),
        ]

        obsoleteSnapshots = list(testee.getObsoleteSnapshots(snapshots, 0, 0, 2, lambda: datetime(2019, 11, 13)))
        self.assertEqual(len(obsoleteSnapshots), 2)
        self.assertEqual(obsoleteSnapshots[0][1], datetime(2019, 11, 11))
        self.assertEqual(obsoleteSnapshots[1][1], datetime(2019, 11, 11, 20))

    def testGetObsoleteSnapshotsDueToDaysInPreviousMonth(self):    
        testee = backup.Backup()
        snapshots = [
            ('2019-10-30_00:00:00', datetime(2019, 10, 30)),
            ('2019-10-30_20:00:00', datetime(2019, 10, 30, 20)), #Test partial days
            ('2019-10-31_00:00:00', datetime(2019, 10, 31)),
            ('2019-11-01_00:00:00', datetime(2019, 11, 11)),
            ('2019-11-02_00:00:00', datetime(2019, 11, 2)),
        ]

        obsoleteSnapshots = list(testee.getObsoleteSnapshots(snapshots, 0, 0, 3, lambda: datetime(2019, 11, 2)))
        self.assertEqual(len(obsoleteSnapshots), 2)
        self.assertEqual(obsoleteSnapshots[0][1], datetime(2019, 10, 30))
        self.assertEqual(obsoleteSnapshots[1][1], datetime(2019, 10, 30, 20))

    def testGetObsoleteSnapshotsDueToDaysKeepAllInDays(self):    
        testee = backup.Backup()
        snapshots = [
            ('2019-11-11_00:00:00', datetime(2019, 11, 11)),
            ('2019-11-12_00:00:00', datetime(2019, 11, 12)),
            ('2019-11-12_00:00:01', datetime(2019, 11, 12, 0, 0, 1)),
            ('2019-11-12_23:59:59', datetime(2019, 11, 12, 23, 59, 59)),
        ]

        obsoleteSnapshots = list(testee.getObsoleteSnapshots(snapshots, 0, 0, 2, lambda: datetime(2019, 11, 13)))
        self.assertEqual(len(obsoleteSnapshots), 1)
        self.assertEqual(obsoleteSnapshots[0][1], datetime(2019, 11, 11))


    def testGetObsoleteSnapshotsDueToDaysInPreviousMonthsAndYear(self):    
        testee = backup.Backup()
        snapshots = [
            ('2019-12-30_00:00:00', datetime(2019, 12, 30)),
            ('2019-12-30_20:00:00', datetime(2019, 12, 30, 20)), #Test partial days
            ('2019-12-31_00:00:00', datetime(2019, 12, 31)),
            ('2020-01-01_00:00:00', datetime(2020, 1, 1)),
            ('2020-01-02_00:00:00', datetime(2020, 1, 2)),
            ('2020-02-01_00:00:00', datetime(2020, 2, 1)),
        ]

        obsoleteSnapshots = list(testee.getObsoleteSnapshots(snapshots, 0, 0, 33, lambda: datetime(2020, 2, 1)))
        self.assertEqual(len(obsoleteSnapshots), 2)
        self.assertEqual(obsoleteSnapshots[0][1], datetime(2019, 12, 30))
        self.assertEqual(obsoleteSnapshots[1][1], datetime(2019, 12, 30, 20))

        obsoleteSnapshots = list(testee.getObsoleteSnapshots(snapshots, 0, 0, 31, lambda: datetime(2020, 2, 1)))
        self.assertEqual(len(obsoleteSnapshots), 4)
        self.assertEqual(obsoleteSnapshots[0][1], datetime(2019, 12, 30))
        self.assertEqual(obsoleteSnapshots[1][1], datetime(2019, 12, 30, 20))
        self.assertEqual(obsoleteSnapshots[2][1], datetime(2019, 12, 31))
        self.assertEqual(obsoleteSnapshots[3][1], datetime(2020, 1, 1))

    def testGetObsoleteSnapshotsDueToYearMonthAndDay(self):    
        testee = backup.Backup()
        snapshots = [
        #2019-10-01
        #2019-11-05 <- obsolete
        #2019-12-01
        #2019-12-31 <- obsolete
        #2020-01-01
        #2020-02-01
        #2020-02-02 <- obsolete
        #2020-03-01
        #2020-03-02 <- obsolete
        #2020-03-03 <- obsolete
        #2020-03-04
        #2020-03-05
        #2020-03-06
            ('2019-10-01_19:15:41', datetime(2019, 10, 1)),
            ('2019-11-05_20:01:01', datetime(2019, 11, 5)),
            ('2019-12-01_19:15:41', datetime(2019, 12, 1)),
            ('2019-12-31_19:15:41', datetime(2019, 12, 31)),
            ('2020-01-01_01:02:03', datetime(2020, 1, 1)),
            ('2020-02-01_04:05:06', datetime(2020, 2, 1)),
            ('2020-02-02_07:08:09', datetime(2020, 2, 2)),
            ('2020-03-01_10:11:12', datetime(2020, 3, 1)),
            ('2020-03-02_13:14:15', datetime(2020, 3, 2)),
            ('2020-03-03_16:17:18', datetime(2020, 3, 3)),
            ('2020-03-04_19:20:21', datetime(2020, 3, 4)),
            ('2020-03-05_22:23:24', datetime(2020, 3, 5)),
            ('2020-03-06_10:11:12', datetime(2020, 3, 6)),
        ]

        obsoleteSnapshots = list(testee.getObsoleteSnapshots(snapshots, sys.maxsize, 4, 28, lambda: datetime(2020, 3, 31)))
        self.assertEqual(len(obsoleteSnapshots), 5)
        self.assertEqual(obsoleteSnapshots[0][1], datetime(2019, 11, 5))
        self.assertEqual(obsoleteSnapshots[1][1], datetime(2019, 12, 31))
        self.assertEqual(obsoleteSnapshots[2][1], datetime(2020, 2, 2))
        self.assertEqual(obsoleteSnapshots[3][1], datetime(2020, 3, 2))
        self.assertEqual(obsoleteSnapshots[4][1], datetime(2020, 3, 3))

