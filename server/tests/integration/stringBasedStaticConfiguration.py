from configparser import ConfigParser


class StringBasedStaticConfiguration:
    def __init__(self, fileContent):
        self.configParser = ConfigParser()
        self.configParser.read_string(fileContent)

    def isValid(self):
        return self.configParser is not None

    def get(self, section, key, fallback):
        return self.configParser.get(section, key, fallback=fallback)

    def getint(self, section, key, fallback):
        return self.configParser.getint(section, key, fallback=fallback)

    def getboolean(self, section, key, fallback):
        return self.configParser.getboolean(section, key, fallback=fallback)