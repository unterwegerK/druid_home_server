import logging
from subprocess import getstatusoutput, getoutput
from datetime import datetime
from pathlib import Path
from periodicTaskConfiguration import PeriodicTaskConfiguration
import re

class Backup:
    FORMAT = '%Y-%m-%d_%H:%M:%S'

    def _createSubvolumeSnapshot(subvolume, snapshotDirectory):
        return getstatusoutput(f'btrfs subvolume snapshot {subvolume} {snapshotDirectory}')

    def takeSnapshot(self, subvolume, snapshotsDirectory, getCurrentTime=datetime.now, createSnapshot=_createSubvolumeSnapshot):
        timestamp = getCurrentTime().strftime(self.FORMAT)
        snapshotDirectory = Path(snapshotsDirectory) / timestamp
        (status, output) = createSnapshot(subvolume, snapshotDirectory)

        if status == 0:
            message = output
        else:
            message = f'Error while taking a snapshot of subvolume {subvolume} into directory {snapshotsDirectory}\n{output}'
            logging.error(message)
        return message

    def _getSubvolumeSnapshots(fileSystem):
        return getoutput(f'btrfs subvolume list {fileSystem}').splitlines()
    

    def getSnapshots(self, fileSystem, snapshotsDirectory, getSubvolumeSnapshots=_getSubvolumeSnapshots):
        fileSystemPath = Path(fileSystem)
        snapshotsDirectoryPath = Path(snapshotsDirectory)
        for line in getSubvolumeSnapshots(fileSystem):
            m = re.search(r'ID\s*[0-9]+\s*gen\s*[0-9]+\s*top\s*level\s*[0-9]+\s*path\s*(.+)', line)
            if m:
                subvolumePath = fileSystemPath / m.group(1)
                if snapshotsDirectoryPath in subvolumePath.parents:
                    timestamp = datetime.strptime(subvolumePath.name, self.FORMAT)
                    yield (subvolumePath, timestamp)
            else:
                logging.error(f'Could not parse subvolume line {line}')

    def getObsoleteSnapshots(self, snapshots, yearsToKeep, monthsToKeep, daysToKeep, getCurrentTime=datetime.now):
        snapshots = sorted(snapshots, key=lambda s:s[1])

        now = getCurrentTime()

        currentYear = -1
        currentMonth = -1
        currentDay = -1

        for snapshot in snapshots:
            timestamp = snapshot[1]

            keepDueToYear = False
            keepDueToMonth = False
            keepDueToDay = False

            if currentYear != timestamp.year:
                currentYear = timestamp.year
                currentMonth = -1
                if (now.year - currentYear) < yearsToKeep:
                    keepDueToYear = True

            if currentMonth != timestamp.month:
                currentMonth = timestamp.month
                currentDay = -1
                if (now.year - currentYear) * 12 + now.month - currentMonth < monthsToKeep:
                    keepDueToMonth = True

            if currentDay != timestamp.day:
                currentDay = timestamp.day
            delta = now - timestamp
            if delta.days + (1 if delta.seconds > 0 else 0) < daysToKeep:
                keepDueToDay = True

            if not keepDueToYear and not keepDueToMonth and not keepDueToDay:
                yield snapshot

    def _deleteSubvolumeSnapshot(snapshotDirectory):
        return getstatusoutput(f'btrfs subvolume delete {snapshotDirectory}')

    def cleanSnapshots(self, fileSystem, snapshotsDirectory, yearsToKeep, monthsToKeep, daysToKeep, deleteSnapshot=_deleteSubvolumeSnapshot):
        snapshots = self.getSnapshots(fileSystem, snapshotsDirectory)
        messages = []
        for obsoleteSnapshot in self.getObsoleteSnapshots(snapshots, yearsToKeep, monthsToKeep, daysToKeep):
            snapshotMessage = f'Deleting snapshot {obsoleteSnapshot[0]}'
            logging.info(snapshotMessage)
            messages.append(snapshotMessage)
            deleteSnapshot(obsoleteSnapshot[0])

        return '\n'.join(messages)


    def updateSnapshots(self, configSection):
        fileSystem = configSection.get('filesystem', None)
        if fileSystem is None:
            errorMessage = f'Key filesystem must be defined in Section {configSection.sectionName}'
            logging.error(errorMessage)
            return errorMessage

        subvolume = configSection.get('subvolume', None)
        if subvolume is None:
            errorMessage = f'Key subvolume must be defined in Section {configSection.sectionName}'
            logging.error(errorMessage)
            return errorMessage

        snapshotsDirectory = configSection.get('snapshotsDirectory', None)
        if snapshotsDirectory is None:
            errorMessage = f'Key snapshotsDirectory must be defined in Section {configSection.sectionName}'
            logging.error(errorMessage)
            return errorMessage

        yearsToKeep = configSection.getint('yearsToKeep', None)
        if yearsToKeep is None:
            errorMessage = f'Key yearsToKeep must be defined in Section {configSection.sectionName}'
            logging.error(errorMessage)
            return errorMessage

        monthsToKeep = configSection.getint('monthsToKeep', None)
        if monthsToKeep is None:
            errorMessage = f'Key monthsToKeep must be defined in Section {configSection.sectionName}'
            logging.error(errorMessage)
            return errorMessage

        daysToKeep = configSection.getint('daysToKeep', None)
        if daysToKeep is None:
            errorMessage = f'Key daysToKeep must be defined in Section {configSection.sectionName}'
            logging.error(errorMessage)
            return errorMessage

        with PeriodicTaskConfiguration(configSection, 'lastBackup', 24 * 60 * 60) as periodicBackup:
            if periodicBackup.periodicTaskIsDue:
                createMessage = self.takeSnapshot(subvolume, snapshotsDirectory)
                deleteMessages = self.cleanSnapshots(fileSystem, snapshotsDirectory, yearsToKeep, monthsToKeep, daysToKeep)
                return f'The following snapshot changes have been made:\n{createMessage}\n{deleteMessages}'
            else:
                return None
