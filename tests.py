#!/usr/bin/env python3
import unittest
import configuration
import os
from os.path import exists
from datetime import datetime, timedelta
import periodicStatusReport

class TestConfigFile:

    def __init__(self, fileName):
        self.fileName = fileName

    def __enter__(self):
        with open(self.fileName, 'w') as f:
            f.write('[Section0]\nKey0=Value0\nKey1=Value1\n\n[Section1]\nKey2=Value2\n')
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        os.remove(self.fileName)
            

class ConfigurationTests(unittest.TestCase):

    def testInvalidWhenNotInWithBlock(self):
        testee = configuration.Configuration('./unkownConfig.ini')
        self.assertFalse(testee.isValid())

        #avoid error due to not-closed file
        testee.__exit__(None, None, None)

    def testInvalidWhenFileNotFound(self):
        iniFilePath = './unknownConfig.ini'
        if exists(iniFilePath):
            os.remove(iniFilePath)
        with configuration.Configuration(iniFilePath) as testee:
            self.assertFalse(testee.isValid())
        if exists(iniFilePath):
            os.remove(iniFilePath)


    def testIniFile(self):
        with TestConfigFile('./config.ini') as iniFile:
            with configuration.Configuration(iniFile.fileName) as testee:
                self.assertTrue(testee.isValid())

            with open(iniFile.fileName, 'r') as f:
                lines = f.readlines()
                self.assertTrue(any('[Section0]' in line for line in lines))
                self.assertTrue(any('key0 = Value0' in line for line in lines))
                self.assertTrue(any('key1 = Value1' in line for line in lines))
                self.assertTrue(any('[Section1]' in line for line in lines))
                self.assertTrue(any('key2 = Value2' in line for line in lines))


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



class PeriodicStatusReportTests(unittest.TestCase):
    def testNoLoggingIfIntervalNotYetOver(self):
        keyValuePairs = {}
        timestamp = datetime.now() - timedelta(hours=23)
        timestampString = timestamp.strftime('%y-%m-%d %H:%M:%S')
        keyValuePairs['periodicStatusReport|lastReport'] = timestampString
        
        config = TestConfiguration(keyValuePairs)

        report = periodicStatusReport.getServerStatus(config)

        self.assertIsNone(report)
        self.assertEqual(config.get('periodicStatusReport', 'lastReport', None), timestampString)

    def testLoggingIfIntervalIsOver(self):
        timeFormat = '%y-%m-%d %H:%M:%S'
        keyValuePairs = {}
        timestamp = datetime.now() - timedelta(hours=25)
        timestampString = timestamp.strftime(timeFormat)
        keyValuePairs['periodicStatusReport|lastReport'] = timestampString
        
        config = TestConfiguration(keyValuePairs)

        report = periodicStatusReport.getServerStatus(config)

        self.assertIs(type(report), str)
        newTimestamp = datetime.strptime(config.get('periodicStatusReport', 'lastReport', None), timeFormat)

        self.assertTrue((datetime.now() - newTimestamp).total_seconds() < 10)

if __name__ == '__main__':
    unittest.main()

