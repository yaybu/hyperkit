import unittest2
import mock
import crypt
import yaml

from hyperkit import cloudinit

class TestCloudConfig(unittest2.TestCase):

    def setUp(self):
        self.auth = mock.MagicMock()
        self.auth.username = "foo"
        self.auth.password = "bar"
        self.c = cloudinit.CloudConfig(self.auth)

    def test_get_config(self):
        config = self.c.get_config()
        pwentry = config['users'][0]['passwd']
        _, _, salt, passwd = pwentry.split("$")
        self.assertEqual(config['users'][0]['name'], 'foo')
        self.assertEqual(pwentry, crypt.crypt("bar", "$5${0}$".format(salt)))
        self.assertEqual(config['password'], "bar")
        self.assertEqual(config['chpasswd'], {'expire': False})
        self.assertEqual(config['ssh_pwauth'], True)

    def test_encrypt(self):
        pwentry = self.c.encrypt("foobarbaz")
        _, _, salt, passwd = pwentry.split("$")
        self.assertEqual(pwentry, crypt.crypt("foobarbaz", "$5${0}$".format(salt)))

    def test_generate_salt(self):
        salt = self.c.generate_salt()
        self.assertEqual(len(salt), 16)

    def test_open(self):
        stream = self.c.open()
        header = stream.readline()
        self.assertEqual(header, "#cloud-config\n")
        data = yaml.load(stream)
        self.assertTrue(isinstance(data, dict))
