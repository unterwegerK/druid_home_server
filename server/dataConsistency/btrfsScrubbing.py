from os import path
from subprocess import getoutput
import re

class BtrfsScrubbing:
    def startScrubbing(self, fileSystem):
        getoutput(f'btrfs scrub start {fileSystem}')

    def getScrubStatus(self, fileSystem):
        return getoutput(f'btrfs scrub status {fileSystem}')
            
    def parseScrubOutput(self, scrubOutput):    
        if m := re.search(r'\s*Status:\s*([a-zA-Z0-9_]*)', scrubOutput):
            return m.group(1)
        return None