# Repository:   https://github.com/Python-utilities
# File Name:    tools/cpp_project/basic_file_set_creator.py
# Description:  creator for a set of basic C++ files
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
from tools.cpp_project.abc_file_set_creator import ABCFileSetCreator
from tools.cpp_project.file_name_mapper import FileNameMapper, CommentStyle


class BasicFileSetCreator(ABCFileSetCreator):
    """
    @brief base class for creating *one* set of files for a feature of a project.
    """

    def __init__(self, project_path: (str | PathLike), add_docker: bool):
        super().__init__(project_path)
        self.__add_docker = add_docker

    @overrides(ABCFileSetCreator)
    def get_file_map_list(self) -> list[FileNameMapper]:
        file_list = []
        ######################################
        # add common project files.
        for tmplt in [(".vscode/c_cpp_properties.json", CommentStyle.NONE),
                      (".vscode/launch.json", CommentStyle.NONE),
                      (".vscode/settings.json", CommentStyle.NONE),
                      (".vscode/tasks.json", CommentStyle.NONE),
                      (".gitignore", CommentStyle.BASH),
                      (".clang-format", CommentStyle.BASH),
                      (".clang-tidy", CommentStyle.BASH),
                      ("Doxyfile", CommentStyle.BASH)]:
            file_list.append(
                FileNameMapper(template_file=f"{self.tpl_dir()}/{tmplt[0]}",
                               target_file=f"{self.project_path()}/{tmplt[0]}",
                               comment_style=tmplt[1]))
        if self.__add_docker:
            file_list.append(
                FileNameMapper(template_file=f"{self.tpl_dir()}/bash_aliases_for_docker",
                               target_file=f"{self.project_path()}/bash_aliases_for_docker",
                               comment_style=tmplt[1]))
        return file_list

    @overrides(ABCFileSetCreator)
    def get_tag_replacements(self) -> dict[str, str]:
        return {}
