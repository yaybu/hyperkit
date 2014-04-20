
import mock
import unittest2

import urllib2

from hyperkit.distro import distro
from hyperkit.distro.ubuntu import UbuntuCloudImage
from hyperkit import error


import hashlib


class MockDistroImage(distro.DistroImage):

    @property
    def hash_function(self):
        return hashlib.md5

    def remote_image_url(self):
        return "remote_image_url"

    def remote_hashfile_url(self):
        return "remote_hashfile_url"

    def image_hash(self, hashes):
        return hashes

class TestDistroImage(unittest2.TestCase):

    def setUp(self):
        self.cloud_image = MockDistroImage("pathname", "release", "arch")

    @mock.patch('urllib2.urlopen')
    @mock.patch('__builtin__.open')
    def test_fetch(self, m_open, m_urlopen):
        m_urlopen().read.side_effect = ["foo", "bar", ""]
        self.cloud_image.fetch()
        self.assertEqual(m_urlopen.call_args, mock.call('remote_image_url'))
        self.assertEqual(m_open.call_args, mock.call('pathname', 'w'))
        self.assertEqual(m_open().write.call_args_list, [mock.call('foo'), mock.call('bar')])

    @mock.patch('urllib2.urlopen')
    @mock.patch('__builtin__.open')
    def test_fetch_httperror(self, m_open, m_urlopen):
        m_urlopen.side_effect = urllib2.HTTPError(*[None] * 5)
        self.assertRaises(error.FetchFailedException, self.cloud_image.fetch)

    def test_decode_hashes_happy(self):
        d = self.cloud_image.decode_hashes("""
        foo bar
        baz quux
        """)
        self.assertEqual(d, {'bar': 'foo', 'quux': 'baz'})

    def test_decode_hashes_otherstuff(self):
        d = self.cloud_image.decode_hashes("""
        ----- PGP CRAP -----
        foo bar
        baz quux
        ----- MORE PGP CRAP -----

        stuff
        #wow
        """)
        self.assertEqual(d, {'bar': 'foo', 'quux': 'baz'})

    def test_decode_hashes_duplicate(self):
        self.assertRaises(KeyError, self.cloud_image.decode_hashes, """
        foo bar
        baz bar
        """)

    @mock.patch('urllib2.urlopen')
    def test_get_remote_hashes(self, m_urlopen):
        m_urlopen().read.return_value = """
        foo bar
        baz quux
        """
        self.assertEqual(self.cloud_image.get_remote_hashes(), {
            "bar": "foo",
            "quux": "baz",
        })

    @mock.patch('urllib2.urlopen')
    def test_get_remote_hashes_empty(self, m_urlopen):
        m_urlopen().read.return_value = ""
        self.assertEqual(self.cloud_image.get_remote_hashes(), {})

    @mock.patch('urllib2.urlopen')
    def test_get_remote_hashes_missing(self, m_urlopen):
        m_urlopen.side_effect = urllib2.HTTPError(*[None] * 5)
        self.assertEqual(self.cloud_image.get_remote_hashes(), {})

    @mock.patch('os.path.exists')
    @mock.patch('__builtin__.open')
    def test_get_local_sum(self, m_open, m_exists):
        m_exists.return_value = True
        m_open().read.return_value = "foobar"
        self.assertEqual(self.cloud_image.get_local_sum(), "3858f62230ac3c915f300c664312c63f")

    def test_requires_update(self):
        self.cloud_image.local_hash = None
        self.assertEqual(self.cloud_image.requires_update(), True)
        self.cloud_image.local_hash = "foo"
        self.cloud_image.remote_hash = "bar"
        self.assertEqual(self.cloud_image.requires_update(), True)
        self.cloud_image.local_hash = "foo"
        self.cloud_image.remote_hash = "foo"
        self.assertEqual(self.cloud_image.requires_update(), False)

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
        pass
