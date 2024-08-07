#!/bin/env python3
# Repository:   https://github.com/Python-utilities
# File Name:    test/test_file_system_object.py
# Description:  test file_system objects
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
import shutil
import sys
import unittest
from pathlib import Path

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/../../Python-utilities")
if not os.path.isdir(dk_lib_dir):
    raise FileNotFoundError(f"Library directory '{dk_lib_dir}' cannot be found")
sys.path.insert(0, dk_lib_dir)

from lib.file_system_object import make_path_list, glob_path_patterns, GlobMode, mkdir, remove, touch, pushdir, \
    current_dir, popdir
from lib.logger import LogLevels, set_logger


class FileSystemObjectTests(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self):
        return super().tearDown()

    def test_make_path_list(self):
        path1 = Path("/xyz/abc")
        path2 = Path("/usr/bin")
        path3 = "/home/user"
        self.assertEqual(["/xyz/abc"], make_path_list(path1))
        self.assertEqual(["/home/user"], make_path_list(path3))
        self.assertListEqual(["/xyz/abc", "/usr/bin", "/home/user"], make_path_list([path1, path2, path3]))

        has_thrown = False
        try:
            make_path_list("")
        except SystemExit:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            make_path_list([])
        except SystemExit:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            make_path_list([path1, "", path3])
        except SystemExit:
            has_thrown = True
        self.assertTrue(has_thrown)

        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            make_path_list([path1, [], path3])
        except SystemExit:
            has_thrown = True
        self.assertTrue(has_thrown)

    def test_glob_path_patterns_successful(self):
        shutil.rmtree("/tmp/test-glob", ignore_errors=True)
        dir1 = "/tmp/test-glob/sub/sub1"
        dir2 = "/tmp/test-glob/sub/sub2"
        dir3 = "/tmp/test-glob/sub/DIR3"
        os.makedirs(dir1, exist_ok=True)
        os.makedirs(dir2, exist_ok=True)
        os.makedirs(dir3, exist_ok=True)
        self.assertListEqual(["/tmp/test-glob"], glob_path_patterns("/tmp/test-glob"))
        self.assertListEqual(["/tmp/test-glob"], glob_path_patterns("/tmp/*-glob"))
        self.assertListEqual([dir2], glob_path_patterns("/tmp/*-glob/*/*2"))
        self.assertListEqual([dir1, dir2], sorted(glob_path_patterns("/tmp/*-glob/sub/sub*")))

        expected = [dir1, dir2]
        expected.sort()
        globbed = glob_path_patterns("/tmp/*-glob/*/sub*")
        globbed.sort()
        self.assertListEqual(expected, globbed)

        expected = [dir1, dir2, dir3]
        expected.sort()
        globbed = glob_path_patterns("/tmp/*-glob/*/*")
        globbed.sort()
        self.assertListEqual(expected, globbed)
        shutil.rmtree("/tmp/test-glob", ignore_errors=True)

    def test_glob_path_patterns_failure(self):
        shutil.rmtree("/tmp/test-glob", ignore_errors=True)
        dir1 = "/tmp/test-glob/sub/sub1"
        dir2 = "/tmp/test-glob/sub/sub2"
        dir3 = "/tmp/test-glob/sub/DIR3"
        os.makedirs(dir1, exist_ok=True)
        os.makedirs(dir2, exist_ok=True)
        os.makedirs(dir3, exist_ok=True)

        has_thrown = False
        try:
            glob_path_patterns("/tmp/test-glob/sub/subXXX")
        except FileNotFoundError:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        returned_list = list()
        try:
            returned_list = glob_path_patterns("/tmp/test-glob/sub/subXXX", glob_mode=GlobMode.KEEP_EMPTY)
        except FileNotFoundError:
            has_thrown = True
        self.assertFalse(has_thrown)
        self.assertEqual(1, len(returned_list))
        self.assertEqual(returned_list[0], "/tmp/test-glob/sub/subXXX")

        shutil.rmtree("/tmp/test-glob", ignore_errors=True)

    def test_touch_mkdir_remove(self):
        tmp_dir = "/tmp/test_mkdir_touch_remove"
        shutil.rmtree(tmp_dir, ignore_errors=True)

        mkdir(f"{tmp_dir}/sub1")
        self.assertTrue(os.path.isdir(f"{tmp_dir}/sub1"))
        remove(f"{tmp_dir}/sub1")
        self.assertFalse(os.path.exists(f"{tmp_dir}/sub1"))

        mkdir([f"{tmp_dir}/sub1", f"{tmp_dir}/sub2"])
        self.assertTrue(os.path.isdir(f"{tmp_dir}/sub1"))
        self.assertTrue(os.path.isdir(f"{tmp_dir}/sub2"))
        remove([f"{tmp_dir}/sub1", f"{tmp_dir}/sub2"])
        self.assertFalse(os.path.exists(f"{tmp_dir}/sub1"))
        self.assertFalse(os.path.exists(f"{tmp_dir}/sub2"))

        touch(f"{tmp_dir}/text.txt")
        self.assertTrue(os.path.isfile(f"{tmp_dir}/text.txt"))
        remove(f"{tmp_dir}/text.txt")
        self.assertFalse(os.path.exists(f"{tmp_dir}/text.txt"))

        shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_pwd_pushdir_popdir(self):
        tmp_dir = "/tmp/test_pwd_pushdir_popdir"
        mkdir([f"{tmp_dir}/sub1/sub11", f"{tmp_dir}/sub1/sub12", f"{tmp_dir}/sub2/sub21", f"{tmp_dir}/sub2/sub22"])
        pushdir(tmp_dir)
        self.assertEqual(current_dir(), tmp_dir)

        pushdir(f"{tmp_dir}/sub1/sub11")
        pushdir(f"{tmp_dir}/sub1/sub12")
        pushdir(f"{tmp_dir}/sub2/sub21")
        pushdir(f"{tmp_dir}/sub2/sub22")
        self.assertEqual(current_dir(), f"{tmp_dir}/sub2/sub22")
        popdir()
        self.assertEqual(current_dir(), f"{tmp_dir}/sub2/sub21")
        popdir()
        self.assertEqual(current_dir(), f"{tmp_dir}/sub1/sub12")
        popdir()
        self.assertEqual(current_dir(), f"{tmp_dir}/sub1/sub11")
        popdir()
        self.assertEqual(current_dir(), tmp_dir)

        remove(tmp_dir)


if __name__ == '__main__':
    set_logger(verbosity=LogLevels.WARNING)
    unittest.main()
