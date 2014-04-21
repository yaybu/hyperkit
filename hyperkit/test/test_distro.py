
import mock
import unittest2
import hashlib
import urllib2

from hyperkit.distro import distro
from hyperkit.distro.ubuntu import UbuntuCloudImage
from hyperkit.distro.cirros import CirrosCloudImage
from hyperkit.distro.fedora import FedoraCloudImage
from hyperkit import error

class MockDistroImage(distro.DistroImage):

    @property
    def hash_function(self):
        return hashlib.md5

    def remote_image_url(self):
        return "remote_image_url"

    def remote_hashfile_url(self):
        return "remote_hashfile_url"

    def image_hash(self, hashes):
        return hashes["bar"]

class TestDistroImage(unittest2.TestCase):

    def setUp(self):
        self.image = MockDistroImage("pathname", "release", "arch")

    @mock.patch('urllib2.urlopen')
    @mock.patch('__builtin__.open')
    def test_fetch(self, m_open, m_urlopen):
        m_urlopen().read.side_effect = ["foo", "bar", ""]
        self.image.fetch()
        self.assertEqual(m_urlopen.call_args, mock.call('remote_image_url'))
        self.assertEqual(m_open.call_args, mock.call('pathname', 'w'))
        self.assertEqual(m_open().write.call_args_list, [mock.call('foo'), mock.call('bar')])

    @mock.patch('urllib2.urlopen')
    @mock.patch('__builtin__.open')
    def test_fetch_httperror(self, m_open, m_urlopen):
        m_urlopen.side_effect = urllib2.HTTPError(*[None] * 5)
        self.assertRaises(error.FetchFailedException, self.image.fetch)

    def test_decode_hashes_happy(self):
        d = self.image.decode_hashes("""
        foo bar
        baz quux
        """)
        self.assertEqual(d, {'bar': 'foo', 'quux': 'baz'})

    def test_decode_hashes_otherstuff(self):
        d = self.image.decode_hashes("""
        ----- PGP CRAP -----
        foo bar
        baz quux
        ----- MORE PGP CRAP -----

        stuff
        #wow
        """)
        self.assertEqual(d, {'bar': 'foo', 'quux': 'baz'})

    def test_decode_hashes_duplicate(self):
        self.assertRaises(KeyError, self.image.decode_hashes, """
        foo bar
        baz bar
        """)

    @mock.patch('urllib2.urlopen')
    def test_get_remote_hashes(self, m_urlopen):
        m_urlopen().read.return_value = """
        foo bar
        baz quux
        """
        self.assertEqual(self.image.get_remote_hashes(), {
            "bar": "foo",
            "quux": "baz",
        })

    @mock.patch('urllib2.urlopen')
    def test_get_remote_hashes_empty(self, m_urlopen):
        m_urlopen().read.return_value = ""
        self.assertEqual(self.image.get_remote_hashes(), {})

    @mock.patch('urllib2.urlopen')
    def test_get_remote_hashes_missing(self, m_urlopen):
        m_urlopen.side_effect = urllib2.HTTPError(*[None] * 5)
        self.assertEqual(self.image.get_remote_hashes(), {})

    @mock.patch('os.path.exists')
    @mock.patch('__builtin__.open')
    def test_get_local_sum(self, m_open, m_exists):
        m_exists.return_value = True
        m_open().read.return_value = "foobar"
        self.assertEqual(self.image.get_local_sum(), "3858f62230ac3c915f300c664312c63f")

    def test_requires_update(self):
        self.image.local_hash = None
        self.assertEqual(self.image.requires_update(), True)
        self.image.local_hash = "foo"
        self.image.remote_hash = "bar"
        self.assertEqual(self.image.requires_update(), True)
        self.image.local_hash = "foo"
        self.image.remote_hash = "foo"
        self.assertEqual(self.image.requires_update(), False)

    @mock.patch('urllib2.urlopen')
    @mock.patch('os.path.exists')
    @mock.patch('__builtin__.open')
    def test_update_hashes(self, m_open, m_exists, m_urlopen):
        m_urlopen().read.return_value = """
        foo bar
        baz quux
        """
        self.image.remote_hash = None
        m_exists.return_value = True
        m_open().read.return_value = "foobar"
        self.image.update_hashes()
        self.assertEqual(self.image.remote_hash, "foo")
        self.assertEqual(self.image.local_hash, "3858f62230ac3c915f300c664312c63f")

class TestUbuntuCloudImage(unittest2.TestCase):

    def setUp(self):
        self.image = UbuntuCloudImage("/tmp", "14.04", "amd64")

    def test_remote_image_url(self):
        good = "http://cloud-images.ubuntu.com/releases/14.04/release/ubuntu-14.04-server-cloudimg-amd64-disk1.img"
        self.assertEqual(self.image.remote_image_url(), good)

    def test_remote_hashfile_url(self):
        good = "http://cloud-images.ubuntu.com/releases/14.04/release/SHA256SUMS"
        self.assertEqual(self.image.remote_hashfile_url(), good)

    def test_image_hash(self):
        good = "*ubuntu-14.04-server-cloudimg-amd64-disk1.img"
        self.assertEqual(self.image.image_hash({good: "foo", }), "foo")

class TestCirrosImage(unittest2.TestCase):

    def setUp(self):
        self.image = CirrosCloudImage("/tmp", "14.04", "amd64")

    def test_image_hash(self):
        filename = 'cirros-14.04-amd64-disk.img'
        self.assertEqual(self.image.image_hash({filename: "foo", }), "foo")


fedora_hashfile = """ \
-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA256

b4bce4a24caaa2e480eb1c79210509771f5ce47c903aaa28a41f416588d60d74 *Fedora-x86_64-20-20131211.1-sda.qcow2
a314053befcf1fa7a7874de24d069f5c321f5ea8b3288910252e2d831d8bc772 *Fedora-x86_64-20-20131211.1-sda.raw.xz
-----BEGIN PGP SIGNATURE-----
Version: GnuPG v1.4.11 (GNU/Linux)

iQIcBAEBCAAGBQJSqoUIAAoJEC6xYfokYRDBxTMQAKwaUi08kHiJkSob9lpDLsLw
TSih/5uPj3BO6R1KzqQKtns0I6vo78DC+kuGHmd9G7RyGlr+QTkXoUdXH8RXbdkv
WEKvzGL7K7nTM9yFYl0kZlhHeneQ7yiTEAIuIxJ6NTZVfkJ52xCJ0m17ip/Okzc8
P3fMFBJUuT5y9uz3ARwFcYy6f9Y4M5g/erqhc/o1cqwTpQLNNJBnl7Ihj0rFxrnL
VGXsUBwHx/QlMNXu+jxhEJXsqgKWPC7x2sZ3HXrw9zyj6zUoD+9fzxifVDLliVS2
TdI0wPE+wsx7VfYAobxbH08P3aq2z/nwUoiT4iiz3gOnFusf/ln7R1vt0Ul53i49
FVEBp88++GK2gO/jyM1XhOL7hqSZtUTJ3Em0yG4Xy7SjnsW4AqoWSrKFLbGOHyst
7mbIL5YkW4hvMS7SDbL9HRWCs6CxZVVQ7cqUpijLdzZYz/QAnR/maHVO6po48DcT
+7BHALqX5wvjwHo4xydmwuixMg7x4GNcWbakKDEQLsZoZN46GnRlI0ctp6C0g+Kn
n1w5EsOf9vxAE41YS8n4UHXSzChjDvRTE/YNpERMdzLCYtMENUGn+4e3TDiIlBlY
FiC4feBLhNrdkM0WRGla83wrTRkTL7D6f1VFT2cAc3+Flaof8C6nLi40s4aV41fl
Tbtsx1bwzSh17kL5RYqT
=ynzB
-----END PGP SIGNATURE-----
"""

class TestFedoraImage(unittest2.TestCase):

    def setUp(self):
        self.image = FedoraCloudImage("/tmp", "20", "x86_64")

    def test_remote_image_url(self):
        self.image.version = "foo"
        good = "http://download.fedoraproject.org/pub/fedora/linux/releases/20/Images/x86_64/Fedora-x86_64-20-foo-sda.qcow2"
        self.assertEqual(self.image.remote_image_url(), good)

    def test_image_hash(self):
        self.image.version = "foo"
        filename = '*Fedora-x86_64-20-foo-sda.qcow2'
        self.assertEqual(self.image.image_hash({filename: "foo", }), "foo")

    @mock.patch('urllib2.urlopen')
    @mock.patch('os.path.exists')
    @mock.patch('__builtin__.open')
    def test_update_hashes(self, m_open, m_exists, m_urlopen):
        m_urlopen().read.return_value = fedora_hashfile
        self.image.remote_hash = None
        m_exists.return_value = True
        m_open().read.return_value = "foobar"
        self.image.update_hashes()
        self.assertEqual(self.image.remote_hash, "b4bce4a24caaa2e480eb1c79210509771f5ce47c903aaa28a41f416588d60d74")
        self.assertEqual(self.image.local_hash, "c3ab8ff13720e8ad9047dd39466b3c8974e592c2fa383d4a3960714caef0c4f2")
