import unittest
from backup.btrfsSnapshotting import BtrfsSnapshotting
from datetime import datetime
import logging

class RunProcessSpy:
    def __init__(self, exitcode=0, output='Output'):
        self.exitcode = exitcode
        self.output = output

    def runProcess(self, command):
        self.command = command
        return (self.exitcode, self.output)
    
class BtrfsSnapshottingTests(unittest.TestCase):
    def testCreateSnapshotsSuccessfully(self):
        spy = RunProcessSpy()
        testee = BtrfsSnapshotting('/media/testdata', '/media/testdata/data', '/media/testdata/snapshots', spy.runProcess)
        result = testee.createSubvolumeSnapshot(lambda: datetime(2020, 10, 1, 15, 34, 26))
        self.assertEqual(result, 'Output')
        self.assertEqual(str(spy.command), 'btrfs subvolume snapshot /media/testdata/data /media/testdata/snapshots/2020-10-01_15:34:26')

    def testCreateSnapshotsError(self):
        logging.disable('ERROR')
        spy = RunProcessSpy(1, 'Output')
        testee = BtrfsSnapshotting('/media/testdata', '/media/testdata/data', '/media/testdata/snapshots', spy.runProcess)
        result = testee.createSubvolumeSnapshot(lambda: datetime(2020,10,1, 15, 34, 26))
        self.assertTrue('Error' in result)
        self.assertTrue('Output' in result)
    
    def testGetSnapshots(self):
        subvolumeList='''ID 123 gen 456 top level 1 path data0
        ID 789 gen 10 top level 2 path data1
        ID 11 gen 12 top level 3 path snapshots/2020-10-01_15:34:26
        ID 13 gen 14 top level 4 path snapshots/2022-01-10_00:01:02'''
        spy = RunProcessSpy(0, subvolumeList)
        testee = BtrfsSnapshotting('/media/testdata', '/media/testdata/data', '/media/testdata/snapshots', spy.runProcess)
        
        snapshots = list(testee.getSubvolumeSnapshots())
        self.assertEqual(len(snapshots), 2)
        self.assertEqual(str(snapshots[0][0]), '/media/testdata/snapshots/2020-10-01_15:34:26')
        self.assertEqual(snapshots[0][1], datetime(2020, 10, 1, 15, 34, 26))
        self.assertEqual(str(snapshots[1][0]), '/media/testdata/snapshots/2022-01-10_00:01:02')
        self.assertEqual(snapshots[1][1], datetime(2022, 1, 10, 0, 1, 2))