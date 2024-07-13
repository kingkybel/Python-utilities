#!/bin/env python3
# Repository:   https://github.com/Python-utilities
# File Name:    test/test_basic_functions.py
# Description:  test basic functions
#
# Copyright (C) 2024 Dieter J Kybelksties <github@kybelksties.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# @date: 2024-07-13
# @author: Dieter J Kybelksties


import os
import sys
import unittest

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/../../Python-utilities")
if not os.path.isdir(dk_lib_dir):
    raise FileNotFoundError(f"Library directory '{dk_lib_dir}' cannot be found")
sys.path.insert(0, dk_lib_dir)

from lib.basic_functions import valid_absolute_path
from lib.logger import LogLevels, set_logger


class BasicFunctionsTests(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self):
        return super().tearDown()

    def test_valid_absolute_path_protected_patterns(self):
        protected_paths = ["/usr/bin", "/", "/lib32", "/lib64/some/random/sub/dir",
                           "/dev/123", "/proc/x/y/z"]
        for path in protected_paths:
            has_thrown = False
            try:
                valid_absolute_path(path)
            except SystemError as e:
                # print(e)
                has_thrown = True
            self.assertTrue(has_thrown)

        unprotected_paths = ["/tmp", "/home", "~", "xxx",
                             "dev/123", "/abs/de/f"]

        for path in unprotected_paths:
            has_thrown = False
            valid_path = None
            try:
                valid_path = valid_absolute_path(path)
            except SystemError as e:
                # print(e)
                has_thrown = True
            # print(valid_path)
            self.assertFalse(has_thrown)

        protect_patterns = ["/tmp.*", "/hom.*"]
        now_specified_protected_paths = ["/tmp/bin", "/home/user", "/home/user/x/yy/zzz"]
        for path in now_specified_protected_paths:
            has_thrown = False
            try:
                valid_absolute_path(path, protect_system_patterns=protect_patterns)
            except SystemError as e:
                # print(e)
                has_thrown = True
            self.assertTrue(has_thrown)

        now_specified_unprotected_paths = ["/usr/bin", "/", "/lib32", "/lib64/some/random/sub/dir",
                                           "/dev/123", "/proc/x/y/z"]
        for path in now_specified_unprotected_paths:
            has_thrown = False
            try:
                valid_absolute_path(path, protect_system_patterns=protect_patterns)
            except SystemError as e:
                print(e)
                has_thrown = True
            self.assertFalse(has_thrown)


if __name__ == '__main__':
    set_logger(verbosity=LogLevels.WARNING)
    unittest.main()
