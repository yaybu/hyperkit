
import guestfs
import time
import threading

class LogMonitor(threading.Thread):

    logfile = "/var/log/syslog"

    def __init__(self, guest):
        super(LogMonitor, self).__init__()
        self.guest = guest
        self.guest.mount()
        self.finished = threading.Event()

    def run(self):
        printed = 0
        print "Log monitor thread running"
        while True:
            time.sleep(10)
            try:
                lines = self.guest.guest.read_lines(self.logfile)
                print lines[printed:]
                printed = len(lines)
            except RuntimeError:
                print self.logfile, "does not exist"
                for i in self.guest.guest.ls("/var/log"):
                    print i
            self.guest.close()
            if self.finished.is_set():
                return

    def stop(self):
        self.finished.set()
