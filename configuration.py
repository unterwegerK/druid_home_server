from configparser import ConfigParser

class Configuration:

    def __init__(self, filePath):
        self.filePath = filePath
        self.configFile = None
        self.configParser = None

    def __enter__(self):
        try:
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
        value = self.configParser.get(section, key, fallback=None)
        return fallback if value is None else value

    def set(self, section, key, value):
        self.configParser.set(section, key, value)



