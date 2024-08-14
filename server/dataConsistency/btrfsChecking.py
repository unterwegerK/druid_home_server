from subprocess import getoutput
import subprocess
import re
import os

class BtrfsChecking:
    def suspend(self, suspendCommand):
        os.system(suspendCommand)

    def checkDevice(self, device):
        process = subprocess.run(['btrfs', 'check', device], capture_output=True)

        return (process.returncode, f'stdout: {process.stdout}\nstderr: {process.stderr}')
    
    def containsErrors(self, output):
        if re.search('found \\d+ bytes used, no error found', output):
            return False
        
        if re.search('(?:errors|error\\(s\\)|error) found', output):
            return True

        return None