#!/bin/env python3
# Repository:   https://github.com/Python-utilities
# File Name:    test/test_json_object.py
# Description:  test json objects
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
from lib.exceptions import JsonKeyStringRequired, JsonValueMismatch, JsonIndexRequired
from lib.file_system_object import remove
from lib.file_utils import write_file
from lib.json_object import JsonObject
from lib.logger import set_logger, LogLevels


class JsonObjectTestCase(unittest.TestCase):
    def test_json_object_creation(self):
        json_obj = JsonObject(json_str="")
        self.assertEqual(str(json_obj), "{}")

        json_obj = JsonObject(json_str="{}")
        self.assertEqual(str(json_obj), "{}")

        json_obj = JsonObject(json_str="[]")
        self.assertEqual(str(json_obj), "[]")

        json_obj = JsonObject(json_str="""{"key":"value"}""")
        self.assertEqual(json_obj.get('key'), "value")

        json_obj = JsonObject(json_str="""["val1","val2"]""")
        self.assertEqual(json_obj.get('[0]'), "val1")
        self.assertEqual(json_obj.get('[1]'), "val2")

        json_obj = JsonObject(json_obj={"key": "value"})
        self.assertEqual(json_obj.get('key'), "value")

        json_obj = JsonObject(json_obj=["val1", "val2"])
        self.assertEqual(json_obj.get('[0]'), "val1")
        self.assertEqual(json_obj.get('[1]'), "val2")

        json_file = "/tmp/test_json.json"
        write_file(filename=json_file, content="""
        {
            "list": [
                1, 2, 3
            ]
        }
        """)
        json_obj = JsonObject(filename=json_file)
        self.assertEqual(json_obj.get("list/[1]"), 2)
        remove("/tmp/test_json.json")

    def test_key_exists(self):
        json_obj = JsonObject(json_obj={"key": ["val"]})
        self.assertTrue(json_obj.key_exists("key"))
        self.assertTrue(json_obj.key_exists("key/[0]"))
        self.assertFalse(json_obj.key_exists("key2"))
        self.assertFalse(json_obj.key_exists("key/[1]"))

    def test_changing_root_type(self):
        json_obj = JsonObject(json_str="{}")
        self.assertTrue(isinstance(json_obj.get(), dict))

        json_obj.set("[0]", "value", force=True)
        self.assertTrue(isinstance(json_obj.get(), list))

        json_obj.set("key", "value", force=True)
        self.assertTrue(isinstance(json_obj.get(), dict))

    def test_changing_leaf_type(self):
        json_obj = JsonObject(json_str='{"nums":[1,2,3]}')
        self.assertTrue(isinstance(json_obj.get("nums"), list))
        with self.assertRaises(JsonValueMismatch):
            json_obj.set("nums",  {"key": "value"}, force=False)
        json_obj.set("nums",  {"key": "value"}, force=True)

        json_obj.set("nums", ["value"], force=True)
        self.assertTrue(isinstance(json_obj.get("nums"), list))

    def test_get_with_compatible_path(self):
        json_obj = JsonObject(json_str="{}")
        self.assertEqual(json_obj.get(), {})

        json_obj = JsonObject(json_str="[]")
        self.assertEqual(json_obj.get(), [])

        json_obj = JsonObject(json_str='{"key":"value"}')
        self.assertEqual(json_obj.get("key"), 'value')

        json_obj = JsonObject(json_str='[0, "value"]')
        self.assertEqual(json_obj.get("[0]"), 0)
        self.assertEqual(json_obj.get("[1]"), "value")

        json_obj = JsonObject(json_obj={"key": "value", "key2": [0.0, 1.1, 2.2]})
        self.assertEqual(json_obj.get("key2/[0]"), 0.0)
        self.assertEqual(json_obj.get("key2/[1]"), 1.1)
        self.assertEqual(json_obj.get("key2/[^]"), 0.0)
        self.assertEqual(json_obj.get("key2/[$]"), 2.2)

    def test_get_with_incompatible_path(self):
        json_obj = JsonObject(json_str='{"key":"value"}')
        with self.assertRaises(JsonKeyStringRequired):
            json_obj.get("[0]")

        json_obj = JsonObject(json_str='["one","two"]')
        with self.assertRaises(JsonIndexRequired):
            json_obj.get("one")

        json_obj = JsonObject(json_obj={"key": "value", "key2": [0.0, 1.1, 2.2]})
        with self.assertRaises(JsonIndexRequired):
            json_obj.get("key2/one")

        json_obj = JsonObject(json_obj=["key", "value", {"key2": [0.0, 1.1, 2.2]}])
        with self.assertRaises(JsonIndexRequired):
            json_obj.get("key2/[0]")

    def test_get_with_default(self):
        json_obj = JsonObject(json_str="{}")
        self.assertEqual(json_obj.get("key", "default"), "default")
        with self.assertRaises(JsonKeyStringRequired):
            json_obj.get("[0]")

        json_obj = JsonObject(json_str="[]")
        self.assertEqual(json_obj.get("[0]", "default"), "default")
        with self.assertRaises(JsonIndexRequired):
            json_obj.get("key")

        json_obj = JsonObject(json_str='{"key":"value"}')
        self.assertEqual(json_obj.get("non-existing-key", default="default"), "default")

        json_obj = JsonObject(json_obj=["key", "value"])
        with self.assertRaises(JsonIndexRequired):
            self.assertEqual(json_obj.get("key", "default"), "default")

        json_obj = JsonObject(json_obj={"key": [1.1, 2.2, 3.3]})
        self.assertEqual(json_obj.get("key/[4]", default=-1.0), -1.0)

        json_obj = JsonObject(json_obj=["key", [1.1, {"key2": 2.2}, 3.3]])
        self.assertEqual(json_obj.get("[1]/[1]/key3", default={}), {})
        self.assertEqual(json_obj.get("[1]/[5]/key3", default={}), {})

    def test_simple_get_and_set(self):
        json_obj = JsonObject(json_obj={})
        # change the root from dict to list and set a value
        json_obj.set(keys="[0]", value="value", force=True)
        self.assertEqual(json_obj.get("[0]"), "value")
        self.assertEqual(json_obj.get("[^]"), "value")
        self.assertEqual(json_obj.get("[$]"), "value")

        # overwriting the value without force
        json_obj.set(keys="[0]", value="value2", force=False)
        self.assertEqual(json_obj.get("[0]"), "value2")
        self.assertEqual(json_obj.get("[^]"), "value2")
        self.assertEqual(json_obj.get("[$]"), "value2")

        # [^] should insert an element at the front and not overwrite the existing element
        json_obj.set(keys="[^]", value="value3", force=True)
        self.assertEqual(json_obj.get("[0]"), "value3")
        self.assertEqual(json_obj.get("[^]"), "value3")
        self.assertEqual(json_obj.get("[$]"), "value2")

        # [$] should insert an element at the front and not overwrite the existing element
        json_obj.set(keys="[$]", value="value4", force=True)
        self.assertEqual(json_obj.get("[0]"), "value3")
        self.assertEqual(json_obj.get("[^]"), "value3")
        self.assertEqual(json_obj.get("[$]"), "value4")

    def test_more_complicated_get_and_set(self):
        json_obj = JsonObject(json_obj={})
        json_obj.set(keys="l0_k0/[0]/l3_k0", value="v0", force=True)
        self.assertEqual(json_obj.get("l0_k0/[0]/l3_k0"), "v0")
        self.assertEqual(json_obj.get("l0_k0/[^]/l3_k0"), "v0")
        self.assertEqual(json_obj.get("l0_k0/[$]/l3_k0"), "v0")

        # insert another list item at level 1
        json_obj.set(keys="l0_k0/[^]/l3_k0", value="v1", force=True)
        self.assertEqual(json_obj.get("l0_k0/[0]/l3_k0"), "v1")
        self.assertEqual(json_obj.get("l0_k0/[^]/l3_k0"), "v1")
        self.assertEqual(json_obj.get("l0_k0/[$]/l3_k0"), "v0")

        # append another list item at level 1
        json_obj.set(keys="l0_k0/[$]/l3_k0", value="v2", force=True)
        self.assertEqual(json_obj.get("l0_k0/[0]/l3_k0"), "v1")
        self.assertEqual(json_obj.get("l0_k0/[^]/l3_k0"), "v1")
        self.assertEqual(json_obj.get("l0_k0/[$]/l3_k0"), "v2")
        self.assertEqual(json_obj.get("l0_k0/[1]/l3_k0"), "v0")

    def test_failing_get_and_set(self):
        json_obj = JsonObject(json_obj={})
        with self.assertRaises(JsonKeyStringRequired):
            json_obj.get("key")
        self.assertEqual(json_obj.get("key", default="MyDefaultedValue"), "MyDefaultedValue")

        with self.assertRaises(JsonKeyStringRequired):
            json_obj.get("[0]")
        with self.assertRaises(JsonKeyStringRequired):
            json_obj.get("[0]", default="MyDefaultedValue")

        json_obj = JsonObject(json_obj={})
        json_obj.set(keys="key/path/[3]/mixed", value="value", force=True)
        with self.assertRaises(JsonValueMismatch):
            json_obj.set(keys="key/path/[3]/mixed", value=1234, force=False)

        json_obj = JsonObject(json_str="")
        json_obj.set(keys="key/path/[3]/mixed/[$]", value="value", force=True)

        with self.assertRaises(JsonValueMismatch):
            json_obj.set(keys="key/path/[3]/mixed/[$]", value=1234, force=False)

    if __name__ == '__main__':
        set_logger(verbosity=LogLevels.WARNING)
        unittest.main()
