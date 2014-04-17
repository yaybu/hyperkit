
import abc
import time
import os
import datetime


class State:
    DEAD = 0
    STARTING = 1
    RUNNING = 2


class MachineInstance(object):

    """ This is a local virtual machine, probably created originally by a MachineBuilder. """

    __metaclass__ = abc.ABCMeta

    system = None

    timeout = 30

    def __init__(self, directory, instance_id):
        self.instance_dir = os.path.join(directory, instance_id)
        self.instance_id = instance_id
        self.state = State.DEAD

    def start(self):
        self._start()
        self.state = State.STARTING

    def stop(self, force=False):
        self._stop(force=force)
        self.state = State.DEAD

    def destroy(self):
        self._destroy()
        self.state = State.DEAD

    def load(self, name):
        if self.state != State.DEAD:
            raise ValueError("Trying to start a node when we already have one")
        for vm in self.machines.instances("vbox"):
            if vm.name == name:
                self.node = vm
                self.start()
                return

    def wait(self, timeout=None):
        """ Call with a timeout of 0 to wait forever. """
        if timeout is None:
            timeout = self.timeout
        started = time.time()
        while True:
            if self.get_ip():
                self.state = State.RUNNING
                return True
            else:
                time.sleep(1)
            if timeout > 0:
                if time.time() - started > timeout:
                    return False


class Hypervisor(object):

    """ This builds a new MachineInstance when provided with a source image.
    The create method will return a MachineInstance when provided with a
    MachineSpec """

    __metaclass__ = abc.ABCMeta

    # the directory in which instances live
    directory = None

    # the class that represents an instance
    instance = None

    # the directory that contains images
    image_dir = os.path.expanduser("~/.hyperkit")

    def set_image_dir(self, image_dir):
        self.image_dir = os.path.expanduser(image_dir)

    @abc.abstractmethod
    def create(self, spec, image_dir="~/.hyperkit"):
        """ Builds the instance based on the spec, loading images from image_dir. """

    def load(self, name):
        if os.path.exists(os.path.join(self.directory, name)):
            return self.instance(self.directory, name)

    def get_instance_id(self, spec):
        today = datetime.datetime.now()
        instance_id = "{0}-{1:%Y-%m-%d}".format(spec.name, today)
        count = 1
        while True:
            pathname = os.path.join(self.directory, instance_id)
            if not os.path.exists(pathname):
                break
            instance_id = "{0}-{1:%Y-%m-%d}-{2:02}".format(spec.name, today, count)
            count = count + 1
        return instance_id

    def instances(self):
        """ Return a generator of instance objects. """
        for d in os.listdir(self.directory):
            yield self.instance(self.directory, d)

__all__ = [State, MachineInstance, Hypervisor]
