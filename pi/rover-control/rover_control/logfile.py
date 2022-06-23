import time


class LogFile(object):
    def __init__(self, filename):
        self.f = open(filename, 'wt')

    def __del__(self):
        self.f.close()

    def write(self, string):
        self.f.write(f'{time.time()}:{string}')
        self.f.flush()  # To prevent power disconnect from erasing too much data
