from periodicTaskConfiguration import PeriodicTaskConfiguration
from backup import backupConfigurationParser
from datetime import datetime

def updateSnapshots(configuration):

    backupVolumes = backupConfigurationParser.getBackupVolumes(configuration)

    for backupVolume in backupVolumes:
        with PeriodicTaskConfiguration(backupVolume[2], 'lastBackup', 24 * 60 * 60) as periodicBackup:
            if periodicBackup.periodicTaskIsDue:
                fileSystem = backupVolume[0]
                obsoleteSnapshotsDetermination = backupVolume[1]

                currentTime = datetime.now()

                createMessage = fileSystem.takeSnapshot(currentTime)

                obsoleteSnapshots = obsoleteSnapshotsDetermination.getObsoleteSnapshots(fileSystem.getSubvolumeSnapshots(), currentTime)
                deleteMessages = fileSystem.deleteSubvolumeSnapshots(obsoleteSnapshots)
                return f'The following snapshot changes have been made:\n{createMessage}\n{deleteMessages}'
            else:
                return None
            



