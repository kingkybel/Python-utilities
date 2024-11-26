# Repository:   https://github.com/Python-utilities
# File Name:    lib/json_key_path.py
# Description:  formalizing paths to keys in a JSON object
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

from __future__ import annotations

import collections.abc
import os
import sys
from abc import ABC, abstractmethod
from typing import Iterable

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/../../Python-utilities")
if not os.path.isdir(dk_lib_dir):
    raise FileNotFoundError(f"Library directory '{dk_lib_dir}' cannot be found")
sys.path.insert(0, dk_lib_dir)

# pylint: disable=wrong-import-position
from lib.basic_functions import is_empty_string
from lib.exceptions import JsonPathFormatError, JsonMalformedIndex, JsonMalformedStringKey, \
    JsonMalformedKey
from lib.string_utils import matches_any


class JsonKey(ABC):
    @abstractmethod
    def get(self) -> int | str:
        pass


class JsonIndexKey(JsonKey):
    START_SYMBOL = -1
    END_SYMBOL = -2
    def __init__(self, index: (str | int)):
        self.is_start_symbol = False
        self.is_end_symbol = False
        self.index = None
        if isinstance(index, str):
            if index == "^":
                self.is_start_symbol = True
            elif index == "$":
                self.is_end_symbol = True
            else:
                try:
                    self.index = int(index)
                except ValueError:
                    raise JsonMalformedIndex(index) from ValueError
        else:
            self.index = index

        if self.index is not None and self.index < 0:
            raise JsonMalformedIndex(self.index)

    def __str__(self):
        if self.is_start_symbol:
            return "[^]"
        if self.is_end_symbol:
            return "[$]"
        return f"[{self.index}]"

    def get(self) -> int | str:
        """
        Get the list index as int.
        In case of start- or end- symbol, return 0.
        :return: index as int
        """
        if self.is_start_symbol or self.is_end_symbol:
            return 0
        return int(self.index)


    def extend_object(self, list_container: list, element: object) -> list:
        """
        Extend the list by inserting or appending elements depending on index/start-/end-values.
        :param list_container: the list to extend.
        :param element: the element to insert/append.
        :return: the extended list.
        """
        if self.is_start_symbol:
            list_container.insert(0, element)
            return list_container
        if self.is_end_symbol:
            list_container.append(element)
            return list_container
        for _ in range(self.index - len(list_container)):
            list_container.append(element)
        return list_container

class JsonStringKey(JsonKey):
    def __init__(self, key: str):
        if is_empty_string(key):
            raise JsonMalformedStringKey(key)
        if matches_any(search_string=key, patterns=[".* $", ".*\t$",
                                                    "^ .*", "^\t.*",
                                                    ".*\n.*",
                                                    ".*/.*",
                                                    r".*\[.*",
                                                    r".*\].*",
                                                    r".*\".*"]):
            raise JsonMalformedStringKey(key=key)
        self.key = key

    def __str__(self):
        return self.key

    def get(self) -> int | str:
        """
        Get the dict key as str.
        :return:
        """
        return str(self.key)


class JsonKeyPath(collections.abc.Sized, ABC, Iterable[JsonKey]):
    def __init__(self, key_path: (str | list) = None):
        self.list_of_keys = []
        if isinstance(key_path, str):
            key_path = key_path.split("/")
        if len(key_path) == 0:
            raise JsonPathFormatError(path_string="<EMPTY-PATH!!>")
        for partial in key_path:
            if not isinstance(partial, (str | int)):
                raise JsonPathFormatError(path_string="/".join(key_path),
                                          extra_info="All elements in key-path list must be of type string or int, "
                                                     f"but type({partial}) is {type(partial)}")
            try:
                if isinstance(partial, str) and partial.startswith("[") and partial.endswith("]"):
                    partial = partial[1:len(partial) - 1]
                    self.list_of_keys.append(JsonIndexKey(partial))
                else:
                    self.list_of_keys.append(JsonStringKey(str(partial)))
            except JsonMalformedKey as e:
                raise JsonPathFormatError(path_string="/".join(key_path), extra_info=e.message) from e

    def __str__(self):
        return "/".join([str(key) for key in self.list_of_keys])

    def __sizeof__(self):
        return len(self.list_of_keys)

    def __getitem__(self, item):
        return self.list_of_keys[item]

    def __iter__(self):
        for key in self.list_of_keys:
            yield key

    def __len__(self):
        return len(self.list_of_keys)

    def __contains__(self, item):
        return item in self.list_of_keys

    def __eq__(self, other):
        if isinstance(other, JsonKeyPath):
            return self.list_of_keys == other.list_of_keys
        return False

    def key_list(self):
        """
        Get the list of keys.
        :return: the list of keys.
        """
        return self.list_of_keys
