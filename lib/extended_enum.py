# Repository:   https://github.com/Python-utilities
# File Name:    lib/extended_enum.py
# Description:  enumeration classes that handle "fuzzy" parameter-matching
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
import os
import sys
import re
from enum import Flag, Enum, auto

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/../../Python-utilities")
if not os.path.isdir(dk_lib_dir):
    raise FileNotFoundError(f"Library directory '{dk_lib_dir}' cannot be found")
sys.path.insert(0, dk_lib_dir)

# pylint: disable=wrong-import-position
from lib.basic_functions import is_empty_string
from lib.exceptions import StringUtilError, ExtendedEnumError


class EnumListType(Flag):
    ITEM = auto()
    VALUE = auto()
    NAME = auto()
    STR = auto()


def always_match(any_obj):
    """
    Predicate that always matches for any object of any type.
    :param: any_obj: placeholder object
    :return: always true.
    """
    return True


def match_one_alternative(partial: str,
                          alternatives: (str | list[str]),
                          delimiter: str = "|",
                          predicate=always_match,
                          flags: re.RegexFlag = re.IGNORECASE,
                          consecutive_only: bool = False) -> tuple[(str | None), int, list]:
    """
    Matches a string to a unique alternative
    :param: partial: a partial string to be matched to any of the alternatives.
    :param: alternatives: if given as string, then use the delimiter to split it into a list of alternatives,
                         otherwise use the given list of strings.
    :param: delimiter: delimiter used to split the alternatives string into a list.
    :param: predicate: a unary predicate, this can be used to select only from a subset of the alternatives.
    :param: flags: regular expression flags.
    :param: consecutive_only: If true, then the characters in the partial have to be consecutive, otherwise only their
                             order is important.
    :return: returns a tuple:
                        — one alternative string or None.
                        — a return code (0 means success).
                        — a list of all matches.
    """
    if is_empty_string(partial):
        raise StringUtilError("Cannot match an empty partial to an alternative (all would match)")
    if isinstance(alternatives, str):
        alternatives = alternatives.split(delimiter)
    for i in range(0, len(alternatives)):
        if is_empty_string(alternatives[i]):
            raise StringUtilError(f"Alternative '{i}' in {alternatives} is empty. Cannot match.")

    if not consecutive_only:
        new_partial = ""
        for i, v in enumerate(partial):
            new_partial += v
            if i < len(partial) - 1:
                new_partial += ".*"

        partial = new_partial

    filtered_matches = []
    for alternative in alternatives:
        if isinstance(alternative, (ExtendedEnum, ExtendedFlag)):
            alt_value = alternative.value
        else:
            alt_value = alternative
        if flags is None:
            alternative_re = re.compile(pattern=f".*{partial}.*")
        else:
            alternative_re = re.compile(pattern=f".*{partial}.*", flags=flags)
        matches = alternative_re.findall(alt_value)
        if len(matches) > 0:
            if predicate(alternative):
                filtered_matches.append(alternative)

    if len(filtered_matches) != 1:
        return None, -1, filtered_matches

    return filtered_matches[0], 0, filtered_matches


def _list(cls: (Flag | Enum), list_type=EnumListType.ITEM):
    reval_list = []
    for item in cls:
        match list_type:
            case EnumListType.ITEM:
                reval_list.append(item)
            case EnumListType.VALUE:
                reval_list.append(item.value)
            case EnumListType.NAME:
                reval_list.append(item.name)
            case EnumListType.STR:
                reval_list.append(str(item))
    return reval_list


def _from_string(cls: (Flag | Enum), partial: str, predicate=always_match):
    alternatives_list = []
    items = _list(cls, EnumListType.ITEM)
    if isinstance(items[0].value, str):
        alternatives_list.append((EnumListType.VALUE, _list(cls, EnumListType.VALUE)))
    alternatives_list.append((EnumListType.NAME, _list(cls, EnumListType.NAME)))
    alternatives_list.append((EnumListType.STR, _list(cls, EnumListType.STR)))
    tried_alternatives = []
    for tp, alternatives in alternatives_list:
        matched, reval, duplicates = match_one_alternative(partial=partial,
                                                           alternatives=alternatives,
                                                           predicate=predicate)
        if reval == 0:
            for item in items:
                if tp == EnumListType.VALUE and item.value == matched:
                    return item
                if tp == EnumListType.NAME and item.name == matched:
                    return item
                if tp == EnumListType.STR and str(item) == matched:
                    return item
        tried_alternatives.append((alternatives, duplicates))

    error_message = f"Cannot match partial '{partial}' to unique enum-value\n"
    for i in range(0, len(tried_alternatives)):
        dupe = "-no match-"
        if len(tried_alternatives[i][1]) > 1:
            dupe = f"multiple matches {tried_alternatives[i][1]}"

        error_message += f"{tried_alternatives[i][0]}:\t{dupe}\n"
    raise ExtendedEnumError(error_message)


class ExtendedEnum(Enum):
    """
    Derived from Enum and extended to allow value creation from partial strings and listing of:
    — items
    — values
    — names
    — string-conversions.
    """

    @classmethod
    def list(cls, list_type=EnumListType.ITEM):
        return _list(cls=cls, list_type=list_type)

    @classmethod
    def from_string(cls, partial: str, predicate=always_match):
        return _from_string(cls=cls, partial=partial, predicate=predicate)


class ExtendedFlag(Flag):
    """
    Derived from Flag and extended to allow value creation from partial strings and listing of:
    — items
    — values
    — names
    — string-conversions.
    """

    @classmethod
    def list(cls, list_type=EnumListType.ITEM):
        return _list(cls=cls, list_type=list_type)

    @classmethod
    def from_string(cls, partial: str, predicate=always_match):
        return _from_string(cls=cls, partial=partial, predicate=predicate)
