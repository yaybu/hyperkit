
import abc
import os
import hashlib
import urllib2

from hyperkit import error


class Image(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def fetch(self, image_dir):
        """ Fetch the image into the specified image directory, and return the pathname. """


class LiteralImage(Image):

    """ An image specified by URL """

    def __init__(self, distro, release, arch, url):
        self.distro = distro
        self.release = release
        self.arch = arch
        self.url = url

    def fetch(self, imagedir):
        urihash = hashlib.sha256()
        urihash.update(self.url)
        pathname = os.path.join(imagedir, "user-{0}.qcow2".format(urihash.hexdigest()))
        try:
            response = urllib2.urlopen(self.url)
        except urllib2.HTTPError:
            raise error.FetchFailedException("Unable to fetch {0}".format(self.url))
        local = open(pathname, "w")
        while True:
            data = response.read(20 * 1024 * 1024 * 1024)
            if not data:
                break
            local.write(data)
        return pathname


class CanonicalImage(Image):

    """ An image specified with distro, release and arch. Distribution image
    handlers can register themselves with this class to provide fetching
    behaviour. """

    # populated with metaclass magic
    distributions = {}

    def __init__(self, distro, release, arch):
        self.distro = distro
        self.release = release
        self.arch = arch

    def distro_class(self):
        c = self.distributions.get(self.distro, None)
        if c is None:
            raise error.DistributionNotKnown()
        return c

    def fetch(self, image_dir):
        """ Fetches the specified uri into the cache and then extracts it
        into the library.  If name is None then a name is made up.

        Arguments:
            distro: the name of the distribution, i.e. Ubuntu, Fedora
            release: the distribution's name for the release, i.e. 12.04
            arch: the distribution's name for the architecture, i.e. x86_64, amd64
            format: the format of virtual machine image required, i.e. vmdk, qcow
        """
        pathname = os.path.join(image_dir, "{0}-{1}-{2}.qcow2".format(self.distro, self.release, self.arch))
        klass = self.distro_class()
        distro = klass(pathname, self.release, self.arch)
        distro.update()
        return pathname

__all__ = [LiteralImage, CanonicalImage]
