import os
import sys
import unittest
from enum import auto

parent_path = f"{os.path.dirname(os.path.abspath(__file__))}/.."
sys.path.insert(0, parent_path)

from lib.exceptions import ExtendedEnumError
from lib.extended_enum import ExtendedEnum, EnumListType, ExtendedFlag
from lib.logger import LogLevels, set_logger


class ExtendedEnumTests(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self):
        return super().tearDown()

    def test_create_enum(self):
        class SimpleEnum(ExtendedEnum):
            SIMPLE1 = 0
            SIMPLE2 = 1
            SIMPLE3 = 2

        self.assertListEqual(SimpleEnum.list(EnumListType.NAME), ["SIMPLE1", "SIMPLE2", "SIMPLE3"])
        self.assertListEqual(SimpleEnum.list(EnumListType.STR), ["SimpleEnum.SIMPLE1",
                                                                 "SimpleEnum.SIMPLE2",
                                                                 "SimpleEnum.SIMPLE3"])
        self.assertListEqual(SimpleEnum.list(EnumListType.VALUE), [0, 1, 2])
        self.assertListEqual(SimpleEnum.list(EnumListType.ITEM), [SimpleEnum.SIMPLE1,
                                                                  SimpleEnum.SIMPLE2,
                                                                  SimpleEnum.SIMPLE3])

    def test_create_flag(self):
        class SimpleFlag(ExtendedFlag):
            SIMPLE1 = auto()
            SIMPLE2 = auto()
            SIMPLE3 = auto()

        self.assertListEqual(SimpleFlag.list(EnumListType.NAME), ["SIMPLE1", "SIMPLE2", "SIMPLE3"])
        self.assertListEqual(SimpleFlag.list(EnumListType.STR), ["SimpleFlag.SIMPLE1",
                                                                 "SimpleFlag.SIMPLE2",
                                                                 "SimpleFlag.SIMPLE3"])
        self.assertListEqual(SimpleFlag.list(EnumListType.VALUE), [1, 2, 4])
        self.assertListEqual(SimpleFlag.list(EnumListType.ITEM), [SimpleFlag.SIMPLE1,
                                                                  SimpleFlag.SIMPLE2,
                                                                  SimpleFlag.SIMPLE3])

    def test_enum_from_string(self):
        class SimpleEnum(ExtendedEnum):
            SIMPLE1 = 0
            SIMPLE2 = 1
            SIMPLE3 = 2

            def __str__(self):
                match self:
                    case SimpleEnum.SIMPLE1:
                        return "aaa"
                    case SimpleEnum.SIMPLE2:
                        return "bbb"
                    case SimpleEnum.SIMPLE3:
                        return "ccc"

        self.assertEquals(SimpleEnum.SIMPLE1, SimpleEnum.from_string("1"))
        self.assertEquals(SimpleEnum.SIMPLE1, SimpleEnum.from_string("s1"))
        self.assertEquals(SimpleEnum.SIMPLE1, SimpleEnum.from_string("e1"))
        self.assertEquals(SimpleEnum.SIMPLE1, SimpleEnum.from_string("a"))
        self.assertEquals(SimpleEnum.SIMPLE1, SimpleEnum.from_string("aaa"))

    def test_flag_from_string(self):
        class SimpleFlag(ExtendedFlag):
            SIMPLE1 = auto()
            SIMPLE2 = auto()
            SIMPLE3 = auto()

            def __str__(self):
                match self:
                    case SimpleFlag.SIMPLE1:
                        return "aaa"
                    case SimpleFlag.SIMPLE2:
                        return "bbb"
                    case SimpleFlag.SIMPLE3:
                        return "ccc"

        self.assertEquals(SimpleFlag.SIMPLE1, SimpleFlag.from_string("1"))
        self.assertEquals(SimpleFlag.SIMPLE1, SimpleFlag.from_string("s1"))
        self.assertEquals(SimpleFlag.SIMPLE1, SimpleFlag.from_string("e1"))
        self.assertEquals(SimpleFlag.SIMPLE1, SimpleFlag.from_string("a"))
        self.assertEquals(SimpleFlag.SIMPLE1, SimpleFlag.from_string("aaa"))

    def test_enum_from_string_with_string_conversion(self):
        class SimpleEnum(ExtendedEnum):
            SIMPLE1 = "xxx"
            SIMPLE2 = "yyy"
            SIMPLE3 = "zzz"

            def __str__(self):
                match self:
                    case SimpleEnum.SIMPLE1:
                        return "aaa"
                    case SimpleEnum.SIMPLE2:
                        return "bbb"
                    case SimpleEnum.SIMPLE3:
                        return "ccc"

        self.assertEquals(SimpleEnum.SIMPLE1, SimpleEnum.from_string("a"))
        self.assertEquals(SimpleEnum.SIMPLE1, SimpleEnum.from_string("x"))
        self.assertEquals(SimpleEnum.SIMPLE1, SimpleEnum.from_string("1"))
        self.assertEquals(SimpleEnum.SIMPLE1, SimpleEnum.from_string("e1"))

    def test_enum_no_match(self):
        class SimpleEnum(ExtendedEnum):
            SIMPLE1 = "xxx"
            SIMPLE2 = "yyy"
            SIMPLE3 = "zzz"

            def __str__(self):
                match self:
                    case SimpleEnum.SIMPLE1:
                        return "aaa"
                    case SimpleEnum.SIMPLE2:
                        return "bbb"
                    case SimpleEnum.SIMPLE3:
                        return "ccc"

        has_thrown = False
        try:
            SimpleEnum.from_string("xy")
        except ExtendedEnumError as e:
            print(e.message)
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            SimpleEnum.from_string("SIM")
        except ExtendedEnumError as e:
            print(e.message)
            has_thrown = True
        self.assertTrue(has_thrown)

    def test_flag_no_match(self):
        class SimpleFlag(ExtendedFlag):
            SIMPLE1 = auto()
            SIMPLE2 = auto()
            SIMPLE3 = auto()

            def __str__(self):
                match self:
                    case SimpleFlag.SIMPLE1:
                        return "aaa"
                    case SimpleFlag.SIMPLE2:
                        return "bbb"
                    case SimpleFlag.SIMPLE3:
                        return "ccc"

        has_thrown = False
        try:
            SimpleFlag.from_string("12")
        except ExtendedEnumError as e:
            has_thrown = True
        self.assertTrue(has_thrown)

        has_thrown = False
        try:
            SimpleFlag.from_string("SIM")
        except ExtendedEnumError as e:
            has_thrown = True
        self.assertTrue(has_thrown)


if __name__ == '__main__':
    set_logger(verbosity=LogLevels.WARNING)
    unittest.main()
