# Repository:   https://github.com/Python-utilities
# File Name:    tools/cpp_project/main_only_file_set_creator.py
# Description:  creator for a set of main only C++ project files
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
from os import PathLike

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/../../../Python-utilities")
if not os.path.isdir(dk_lib_dir):
    raise FileNotFoundError(f"Library directory '{dk_lib_dir}' cannot be found")
sys.path.insert(0, dk_lib_dir)

# pylint: disable=wrong-import-position
from lib.overrides import overrides
from tools.cpp_project.file_name_mapper import FileNameMapper, CommentStyle
from tools.cpp_project.abc_file_set_creator import ABCFileSetCreator


class MainOnlyFileSetCreator(ABCFileSetCreator):
    """
    @brief Create files for one class
    """

    # left here for consistency with other derivatives of ABCFileSetCreator
    # pylint: disable=useless-parent-delegation
    def __init__(self, project_path: (str | PathLike)):
        super().__init__(project_path)

    @overrides(ABCFileSetCreator)
    def get_file_map_list(self) -> list[FileNameMapper]:
        return [FileNameMapper(template_file=f"{self.tpl_services_dir()}/project_main.cc",
                               target_file=f"{self.services_dir()}/{self.project_name().lower()}_main.cc",
                               comment_style=CommentStyle.CPP)]

    @overrides(ABCFileSetCreator)
    def get_tag_replacements(self) -> dict[str, str]:
        return {}
