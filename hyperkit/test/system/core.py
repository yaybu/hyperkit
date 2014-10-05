import unittest2

# set before test run
# because I can't find a neat way to do this
guest = None

class Core(unittest2.TestCase):

    def test_hosts(self):
        hosts = guest.read_lines("/etc/hosts")
        self.assertEqual(hosts, None)

    def test_passwd(self):
        passwd = guest.read_lines("/etc/passwd")
        self.assertEqual(passwd, None)

    def test_shadow(self):
        shadow = guest.read_lines("/etc/shadow")
        self.assertEqual(shadow, None)

    def test_home(self):
        home = guest.readdir("/home")
        self.assertEqual(home, None)

    def test_network(self):
        raise NotImplemented


