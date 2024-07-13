# Repository:   https://github.com/Python-utilities
# File Name:    tools/cpp_project/class_file_set_creator.py
# Description:  creator for a set of C++-class files
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
from os import PathLike

from lib.overrides import overrides

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/../../../Python-utilities")
if not os.path.isdir(dk_lib_dir):
    raise FileNotFoundError(f"Library directory '{dk_lib_dir}' cannot be found")
sys.path.insert(0, dk_lib_dir)

from lib.logger import error
from lib.string_utils import is_cpp_id
from tools.cpp_project.file_name_mapper import FileNameMapper, CommentStyle
from tools.cpp_project.abc_file_set_creator import ABCFileSetCreator


class ClassFileSetCreator(ABCFileSetCreator):
    """
    @brief Create files for one class
    """

    def __init__(self, project_path: (str | PathLike), class_name: str):
        super().__init__(project_path)
        if not is_cpp_id(class_name):
            error(f"Class-name {class_name} is not a valid C++ identifier")
        self.__class_name = class_name

    @overrides(ABCFileSetCreator)
    def get_tag_replacements(self) -> dict[str, str]:
        return {
            "[[CLASS_NAME]]": self.__class_name,
            "[[CLASS_NAME_LOWER]]": self.__class_name.lower(),
            "[[CLASS_NAME_UPPER]]": self.__class_name.upper(),
            "[[CLASS_HASH_INCLUDE]]": f'#include "{self.__class_name.lower()}.h"\n'}

    @overrides(ABCFileSetCreator)
    def get_file_map_list(self) -> list[FileNameMapper]:
        return [FileNameMapper(template_file=f"{self.tpl_include_dir()}/class_include.h",
                               target_file=f"{self.include_dir()}/{self.__class_name.lower()}.h",
                               comment_style=CommentStyle.CPP),
                FileNameMapper(template_file=f"{self.tpl_classes_dir()}/class_source.cc",
                               target_file=f"{self.classes_dir()}/{self.__class_name.lower()}.cc",
                               comment_style=CommentStyle.CPP),
                FileNameMapper(template_file=f"{self.tpl_test_dir()}/class_tests.cc",
                               target_file=f"{self.test_dir()}/{self.__class_name.lower()}_tests.cc",
                               comment_style=CommentStyle.CPP),
                FileNameMapper(template_file=f"{self.tpl_test_dir()}/run_tests.cc",
                               target_file=f"{self.test_dir()}/run_{self.project_name().lower()}_tests.cc",
                               comment_style=CommentStyle.CPP)]
