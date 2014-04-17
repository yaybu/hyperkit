========
Hyperkit
========


Command line interface
======================

Create
------

Create a virtual machine. If called with no arguments it will use
your default hypervisor to create a new virtual machine with your default
distribution, release, architecture with default configuration::

    hyperkit create

By default it will use VirtualBox to create a recent 64-bit Ubuntu VM.

usage: hyperkit create [-h] [--username USERNAME] [--password PASSWORD]
                       [--public-key PUBLIC_KEY] [--key-id KEY_ID]
                       [--memory MEMORY] [--cpus CPUS] [--image IMAGE]
                       [--options OPTIONS]
                       [name] [distro] [release] [arch]

positional arguments:
  name                  The name of the vm to create
  distro                The name of the distro to use
  release               The release of the distro to use
  arch                  The architecture of the distro to use

optional arguments:
  -h, --help            show this help message and exit
  --username USERNAME   The username of the initial user
  --password PASSWORD   The password for the initial user
  --public-key PUBLIC_KEY
                        A specific public key to be added to the initial
                        user's authorized list
  --key-id KEY_ID       The name of a key in your ~/.ssh folder
  --memory MEMORY       The amount of memory for the new virtual machine
  --cpus CPUS           The number of cpus for the new virtual machine
  --image IMAGE         A file path or url to an image to use instead of the
                        distro's default
  --options OPTIONS     hypervisor specific options to pass to the new VM



Authentication
~~~~~~~~~~~~~~

The following options affect how you can log into the created VM::

    --username        the username of the initial user (default:
    --password        the password for the initial user
    --public-key      a specific public key to be added to the initial user's allowed list
    --key-id          the name of a key in your ~/.ssh folder, to be added to the initial user's allowed list

If no authentication options are provided, hyperkit will use the first public key loaded into the running ssh agent, if there is one running.

If no password is provided, then password authentication will not be possible, and a public key must be used.

Hardware options
~~~~~~~~~~~~~~~~
    --memory          the amount of RAM for the VM, in Megabytes
    --cpus
