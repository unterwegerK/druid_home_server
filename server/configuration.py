from configparser import ConfigParser
from pathlib import Path
import os

class DynamicSection:
    def __init__(self, configuration, sectionName):
        self.sectionName = sectionName
        self.configuration = configuration

    def get(self, key, fallback):
        return self.configuration.get(self.sectionName, key, fallback)

    def getint(self, key, fallback):
        return self.configuration.getint(self.sectionName, key, fallback)

    def getboolean(self, key, fallback):
        return self.configuration.getboolean(self.sectionName, key, fallback)

    def set(self, key, value):
        self.configuration.set(self.sectionName, key, value)

class DynamicConfiguration:
    def __init__(self, filePath):
        self.filePath = filePath
        self.configFile = None
        self.configParser = None

    def __enter__(self):
        try:
            if not os.path.exists(self.filePath):
                Path(self.filePath).touch()

            self.configFile = open(self.filePath, 'r')
            self.configParser = ConfigParser()
            self.configParser.read_file(self.configFile)
        except (IOError, AttributeError):
            if self.configFile is not None:
                self.configFile.close()
                self.configFile = None
            self.configParser = None
        return self
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        if self.configParser is not None and self.configFile is not None:
            self.configFile.close()
            with open(self.filePath, 'w') as f:
                self.configParser.write(f)
        if self.configFile is not None:
            self.configFile.close()
            
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

        

class StaticSection:
    def __init__(self, configuration, sectionName):
        self.sectionName = sectionName
        self.configuration = configuration

    def get(self, key, fallback):
        return self.configuration.get(self.sectionName, key, fallback)

    def getint(self, key, fallback):
        return self.configuration.getint(self.sectionName, key, fallback)

    def getboolean(self, key, fallback):
        return self.configuration.getboolean(self.sectionName, key, fallback)

class StaticConfiguration:
    def __init__(self, filePath):
            with open(filePath, 'r') as configFile:
                self.configParser = ConfigParser()
                self.configParser.read_file(configFile)
            
    def isValid(self):
        return self.configParser is not None

    def get(self, section, key, fallback):
        return self.configParser.get(section, key, fallback=fallback)

    def getint(self, section, key, fallback):
        return self.configParser.getint(section, key, fallback=fallback)

    def getboolean(self, section, key, fallback):
        return self.configParser.getboolean(section, key, fallback=fallback)



