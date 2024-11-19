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

# pylint: disable=wrong-import-position
from lib.basic_functions import valid_absolute_path
from lib.logger import LogLevels, set_logger


class BasicFunctionsTests(unittest.TestCase):

    def assertPathRaises(self, paths, protect_patterns=None, should_raise=True):
        """Helper to test if valid_absolute_path raises SystemError for paths."""
        for path in paths:
            with self.subTest(path=path, protect_patterns=protect_patterns):
                if should_raise:
                    with self.assertRaises(SystemError):
                        valid_absolute_path(path, protect_system_patterns=protect_patterns)
                else:
                    try:
                        valid_absolute_path(path, protect_system_patterns=protect_patterns)
                    except SystemError as e:
                        self.fail(f"SystemError raised for path '{path}' with error: {e}")

    def test_valid_absolute_path_protected_patterns(self):
        # Test protected paths
        protected_paths = ["/usr/bin", "/", "/lib32", "/lib64/some/random/sub/dir",
                           "/dev/123", "/proc/x/y/z"]
        self.assertPathRaises(protected_paths)

        # Test unprotected paths
        unprotected_paths = ["/tmp", "/home", "~", "xxx", "dev/123", "/abs/de/f"]
        self.assertPathRaises(unprotected_paths, should_raise=False)

        # Test with specified protection patterns
        protect_patterns = ["/tmp.*", "/hom.*"]
        now_specified_protected_paths = ["/tmp/bin", "/home/user", "/home/user/x/yy/zzz"]
        self.assertPathRaises(now_specified_protected_paths, protect_patterns=protect_patterns)

        now_specified_unprotected_paths = ["/usr/bin", "/", "/lib32", "/lib64/some/random/sub/dir",
                                           "/dev/123", "/proc/x/y/z"]
        self.assertPathRaises(now_specified_unprotected_paths, protect_patterns=protect_patterns, should_raise=False)


if __name__ == '__main__':
    set_logger(verbosity=LogLevels.WARNING)
    unittest.main()
