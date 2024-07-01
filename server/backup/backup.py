from periodicTaskConfiguration import PeriodicTaskConfiguration
from backup import backupConfigurationParser
from datetime import datetime
from notification import Notification, Severity

def updateSnapshots(staticConfiguration, dynamicConfiguration):

    backupVolumes = backupConfigurationParser.getBackupVolumes(staticConfiguration, dynamicConfiguration)

    notifications = []
    for backupVolume in backupVolumes:
        with PeriodicTaskConfiguration(backupVolume[2], 'lastBackup', 24 * 60 * 60) as periodicBackup:
            if periodicBackup.periodicTaskIsDue:
                fileSystem = backupVolume[0]
                obsoleteSnapshotsDetermination = backupVolume[1]

                currentTime = datetime.now()

                createMessage = fileSystem.createSubvolumeSnapshot(currentTime)

                obsoleteSnapshots = obsoleteSnapshotsDetermination.getObsoleteSnapshots(fileSystem.getSubvolumeSnapshots(), currentTime)
                deleteMessages = fileSystem.deleteSubvolumeSnapshots(obsoleteSnapshots)
                notifications.append(Notification('Snapshot Update', f'The following snapshot changes have been made:\n{createMessage}\n{deleteMessages}', Severity.INFO))
            
    return notifications



