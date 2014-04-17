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

You can specify the VM details thusly::

    hyperkit create [name] [distro] [release] [arch]

e.g.::

    hyperkit create testvm fedora 20 x86_64

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
