#!/usr/bin/env python3
import unittest
import os

class TestConfigFile:

    def __init__(self, fileName):
        self.fileName = fileName

    def __enter__(self):
        with open(self.fileName, 'w') as f:
            f.write('[Section0]\nKey0=Value0\nKey1=Value1\n\n[Section1]\nKey2=Value2\n[Section2]\nKey3=5\nKey4=True')
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        os.remove(self.fileName)

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
        return fallback if value is None else value

    def set(self, section, key, value):
        key = f'{section}|{key}'
        self.keyValuePairs[key] = value

if __name__ == '__main__':
    unittest.main()

