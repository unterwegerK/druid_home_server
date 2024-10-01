from subprocess import getstatusoutput, getoutput
from pathlib import Path
from datetime import datetime
import logging
import re

class BtrfsSnapshotting:    
    FORMAT = '%Y-%m-%d_%H:%M:%S'

    def __init__(self, fileSystemRoot, subvolume, snapshotsDirectory, runProcess = lambda command: getstatusoutput(command)):
        self.fileSystemRoot = fileSystemRoot
        self.subvolume = subvolume
        self.snapshotsDirectory = snapshotsDirectory
        self.runProcess = runProcess
    
    def getSubvolumeSnapshots(self):
        fileSystemPath = Path(self.fileSystemRoot)
        snapshotsDirectoryPath = Path(self.snapshotsDirectory)

        for line in self.runProcess(f'btrfs subvolume list {self.fileSystemRoot}')[1].splitlines():
            m = re.search(r'ID\s*[0-9]+\s*gen\s*[0-9]+\s*top\s*level\s*[0-9]+\s*path\s*(.+)', line)
            if m:
                subvolumePath = fileSystemPath / m.group(1)
                if snapshotsDirectoryPath in subvolumePath.parents:
                    timestamp = datetime.strptime(subvolumePath.name, self.FORMAT)
                    yield (subvolumePath, timestamp)
            else:
                logging.error(f'Could not parse subvolume line {line}')
    
    def createSubvolumeSnapshot(self, currentTime):
        timestamp = currentTime().strftime(self.FORMAT)
        snapshotsDirectory = Path(self.snapshotsDirectory) / timestamp
        (exitcode, output) = self.runProcess(f'btrfs subvolume snapshot {self.subvolume} {snapshotsDirectory}')

        if exitcode == 0:
            message = output
        else:
            message = f'Error while taking a snapshot of subvolume {self.subvolume} into directory {self.snapshotsDirectory}\n{output}'
            logging.error(message)
        return message

    def _deleteSubvolumeSnapshot(self, snapshotDirectory):
        return self.runProcess(f'btrfs subvolume delete {snapshotDirectory}')
    
    def deleteSubvolumeSnapshots(self, obsoleteSnapshots):
        messages = []
        for obsoleteSnapshot in obsoleteSnapshots:
            snapshotMessage = f'Deleting snapshot {obsoleteSnapshot[0]}'
            logging.info(snapshotMessage)
            messages.append(snapshotMessage)
            self._deleteSubvolumeSnapshot(obsoleteSnapshot[0])

        return '\n'.join(messages)

