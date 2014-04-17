from auth import PasswordAuth
from image import CanonicalImage
from hardware import Hardware


class MachineSpec(object):
    def __init__(self, name="myvm",
                 auth=None, image=None, hardware=None, options=None):
        if auth is None:
            auth = PasswordAuth()
        if image is None:
            image = CanonicalImage()
        if hardware is None:
            hardware = Hardware()
        self.name = name
        self.auth = auth
        self.image = image
        self.hardware = hardware
        self.options = options
