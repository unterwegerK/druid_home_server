class ObsoleteSnapshotDetermination:
    def __init__(self, yearsToKeep, monthsToKeep, daysToKeep):
        self.yearsToKeep = yearsToKeep
        self.monthsToKeep = monthsToKeep
        self.daysToKeep = daysToKeep

    def getObsoleteSnapshots(self, snapshots, currentTime):
        snapshots = sorted(snapshots, key=lambda s:s[1])

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
                if (currentTime.year - currentYear) < self.yearsToKeep:
                    keepDueToYear = True

            if currentMonth != timestamp.month:
                currentMonth = timestamp.month
                currentDay = -1
                if (currentTime.year - currentYear) * 12 + currentTime.month - currentMonth < self.monthsToKeep:
                    keepDueToMonth = True

            if currentDay != timestamp.day:
                currentDay = timestamp.day
            delta = currentTime - timestamp
            if delta.days + (1 if delta.seconds > 0 else 0) < self.daysToKeep:
                keepDueToDay = True

            if not keepDueToYear and not keepDueToMonth and not keepDueToDay:
                yield snapshot
