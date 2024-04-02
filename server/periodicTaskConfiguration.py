from datetime import datetime


class PeriodicTaskConfiguration:
    FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, section, lastTimestampKey, defaultInterval, getCurrentTime = datetime.now):
        self.section = section
        self.lastTimestampKey = lastTimestampKey
        self.now = getCurrentTime()

        interval = section.getint('interval', defaultInterval)
        lastTimestamp = datetime.strptime(section.get(lastTimestampKey, '0001-01-01 00:00:00'), self.FORMAT)

        timeSinceLastTimestamp = self.now - lastTimestamp

        self.periodicTaskIsDue = timeSinceLastTimestamp.total_seconds() >= interval

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self.periodicTaskIsDue:
            self.section.set(self.lastTimestampKey, self.now.strftime(self.FORMAT))

