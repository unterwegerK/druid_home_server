
from datetime import datetime

from dataConsistency.btrfsChecking import BtrfsChecking
from dataConsistency.btrfsScrubbing import BtrfsScrubbing


class TestScrubbing:
    def __init__(self, outputs):
        self.outputs = outputs

    def startScrubbing(self, fileSystem):
        pass

    def getScrubStatus(self, fileSystem):
        if isinstance(self.outputs, dict):
            return self.outputs[fileSystem]
        else:
            return self.outputs
            
    def parseScrubOutput(self, scrubOutput):
        return BtrfsScrubbing().parseScrubOutput(scrubOutput)

class TestChecking():
    def __init__(self, outputs='found 1234567890 bytes used, no error found', exitcode=0):
        self.outputs = outputs
        self.exitcode = exitcode

    def suspend(self, suspendCommand):
        pass

    def checkDevice(self, device):
        if isinstance(self.outputs, dict):
            return (self.exitcode, self.outputs[device])
        else:
            return (self.exitcode, self.outputs)
    
    def containsErrors(self, output):
        return BtrfsChecking().containsErrors(output)
    
class TestSnapshotting:
    FORMAT = '%Y-%m-%d %H:%M:%S'
    def __init__(self, fileSystem, subvolume, snapshotsDirectory, existingSnapshots=[]):
        self.fileSystemRoot = fileSystem
        self.subvolume = subvolume
        self.snapshotsDirectory = snapshotsDirectory
        self.existingSnapshots = existingSnapshots

    def getSubvolumeSnapshots(self):
        return self.existingSnapshots
    
    def createSubvolumeSnapshot(self, currentTime):
        return f'Created snapshot {self.snapshotsDirectory}/{currentTime().strftime(self.FORMAT)}'
    
    def deleteSubvolumeSnapshots(self, obsoleteSnapshots):
        return (False, "\n".join(f"Deleted snapshot {s[0]}" for s in obsoleteSnapshots))
    
class TestSender:
    def __init__(self):
        self.sendEMails = []

    def sendEMail(self, smtpServerAddress, smtpUser, smtpPassword, receivers, subject, message):
        self.sendEMails.append((smtpServerAddress, smtpUser, smtpPassword, receivers, subject, message))