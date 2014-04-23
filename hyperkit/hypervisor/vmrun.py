
from . import command


class VMRun(command.Command):

    command_name = "vmrun"
    subcommands = {
        "start": ["startvm", "{name}", "{type}"],
        "stop": ["stopvm", "{name}", "hard"],
        "delete": ["deleteVM", "{name}"],
        "readVariable": ["readVariable", "{name}", "guestVar", "{variable}"],
    }
