import os
import time


class LogFile(object):
    def __init__(self, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        self.f = open(filename, 'at')

    def __del__(self):
        self.f.close()

    def write(self, string):
        self.f.write(f'{time.time()}:{string}')
        self.f.flush()  # To prevent power disconnect from erasing too much data
