
from . import command


class QEmuImg(command.Command):
    command_name = "qemu-img"
    subcommands = {
        "convert": ["convert", "-O", "{format}", "{source}", "{destination}"],
    }
