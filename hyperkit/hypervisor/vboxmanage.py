
from . import command

class VBoxManage(command.Command):
    command_name = "VBoxManage"
    subcommands = {
        "createvm": ["createvm",
                      "--name", "{name}",
                      "--basefolder", "{directory}",
                      "--ostype", "{ostype}",
                      "--register"],

        "create_sata": ["storagectl", "{name}",
                         "--name", '"SATA Controller"',
                         "--add", "sata",
                         "--controller", "IntelAHCI"],

        "create_ide": ["storagectl", "{name}",
                        "--name", '"IDE Controller"',
                        "--add", "ide"],

        "attach_disk": ["storageattach", "{name}",
                         "--storagectl", '"SATA Controller"',
                         "--port", "0", "--device", "0",
                         "--type", "hdd",
                         "--medium", "{disk}"],

        "attach_ide": ["storageattach", "{name}",
                        "--storagectl", '"IDE Controller"',
                        "--port", "{port}", "--device", "{device}",
                        "--type", "dvddrive",
                        "--medium", "{filename}"],

        "configurevm": ["modifyvm", "{name}",
                       "--ioapic", "on",
                       "--boot1", "disk", "--boot2", "none",
                       "--memory", "{memsize}", "--vram", "12",
                       "--uart1", "0x3f8", "4",
                       "--uartmode1", "disconnected"],

        "startvm": ["startvm",
                     "--type", "{type}",
                     "{name}"],

        "controlvm": ["controlvm", "{name}", "{button}"],

        "unregistervm": ["unregistervm", "{name}", "--delete"],

        "guestproperty": ["guestproperty", "get", "{name}", "{property}"],

    }


