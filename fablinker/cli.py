#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from fablinker.exceptions import ConfigParseError
from fablinker.fabshell import FabShell
from fablinker.utils import ColorPrint, get_cmd_args
from fablinker.constant import __version__
import traceback


def print_welcome():
    wel = '''
            **************************************************************
            Welcome to fablinker V%s
            Please send email to gangly123@163.com if any problem happened.
            Type help for more information.
            Enjoy your operations! (*^_^*)
            **************************************************************
            ''' % __version__
    ColorPrint.blue(wel)


def main():

    try:
        conf_file = get_cmd_args()

        fabshell = FabShell(conf_file)
        print_welcome()
        fabshell.cmdloop()
    except ConfigParseError as e:
        exstr = traceback.format_exc()
        ColorPrint.red(exstr)

    except Exception as e:
        ColorPrint.red(e.message)