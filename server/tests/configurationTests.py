import unittest
import configuration
from os.path import exists
import os
from unittests import TestConfigFile

class ConfigurationTests(unittest.TestCase):

    def testInvalidWhenNotInWithBlock(self):
        testee = configuration.DynamicConfiguration('./unkownConfig.ini')
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
            with configuration.DynamicConfiguration(iniFile.fileName) as testee:
                self.assertTrue(testee.isValid())

            with open(iniFile.fileName, 'r') as f:
                lines = f.readlines()
                self.assertTrue(any('[Section0]' in line for line in lines))
                self.assertTrue(any('key0 = Value0' in line for line in lines))
                self.assertTrue(any('key1 = Value1' in line for line in lines))
                self.assertTrue(any('[Section1]' in line for line in lines))
                self.assertTrue(any('key2 = Value2' in line for line in lines))

    def testFallbackOnUnkownSection(self):
        with TestConfigFile('./config.ini') as iniFile:
            with configuration.DynamicConfiguration(iniFile.fileName) as testee:
                value = testee.get('UnknownSection', 'Key1', 'Fallback')
                self.assertEqual(value, 'Fallback')

    def testCreationOfUnknownSection(self):
        with TestConfigFile('./config.ini') as iniFile:
            with configuration.DynamicConfiguration(iniFile.fileName) as testee:
                testee.set('UnknownSection', 'Key1', 'Value')
                value = testee.get('UnknownSection', 'Key1', None)
                self.assertEqual(value, 'Value')

    def testConvenienceGetter(self):
        with TestConfigFile('./config.ini') as iniFile:
            with configuration.DynamicConfiguration(iniFile.fileName) as testee:
                i = testee.getint('Section2', 'Key3', None)
                self.assertEqual(i, 5)

                i = testee.getint('Section2', 'UnknownKey', 7)
                self.assertEqual(i, 7)

                b = testee.getboolean('Section2', 'Key4', None)
                self.assertTrue(b)

                b = testee.getboolean('Section2', 'UnknownKey', False)
                self.assertFalse(b)