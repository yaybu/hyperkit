
class MachineSpec(object):
    def __init__(self, name, auth, image, hardware, options):
        self.name = name
        self.auth = auth
        self.image = image
        self.hardware = hardware
        self.options = options
