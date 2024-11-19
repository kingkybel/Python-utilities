# Repository:   https://github.com/Python-utilities
# File Name:    lib/basic_functions.py
# Description:  basic utilities
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
import re
from datetime import datetime
from os import PathLike

LINUX_PROTECTED_DIR_PATTERNS = ["^/$", "^/bin", "^/boot", "^/dev", "^/lib",
                                "^/media", "^/proc", "^/root", "^/run",
                                "^/sbin", "^/sys", "^/usr"]


def is_empty_string(string: str = None):
    return string is None or string == ""


def now_string() -> str:
    return datetime.now(tz=None).strftime("%Y%m%d-%H:%M:%S.%f")


def now_string_short() -> str:
    return datetime.now(tz=None).strftime("%Y%m%d-%H:%M")


def now_date() -> str:
    return datetime.now(tz=None).strftime("%Y-%m-%d")


def now_year() -> str:
    return datetime.now(tz=None).strftime("%Y")


def valid_absolute_path(path: (str | PathLike),
                        protect_system_patterns: (str | list[str]) = None,
                        allow_system_paths: bool = False):
    """
    Create an absolute path from the given path.
    :param: path: the original path.
    :param: protect_system_patterns: a list of patterns to prevent the returned path to be a protected system-path.
                                     By default, the Unix/Linux system paths are protected.
    :param: allow_system_paths: if set to True then system paths are allowed, default False
    :return: the absolute path as string.
    """
    if protect_system_patterns is None:
        protect_system_patterns = LINUX_PROTECTED_DIR_PATTERNS
    if isinstance(path, PathLike):
        path = str(path)
    if is_empty_string(path):
        path = "."
    path = os.path.abspath(path)
    if isinstance(protect_system_patterns, str):
        protect_system_patterns = [protect_system_patterns]
    if not allow_system_paths:
        for protected in protect_system_patterns:
            if bool(re.match(pattern=protected, string=path)):
                raise SystemError(f"Path '{path}' is a protected path. Change protect_system_patterns - parameter")
    if path.find("/") and not path.startswith("/") and not path.startswith("."):
        path = f"./{path}"
    return os.path.abspath(path)
