from configparser import ConfigParser


class StringBasedDynamicConfiguration:
    def __init__(self, initialFileContent):
        self.initialFileContent = initialFileContent
        self.finalFileContent = None
        self.configParser = ConfigParser()
        self.configParser.read_string(self.initialFileContent)

    def isValid(self):
        return self.configParser is not None

    def get(self, section, key, fallback):
        return self.configParser.get(section, key, fallback=fallback)

    def getint(self, section, key, fallback):
        return self.configParser.getint(section, key, fallback=fallback)

    def getboolean(self, section, key, fallback):
        return self.configParser.getboolean(section, key, fallback=fallback)

    def set(self, section, key, value):
        if not self.configParser.has_section(section):
            self.configParser.add_section(section)
        self.configParser.set(section, key, value)