from configuration import Section
from backup.btrfsSnapshotting import BtrfsSnapshotting
from backup.obsoleteSnapshotDetermination import ObsoleteSnapshotDetermination

def getBackupVolumes(configuration):
    numberOfVolumes = int(configuration.get('backup', 'numberofvolumes', 0))

    for i in range(numberOfVolumes):
        configurationSection = Section(configuration, 'backupVolume' + str(i))

        fileSystem = configurationSection.get('filesystem', None)
        if fileSystem is None:
            errorMessage = f'Key filesystem must be defined in Section {configurationSection.sectionName}'
            raise Exception(errorMessage)

        subvolume = configurationSection.get('subvolume', None)
        if subvolume is None:
            errorMessage = f'Key subvolume must be defined in Section {configurationSection.sectionName}'
            raise Exception(errorMessage)

        snapshotsDirectory = configurationSection.get('snapshotsdirectory', None)
        if snapshotsDirectory is None:
            errorMessage = f'Key snapshotsdirectory must be defined in Section {configurationSection.sectionName}'
            raise Exception(errorMessage)

        yearsToKeep = configurationSection.getint('yearstokeep', None)
        if yearsToKeep is None:
            errorMessage = f'Key yearstokeep must be defined in Section {configurationSection.sectionName}'
            raise Exception(errorMessage)

        monthsToKeep = configurationSection.getint('monthstokeep', None)
        if monthsToKeep is None:
            errorMessage = f'Key monthstokeep must be defined in Section {configurationSection.sectionName}'
            raise Exception(errorMessage)

        daysToKeep = configurationSection.getint('daystokeep', None)
        if daysToKeep is None:
            errorMessage = f'Key daystokeep must be defined in Section {configurationSection.sectionName}'
            raise Exception(errorMessage)

        yield (BtrfsSnapshotting(fileSystem, subvolume, snapshotsDirectory),
                ObsoleteSnapshotDetermination(yearsToKeep, monthsToKeep, daysToKeep),
                configurationSection)



