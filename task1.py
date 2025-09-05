import os
import platform


class Shell:
    @staticmethod
    def clean_quotation_marks(arg):
        arg = arg.strip('"')
        return arg

    @staticmethod
    def ls(arg):
        if '"' in arg:
            arg = Shell.clean_quotation_marks(arg)
        return f"ls {arg}"
    
    @staticmethod
    def cd(arg):
        return f"cd {arg}"

    @staticmethod
    def unknown(command):
        return f"{command}: command not found"

    @staticmethod
    def parser(command):
        if command.startswith("ls"):
            args = command[2:].strip()
            return Shell.ls(args)
        elif command.startswith("cd"):
            args = command[2:].strip()
            return Shell.cd(args)
        else:
            return Shell.unknown(command.split()[0] if command else "")


hostname = platform.node()
invite = f"{os.getlogin()}@{hostname}: ~ $ "

while True:
    s = input(invite)
    if s.strip() == 'exit':
        break
    result = Shell.parser(s)
    if result:
        print(result)