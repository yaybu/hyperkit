
class Hardware(object):
    def __init__(self, memory=256, cpus=1):
        self.memory = memory
        self.cpus = cpus

    def __str__(self):
        return "%s CPUs %s RAM" % (self.cpus, self.memory)

__all__ = [Hardware]
