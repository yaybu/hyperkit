import unittest2

class Core(unittest2.TestCase):

    def __init__(self, methodName, system):
        super(Core, self).__init__(methodName)
        self.system = system

    def test_hosts(self):
        pass
