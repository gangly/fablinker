#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import argparse

from fabric.colors import *

from fablinker.compat import config_parser
# from fablinker.constant import CONFIG_FILE
from fablinker.constant import CONFIG_FILE, __version__
from fablinker.exceptions import ConfigParseError, FileNotFoundError


class ColorPrint(object):
    @staticmethod
    def red(msg):
        print(red(msg))

    @staticmethod
    def blue(msg):
        print(blue(msg))

    @staticmethod
    def yellow(msg):
        print(yellow(msg))


def get_cmd_args():
    parser = argparse.ArgumentParser(description='Fablinker is a tool for operating servers!')

    parser.add_argument('-f', action='store', dest='conf_file', help='server hosts file, each line descript a server')
    parser.add_argument("-v", "--version", help="show the version of fablinker", action="store_true")
    cmd_args = parser.parse_args()

    if cmd_args.version:
        print(__version__)
        exit(0)
    conf_file = cmd_args.conf_file if cmd_args.conf_file else CONFIG_FILE
    if not os.path.isfile(conf_file):
        raise FileNotFoundError("config file not found!")
    return conf_file


def parse_config(conf_file):
    base_conf = {}
    host_groups = {}
    try:
        cf = config_parser()
        cf.optionxform = str
        cf.read(conf_file)
        baseconf = cf.options('baseconf')
        for key in baseconf:
            base_conf[key] = cf.get('baseconf', key)
        groups = cf.options('host_groups')
        if len(groups) < 1:
            raise ConfigParseError("parse config file error, hosts not find!")
        current_group = groups[0]

        for group in groups:
            hosts = cf.get('host_groups', group)
            hosts = hosts.replace('[', '').replace(']', '').replace(' ', '').split(',')
            host_groups[group] = hosts
        return base_conf, host_groups, current_group
    except Exception as e:
        raise ConfigParseError("parse config file error, %s" % e)


def get_full_path(path):
    fullpath = os.path.expandvars(path)
    fullpath = os.path.expanduser(fullpath)
    fullpath = os.path.abspath(fullpath)
    return fullpath

