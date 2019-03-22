#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os

# from utils import get_full_path

__version__ = '1.1.10'

CONF_FILE_NAME = 'fabconf.ini'

HCMD_DIR = os.path.expanduser(os.path.join('~', '.fablinker'))
CONFIG_FILE = os.path.join(HCMD_DIR, CONF_FILE_NAME)

CMD_PROMPT = '>>'
