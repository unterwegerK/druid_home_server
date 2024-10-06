from tests.mocks import TestChecking, TestScrubbing, TestSender, TestSnapshotting

class IntegrationTestFactory:
    def __init__(self, currentTime, scrubbingOutputs, checkOutputs, existingSnapshots, userSessions="", networkTraffic=0):
        self.currentTime = currentTime
        self.scrubbingOutputs = scrubbingOutputs
        self.checkOutputs = checkOutputs
        self.existingSnapshots = existingSnapshots
        self.eMailSender = TestSender()
        self.userSessions = userSessions
        self.networkTraffic = networkTraffic

    def getFilesystemScrubbing(self):
        return TestScrubbing(self.scrubbingOutputs)
    
    def getFilesystemChecking(self):
        return TestChecking(self.checkOutputs)
    
    def getCurrentTimeCallable(self):
        return self.currentTime
    
    def getPackageUpdater(self):
        return lambda: (1, 'Package update failed due to reasons')
                               
    def getSnapshotting(self, fileSystem, subvolume, snapshotsDirectory):
        return TestSnapshotting(fileSystem, subvolume, snapshotsDirectory, self.existingSnapshots.get(subvolume) or [])
    
    def getFileSystemUsageCallable(self):
        return lambda device: (0, "")
    
    def getEMailSender(self):
        return self.eMailSender
    
    def getUserSessionsCallable(self):
        return lambda: (0, self.userSessions)
    
    def getNetworkTrafficCallable(self):
        return lambda interface: self.networkTraffic
    
    def getShutdownCallable(self):
        return lambda: 0