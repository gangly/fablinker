#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import tempfile
import unittest

# 避免导入fabric相关模块
sys.modules['fabric.api'] = type('obj', (object,), {})()
sys.modules['fabric.colors'] = type('obj', (object,), {"red": lambda x: x, "blue": lambda x: x, "yellow": lambda x: x})()

from fablinker.utils import parse_config
from fablinker.exceptions import ConfigParseError


class TestUtils(unittest.TestCase):
    
    def test_parse_config(self):
        # 创建一个临时配置文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write("""
[baseconf]
user = test
password = test123
parallel = False

[host_groups]
Group1 = [192.168.1.1, 192.168.1.2]
Group2 = [192.168.1.3, 192.168.1.4]
""")
            temp_config = f.name
        
        try:
            base_conf, host_groups, current_group = parse_config(temp_config)
            self.assertEqual(base_conf['user'], 'test')
            self.assertEqual(base_conf['password'], 'test123')
            self.assertEqual(base_conf['parallel'], 'False')
            self.assertIn('Group1', host_groups)
            self.assertIn('Group2', host_groups)
            self.assertEqual(current_group, 'Group1')
        finally:
            os.unlink(temp_config)
    
    def test_parse_config_invalid(self):
        # 创建一个无效的配置文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write("""
[baseconf]
user = test

# 缺少host_groups部分
""")
            temp_config = f.name
        
        try:
            with self.assertRaises(ConfigParseError):
                parse_config(temp_config)
        finally:
            os.unlink(temp_config)


if __name__ == '__main__':
    unittest.main()
