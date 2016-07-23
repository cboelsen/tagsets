import os

class PathGenerator:
    def __init__(self, basedir):
        self.rootpath=basedir

    def getsubgenerator(self, path):
        return PathGenerator(os.path.join(self.rootpath, path))
        
    def getpath(self, path):
        return os.path.join(self.rootpath, path)

    def getroot(self):
        return self.rootpath

