from periodicTaskConfiguration import PeriodicTaskConfiguration
from backup import backupConfigurationParser
from datetime import datetime
from notification.notification import Notification, Severity

def updateSnapshots(staticConfiguration, dynamicConfiguration, snapshottingFactory, currentTime):

    backupVolumes = backupConfigurationParser.getBackupVolumes(staticConfiguration, dynamicConfiguration, snapshottingFactory)

    notifications = []
    for backupVolume in backupVolumes:
        with PeriodicTaskConfiguration(backupVolume[2], 'lastBackup', 24 * 60 * 60, currentTime) as periodicBackup:
            if periodicBackup.periodicTaskIsDue:
                fileSystem = backupVolume[0]
                obsoleteSnapshotsDetermination = backupVolume[1]

                createMessage = fileSystem.createSubvolumeSnapshot(currentTime)

                obsoleteSnapshots = list(obsoleteSnapshotsDetermination.getObsoleteSnapshots(fileSystem.getSubvolumeSnapshots(), currentTime()))

                (errorOccurred, deleteMessages) = fileSystem.deleteSubvolumeSnapshots(obsoleteSnapshots)
                notifications.append(Notification('Snapshot Update', f'The following snapshot changes have been made:\n{createMessage}\n{deleteMessages}', Severity.ERROR if errorOccurred else Severity.INFO))
            
    return notifications



