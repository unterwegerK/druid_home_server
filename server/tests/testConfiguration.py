
class TestConfiguration:
    def __init__(self, keyValuePairs):
       self.keyValuePairs = keyValuePairs
    
    def get(self, section, key, fallback):
        key = f'{section}|{key}'
        if key in self.keyValuePairs:
            return self.keyValuePairs[key]
        return fallback

    def getint(self, section, key, fallback):
        value = self.get(section, key, None)
        return fallback if value is None else int(value)

    def set(self, section, key, value):
        key = f'{section}|{key}'
        self.keyValuePairs[key] = value



