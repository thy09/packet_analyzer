from datetime import datetime
import sys

class Timer:
    def __init__(self):
        self.reset()
    
    def record(self, hint):
        now = datetime.now()
        print("%s %s %s %s" % (hint, now, now - self.last, now - self.start))
        self.last = now

    def reset(self):
        now = datetime.now()
        self.start = self.last = now
