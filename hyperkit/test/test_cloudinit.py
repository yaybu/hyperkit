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


class TestMetaData(unittest2.TestCase):

    def setUp(self):
        self.m = cloudinit.MetaData("foo")

    def test_as_dict(self):
        d = self.m.as_dict()
        self.assertEqual(d, {
            "local-hostname": "localhost",
            "instance-id": "foo",
        })

    def test_open(self):
        d = yaml.load(self.m.open())
        self.assertEqual(d, {
            "local-hostname": "localhost",
            "instance-id": "foo",
        })


class TestSeed(unittest2.TestCase):

    @mock.patch("tempfile.mkdtemp")
    def setUp(self, m_mkdtemp):
        m_mkdtemp.return_value = "/tmpdir"
        self.cloud_config = mock.MagicMock()
        self.cloud_config.filename = "user-data"
        self.meta_data = mock.MagicMock()
        self.meta_data.filename = "meta-data"
        self.seed = cloudinit.Seed("/does_not_exist", self.cloud_config, self.meta_data)

    def test_pathname(self):
        self.assertEqual(self.seed.pathname, "/does_not_exist/seed.iso")

    def test_filenames(self):
        self.assertEqual(list(self.seed.filenames), ["user-data", "meta-data"])

    @mock.patch("subprocess.Popen")
    @mock.patch("__builtin__.open")
    @mock.patch("os.unlink")
    @mock.patch("os.rmdir")
    def test_write(self, m_rmdir, m_unlink, m_open, m_popen):
        m_popen().communicate.return_value = ["", ""]
        m_popen().returncode = 0
        self.seed.write()
        self.assertEqual(m_open.call_args_list, [mock.call("/tmpdir/user-data", "w"), mock.call("/tmpdir/meta-data", "w")])
        self.assertEqual(m_unlink.call_args_list, [mock.call("/tmpdir/user-data"), mock.call("/tmpdir/meta-data")])
        self.assertEqual(m_rmdir.call_args, mock.call("/tmpdir"))
        self.assertEqual(m_popen.call_args, mock.call(
            stdin=None,
            args=['/usr/bin/genisoimage',
                  '-output',
                  '/does_not_exist/seed.iso',
                  '-volid', 'cidata',
                  '-joliet', '-rock',
                  'user-data', 'meta-data'],
            cwd='/tmpdir', stderr=-1, stdout=-1))
