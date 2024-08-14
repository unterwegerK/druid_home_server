from configuration import DynamicSection, StaticSection
from backup.btrfsSnapshotting import BtrfsSnapshotting
from backup.obsoleteSnapshotDetermination import ObsoleteSnapshotDetermination

def getBackupVolumes(staticConfiguration, dynamicConfiguration, snapshottingFactory):
    numberOfVolumes = int(staticConfiguration.get('backup', 'numberofvolumes', 0))

    for i in range(numberOfVolumes):
        staticSection = StaticSection(staticConfiguration, 'backupVolume' + str(i))
        dynamicSection = DynamicSection(dynamicConfiguration, 'backupVolume' + str(i))

        fileSystem = staticSection.get('filesystem', None)
        if fileSystem is None:
            errorMessage = f'Key filesystem must be defined in Section {staticSection.sectionName}'
            raise Exception(errorMessage)

        subvolume = staticSection.get('subvolume', None)
        if subvolume is None:
            errorMessage = f'Key subvolume must be defined in Section {staticSection.sectionName}'
            raise Exception(errorMessage)

        snapshotsDirectory = staticSection.get('snapshotsdirectory', None)
        if snapshotsDirectory is None:
            errorMessage = f'Key snapshotsdirectory must be defined in Section {staticSection.sectionName}'
            raise Exception(errorMessage)

        yearsToKeep = staticSection.getint('yearstokeep', None)
        if yearsToKeep is None:
            errorMessage = f'Key yearstokeep must be defined in Section {staticSection.sectionName}'
            raise Exception(errorMessage)

        monthsToKeep = staticSection.getint('monthstokeep', None)
        if monthsToKeep is None:
            errorMessage = f'Key monthstokeep must be defined in Section {staticSection.sectionName}'
            raise Exception(errorMessage)

        daysToKeep = staticSection.getint('daystokeep', None)
        if daysToKeep is None:
            errorMessage = f'Key daystokeep must be defined in Section {staticSection.sectionName}'
            raise Exception(errorMessage)

        yield (snapshottingFactory.getSnapshotting(fileSystem, subvolume, snapshotsDirectory),
                ObsoleteSnapshotDetermination(yearsToKeep, monthsToKeep, daysToKeep),
                dynamicSection)



