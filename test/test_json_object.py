import os
import sys
import unittest

parent_path = f"{os.path.dirname(os.path.abspath(__file__))}/.."
sys.path.insert(0, parent_path)

from lib.exceptions import JsonKeyError, JsonPathFormatError, JsonIndexKeyError, JsonStringKeyError, JsonValueMismatch
from lib.file_system_object import remove
from lib.file_utils import write_file
from lib.json_key_path import JsonKeyPath, JsonIndexKey, JsonStringKey
from lib.json_object import JsonObject
from lib.logger import set_logger, LogLevels


class MyTestCase(unittest.TestCase):
    def test_json_index_keys(self):
        has_thrown = False
        try:
            JsonIndexKey("")
        except JsonIndexKeyError as e:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonIndexKey(-1)
        except JsonIndexKeyError as e:
            has_thrown = True
        self.assertTrue(has_thrown)

        key = JsonIndexKey("^")
        self.assertTrue(key.is_start)
        self.assertFalse(key.is_end)
        self.assertIsNone(key.index)
        self.assertEqual(str(key), "[^]")

        key = JsonIndexKey("$")
        self.assertFalse(key.is_start)
        self.assertTrue(key.is_end)
        self.assertIsNone(key.index)
        self.assertEqual(str(key), "[$]")

        key = JsonIndexKey(0)
        self.assertFalse(key.is_start)
        self.assertFalse(key.is_end)
        self.assertEqual(key.index, 0)
        self.assertEqual(str(key), "[0]")

        key = JsonIndexKey(100)
        self.assertFalse(key.is_start)
        self.assertFalse(key.is_end)
        self.assertEqual(key.index, 100)
        self.assertEqual(str(key), "[100]")

    def test_json_string_keys(self):
        has_thrown = False
        try:
            JsonStringKey("")
        except JsonStringKeyError as e:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonStringKey("[key")
        except JsonStringKeyError as e:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonStringKey("k]ey")
        except JsonStringKeyError as e:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonStringKey(" key")
        except JsonStringKeyError as e:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonStringKey("key ")
        except JsonStringKeyError as e:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonStringKey("/key")
        except JsonStringKeyError as e:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonStringKey("key\n")
        except JsonStringKeyError as e:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonStringKey("\tkey")
        except JsonStringKeyError as e:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonStringKey("key\t")
        except JsonStringKeyError as e:
            has_thrown = True
        self.assertTrue(has_thrown)

    def test_illegal_json_paths(self):
        has_thrown = False
        try:
            JsonKeyPath("")
        except JsonPathFormatError as e:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonKeyPath([])
        except JsonPathFormatError as e:
            has_thrown = True
        self.assertTrue(has_thrown)
        has_thrown = False
        try:
            JsonKeyPath([""])
        except JsonPathFormatError as e:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonKeyPath("key/")
        except JsonPathFormatError as e:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonKeyPath(["key", ""])
        except JsonPathFormatError as e:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonKeyPath("key//path")
        except JsonPathFormatError as e:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonKeyPath(["key", "", "path"])
        except JsonPathFormatError as e:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonKeyPath("[]")
        except JsonPathFormatError as e:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonKeyPath(["[]"])
        except JsonPathFormatError as e:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonKeyPath("[no_integer]")
        except JsonPathFormatError as e:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonKeyPath(["[no_integer]"])
        except JsonPathFormatError as e:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonKeyPath("[-666]")
        except JsonPathFormatError as e:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonKeyPath(["[-666]"])
        except JsonPathFormatError as e:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonKeyPath("key/[-666]/path")
        except JsonPathFormatError as e:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonKeyPath(["key", "[-666]", "path"])
        except JsonPathFormatError as e:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            JsonKeyPath(["key", "sep/ar/ate/d", "path"])
        except JsonPathFormatError as e:
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

    def test_successful_get_and_set(self):
        json_obj = JsonObject(json_str="")
        json_obj.set(keys="key", value="value", force=True)
        self.assertEqual(json_obj.get("key"), "value")
        json_obj.set(keys="key", value="value2", force=False)
        self.assertEqual(json_obj.get("key"), "value2")

        json_obj = JsonObject(json_str="")
        json_obj.set(keys="[0]", value="value", force=True)
        self.assertEqual(json_obj.get("[0]"), "value")
        self.assertEqual(json_obj.get("[^]"), "value")
        self.assertEqual(json_obj.get("[$]"), "value")
        json_obj.set(keys="[0]", value="value2", force=False)
        self.assertEqual(json_obj.get("[0]"), "value2")
        self.assertEqual(json_obj.get("[^]"), "value2")
        self.assertEqual(json_obj.get("[$]"), "value2")
        json_obj.set(keys="[^]", value="value3", force=True)
        self.assertEqual(json_obj.get("[0]"), "value3")
        self.assertEqual(json_obj.get("[^]"), "value3")
        self.assertEqual(json_obj.get("[$]"), "value2")
        json_obj.set(keys="[$]", value="value4", force=True)
        self.assertEqual(json_obj.get("[0]"), "value3")
        self.assertEqual(json_obj.get("[^]"), "value3")
        self.assertEqual(json_obj.get("[$]"), "value4")

        json_obj = JsonObject(json_str="")
        json_obj.set(keys="key/path/[3]/mixed/[$]", value="value", force=True)
        self.assertEqual(json_obj.get("key/path/[3]/mixed/[$]"), "value")
        self.assertEqual(json_obj.get("key/path/[3]/mixed/[0]"), "value")
        self.assertEqual(json_obj.get("key/path/[$]/mixed/[0]"), "value")
        self.assertEqual(json_obj.get("key/path/[2]"), dict())

    def test_failing_get_and_set(self):
        json_obj = JsonObject(json_str="")
        has_thrown = False
        try:
            json_obj.get("key")
        except JsonKeyError as e:
            has_thrown = True
        self.assertTrue(has_thrown)
        self.assertEqual(json_obj.get("key", default="MyDefaultedValue"), "MyDefaultedValue")

        has_thrown = False
        try:
            json_obj.get("[0]")
        except JsonKeyError as e:
            has_thrown = True
        self.assertTrue(has_thrown)
        self.assertEqual(json_obj.get("[0]", default="MyDefaultedValue"), "MyDefaultedValue")

        json_obj = JsonObject(json_str="")
        json_obj.set(keys="key/path/[3]/mixed", value="value", force=True)
        has_thrown = False
        try:
            json_obj.set(keys="key/path/[3]/mixed", value=1234, force=False)
        except JsonValueMismatch as e:
            has_thrown = True
        self.assertTrue(has_thrown)

        json_obj = JsonObject(json_str="")
        json_obj.set(keys="key/path/[3]/mixed/[$]", value="value", force=True)
        has_thrown = False
        try:
            json_obj.set(keys="key/path/[3]/mixed/[$]", value=1234, force=False)
        except JsonValueMismatch as e:
            has_thrown = True
        self.assertTrue(has_thrown)


if __name__ == '__main__':
    set_logger(verbosity=LogLevels.WARNING)
    unittest.main()
