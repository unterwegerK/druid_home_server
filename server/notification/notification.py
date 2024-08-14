from enum import Enum

class Severity(Enum):
    INFO = 1
    ERROR = 2


class Notification:
    def __init__(self, header, message, severity):
        self.header = header
        self.message = message
        self.severity = severity