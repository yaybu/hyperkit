# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

    def __str__(self):
        return "%s-%s-%s at %s" % (self.distro, self.release, self.arch, self.url)

    def fetch(self, imagedir):
        if not os.path.exists(imagedir):
            os.mkdir(imagedir)
        urihash = hashlib.sha256()
        urihash.update(self.url)
        pathname = os.path.join(imagedir, "user-{0}-{1}-{2}.{3}.qcow2".format(self.distro, self.release, self.arch, urihash.hexdigest()))
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


class DistroImageType(abc.ABCMeta):

    """ Registers the distro image with the canonical image fetcher """

    def __new__(meta, class_name, bases, new_attrs):
        cls = type.__new__(meta, class_name, bases, new_attrs)
        if cls.name is not None:
            CanonicalImage.distributions[cls.name] = cls
        return cls


class BaseDistroImage(object):

    __metaclass__ = DistroImageType

    name = None

    @abc.abstractmethod
    def __init__(self, pathname, release, arch):
        pass

    @abc.abstractmethod
    def update(self):
        """ Update the path represented by pathname with a qcow2 image of the
        distro for the specified release and architecture. """


class CanonicalImage(Image):

    """ An image specified with distro, release and arch. Distribution image
    handlers can register themselves with this class to provide fetching
    behaviour. """

    # populated with metaclass magic from the distro module
    distributions = {}

    default_distro = "ubuntu"

    default_release = {
        "ubuntu": "14.04",
        "fedora": "20",
    }

    default_arch = {
        "ubuntu": "amd64",
        "fedora": "x86_64",
    }

    def __init__(self, distro=None, release=None, arch=None):
        if distro is None:
            distro = self.default_distro
        self.distro = distro
        if release is None:
            release = self.default_release[distro]
        self.release = release
        if arch is None:
            arch = self.default_arch[distro]
        self.arch = arch

    def __str__(self):
        return "official %s-%s-%s" % (self.distro, self.release, self.arch)

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
        if not os.path.exists(image_dir):
            os.mkdir(image_dir)
        pathname = os.path.join(image_dir, "{0}-{1}-{2}.qcow2".format(self.distro, self.release, self.arch))
        klass = self.distro_class()
        distro = klass(pathname, self.release, self.arch)
        distro.update()
        return pathname

__all__ = [LiteralImage, CanonicalImage]
