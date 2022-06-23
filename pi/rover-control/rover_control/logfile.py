class LogFile(object):
    def __init__(self, filename):
        self.f = open(filename, 'rt')

    def __del__(self):
        self.f.close()

    def write(self, string):
        self.f.write(string)
        self.f.flush()  # To prevent power disconnect from erasing too much data
