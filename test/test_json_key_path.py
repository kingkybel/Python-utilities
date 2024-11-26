#!/bin/env python3
# Repository:   https://github.com/Python-utilities
# File Name:    test/test_json_key_path.py
# Description:  test json key paths
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
from lib.exceptions import JsonPathFormatError, JsonMalformedIndex, JsonMalformedStringKey
from lib.json_key_path import JsonKeyPath, JsonIndexKey, JsonStringKey
from lib.logger import set_logger, LogLevels


class JsonKeyPathTestCase(unittest.TestCase):
    def test_json_index_keys(self):
        has_thrown = False
        try:
            JsonIndexKey("")
        except JsonMalformedIndex:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonIndexKey(-1)
        except JsonMalformedIndex:
            has_thrown = True
        self.assertTrue(has_thrown)

        key = JsonIndexKey("^")
        self.assertTrue(key.is_start_symbol)
        self.assertFalse(key.is_end_symbol)
        self.assertIsNone(key.index)
        self.assertEqual(str(key), "[^]")

        key = JsonIndexKey("$")
        self.assertFalse(key.is_start_symbol)
        self.assertTrue(key.is_end_symbol)
        self.assertIsNone(key.index)
        self.assertEqual(str(key), "[$]")

        key = JsonIndexKey(0)
        self.assertFalse(key.is_start_symbol)
        self.assertFalse(key.is_end_symbol)
        self.assertEqual(key.index, 0)
        self.assertEqual(str(key), "[0]")

        key = JsonIndexKey(100)
        self.assertFalse(key.is_start_symbol)
        self.assertFalse(key.is_end_symbol)
        self.assertEqual(key.index, 100)
        self.assertEqual(str(key), "[100]")

    def test_json_string_keys(self):
        has_thrown = False
        try:
            JsonStringKey("")
        except JsonMalformedStringKey:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonStringKey("[key")
        except JsonMalformedStringKey:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonStringKey("k]ey")
        except JsonMalformedStringKey:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonStringKey(" key")
        except JsonMalformedStringKey:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonStringKey("key ")
        except JsonMalformedStringKey:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonStringKey("/key")
        except JsonMalformedStringKey:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonStringKey("key\n")
        except JsonMalformedStringKey:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonStringKey("\tkey")
        except JsonMalformedStringKey:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonStringKey("key\t")
        except JsonMalformedStringKey:
            has_thrown = True
        self.assertTrue(has_thrown)

    def test_illegal_json_paths(self):
        has_thrown = False
        try:
            JsonKeyPath("")
        except JsonPathFormatError:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonKeyPath([])
        except JsonPathFormatError:
            has_thrown = True
        self.assertTrue(has_thrown)
        has_thrown = False
        try:
            JsonKeyPath([""])
        except JsonPathFormatError:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonKeyPath("key/")
        except JsonPathFormatError:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonKeyPath(["key", ""])
        except JsonPathFormatError:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonKeyPath("key//path")
        except JsonPathFormatError:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonKeyPath(["key", "", "path"])
        except JsonPathFormatError:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonKeyPath("[]")
        except JsonPathFormatError:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonKeyPath(["[]"])
        except JsonPathFormatError:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonKeyPath("[no_integer]")
        except JsonPathFormatError:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonKeyPath(["[no_integer]"])
        except JsonPathFormatError:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonKeyPath("[-666]")
        except JsonPathFormatError:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonKeyPath(["[-666]"])
        except JsonPathFormatError:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonKeyPath("key/[-666]/path")
        except JsonPathFormatError:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonKeyPath(["key", "[-666]", "path"])
        except JsonPathFormatError:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonKeyPath(["key", "sep/ar/ate/d", "path"])
        except JsonPathFormatError:
            has_thrown = True
        self.assertTrue(has_thrown)

    def test_legal_json_paths(self):
        json_keys = JsonKeyPath("key")
        self.assertEqual(str(json_keys), "key")

        json_keys = JsonKeyPath(["key"])
        self.assertEqual(str(json_keys), "key")

        json_keys = JsonKeyPath("key/path")
        self.assertEqual(str(json_keys), "key/path")

        json_keys = JsonKeyPath(["key", "path"])
        self.assertEqual(str(json_keys), "key/path")

        json_keys = JsonKeyPath("[0]")
        self.assertEqual(str(json_keys), "[0]")

        json_keys = JsonKeyPath(["[0]"])
        self.assertEqual(str(json_keys), "[0]")

        json_keys = JsonKeyPath("[1234]")
        self.assertEqual(str(json_keys), "[1234]")

        json_keys = JsonKeyPath(["[1234]"])
        self.assertEqual(str(json_keys), "[1234]")

        json_keys = JsonKeyPath("[^]")
        self.assertEqual(str(json_keys), "[^]")

        json_keys = JsonKeyPath(["[^]"])
        self.assertEqual(str(json_keys), "[^]")

        json_keys = JsonKeyPath("[$]")
        self.assertEqual(str(json_keys), "[$]")

        json_keys = JsonKeyPath(["[$]"])
        self.assertEqual(str(json_keys), "[$]")

        json_keys = JsonKeyPath("key/[$]/path/[123]/xxx/[$]/yyy")
        self.assertEqual(str(json_keys), "key/[$]/path/[123]/xxx/[$]/yyy")

        json_keys = JsonKeyPath(["key", "[$]", "path", "[123]", "xxx", "[$]", "yyy"])
        self.assertEqual(str(json_keys), "key/[$]/path/[123]/xxx/[$]/yyy")


if __name__ == '__main__':
    set_logger(verbosity=LogLevels.WARNING)
    unittest.main()
