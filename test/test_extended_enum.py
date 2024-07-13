#!/bin/env python3
# Repository:   https://github.com/Python-utilities
# File Name:    test/test_extended_enums.py
# Description:  test extended enums
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
from enum import auto

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/../../Python-utilities")
if not os.path.isdir(dk_lib_dir):
    raise FileNotFoundError(f"Library directory '{dk_lib_dir}' cannot be found")
sys.path.insert(0, dk_lib_dir)

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

        self.assertEqual(SimpleEnum.SIMPLE1, SimpleEnum.from_string("1"))
        self.assertEqual(SimpleEnum.SIMPLE1, SimpleEnum.from_string("s1"))
        self.assertEqual(SimpleEnum.SIMPLE1, SimpleEnum.from_string("e1"))
        self.assertEqual(SimpleEnum.SIMPLE1, SimpleEnum.from_string("a"))
        self.assertEqual(SimpleEnum.SIMPLE1, SimpleEnum.from_string("aaa"))

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

        self.assertEqual(SimpleFlag.SIMPLE1, SimpleFlag.from_string("1"))
        self.assertEqual(SimpleFlag.SIMPLE1, SimpleFlag.from_string("s1"))
        self.assertEqual(SimpleFlag.SIMPLE1, SimpleFlag.from_string("e1"))
        self.assertEqual(SimpleFlag.SIMPLE1, SimpleFlag.from_string("a"))
        self.assertEqual(SimpleFlag.SIMPLE1, SimpleFlag.from_string("aaa"))

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

        self.assertEqual(SimpleEnum.SIMPLE1, SimpleEnum.from_string("a"))
        self.assertEqual(SimpleEnum.SIMPLE1, SimpleEnum.from_string("x"))
        self.assertEqual(SimpleEnum.SIMPLE1, SimpleEnum.from_string("1"))
        self.assertEqual(SimpleEnum.SIMPLE1, SimpleEnum.from_string("e1"))

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
