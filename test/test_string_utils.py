#!/bin/env python3
# Repository:   https://github.com/Python-utilities
# File Name:    test/test_string_utils.py
# Description:  test string utilities
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
from lib.string_utils import squeeze_chars, matches_any, normalise_sentence, roman_to_integer, is_roman_numeral
from lib.logger import LogLevels, set_logger


class BasicFunctionsTests(unittest.TestCase):

    def test_squeeze_chars(self):
        self.assertEqual("", squeeze_chars(source="", squeeze_set="\n\t\r ", replace_with=" "))
        self.assertEqual("", squeeze_chars(source="  \n \n\t ", squeeze_set="\n\t\r ", replace_with=" "))
        self.assertEqual("some text with whitespace",
                         squeeze_chars(source="\t \nsome  \n \n\t text   \r with  whitespace \n",
                                       squeeze_set="\n\t\r ",
                                       replace_with=" "))

    def test_matches_any(self):
        self.assertTrue(matches_any("string to test"))
        self.assertTrue(matches_any("string to test", patterns=""))
        self.assertTrue(matches_any("string to test", patterns="s.*t"))
        self.assertTrue(matches_any("string to test", patterns="s.*to.*t"))
        self.assertFalse(matches_any("string to test", patterns="to"))
        self.assertFalse(matches_any("string to test", patterns="STRING to test"))
        self.assertTrue(matches_any("string to test", patterns=["STRING to test", "s.*"]))

    def test_clean_sentence_string(self):
        sentence = "This website! includes information ,about Project Gutenberg™ to hear about new eBooks."
        expected_clean_sentence = \
            "This website ! includes information , about Project Gutenberg™ to hear about new eBooks ."
        result = normalise_sentence(sentence=sentence)
        self.assertEqual(result, expected_clean_sentence)

    def test_is_roman_numeral(self):
        self.assertTrue(is_roman_numeral("XIV"))
        self.assertTrue(is_roman_numeral("lX"))  # True (case-insensitive)
        self.assertFalse(is_roman_numeral("abc"))

    def test_roman_to_integer(self):
        self.assertEqual(roman_to_integer("III"), 3)
        self.assertEqual(roman_to_integer("IX"), 9)
        self.assertEqual(roman_to_integer("LVIII"), 58)
        self.assertEqual(roman_to_integer("MCMXCIV"), 1994)

        self.assertEqual(roman_to_integer("abc"), -1)


if __name__ == '__main__':
    set_logger(verbosity=LogLevels.WARNING)
    unittest.main()
