
import os
import subprocess

from . import command


class VMRun(command.Command):

    command_name = "vmrun"
    subcommands = {
        "start": ["start", "{name}", "{type}"],
        "stop": ["stop", "{name}", "{type}"],
        "delete": ["deleteVM", "{name}"],
        "readVariable": ["readVariable", "{name}", "guestVar", "{variable}"],
    }

    @property
    def hosttype(self):
        default_hosttypes = [
            'ws',
            'fusion',
            'player',
        ]
        devnull = open(os.devnull, "w")
        for hosttype in default_hosttypes:
            command = [self.pathname, "-T", hosttype, "list"]
            if subprocess.call(command, stdout=devnull, stderr=devnull) == 0:
                return hosttype
        raise OSError("Cannot find host type")

    def compose(self, subcommand, *args, **kwargs):
        cmd_args = [self.pathname, "-T", self.hosttype]
        for a in self.subcommands[subcommand]:
            cmd_args.append(a.format(**kwargs))
        cmd_args.extend(args)
        return cmd_args
