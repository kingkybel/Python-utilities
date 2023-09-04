import os
import sys
import unittest

parent_path = f"{os.path.dirname(os.path.abspath(__file__))}/.."
sys.path.insert(0, parent_path)

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
