# Repository:   https://github.com/Python-utilities
# File Name:    tools/cpp_project/abc_file_set_creator.py
# Description:  abstract base class to capture the creation of a set of C++ files
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
from abc import ABC, abstractmethod
from os import PathLike

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/../../../Python-utilities")
if not os.path.isdir(dk_lib_dir):
    raise FileNotFoundError(f"Library directory '{dk_lib_dir}' cannot be found")
sys.path.insert(0, dk_lib_dir)

from lib.file_system_object import remove, mkdir
from lib.basic_functions import valid_absolute_path, now_year, now_date
from lib.file_utils import read_file, write_file, get_git_config
from lib.string_utils import replace_all
from lib.logger import log_info
from tools.cpp_project.file_name_mapper import FileNameMapper, CommentStyle


class ABCFileSetCreator(ABC):
    """
    @brief base class for creating *one* set of files for a feature of a project
    """
    git_config = get_git_config()
    is_basic_structure_created = False

    def __init__(self, project_path: (str | PathLike)):
        self.__project_path = valid_absolute_path(project_path)
        self.__project_name = os.path.basename(self.__project_path)
        self.__common_replacements = {
            "{{cookiecutter.project_name}}": self.__project_name,
            "{{cookiecutter.project_name_upper}}": self.__project_name.upper(),
            "{{cookiecutter.project_name_lower}}": self.__project_name.lower(),
            "{{cookiecutter.using_namespace}}": f"using namespace ns_{self.__project_name.lower()};",
            "{{cookiecutter.author}}": str(ABCFileSetCreator.git_config["user.name"]),
            "{{cookiecutter.email}}": str(ABCFileSetCreator.git_config["user.email"]),
            "{{cookiecutter.today}}": now_date(),
            "{{cookiecutter.year}}": now_year()}
        self.__licence = self.licence()

    @abstractmethod
    def get_file_map_list(self) -> list[FileNameMapper]:
        pass

    @abstractmethod
    def get_tag_replacements(self) -> dict[str, str]:
        pass

    def project_path(self):
        return self.__project_path

    def project_name(self):
        return self.__project_name

    def licence(self) -> str:
        licence_str = read_file(filename=f"{this_dir}/templates/licence/licence")
        return replace_all(licence_str, self.__common_replacements)

    def __create_basic_dir_structure(self):
        # Create the project directory and subdirectories
        if not ABCFileSetCreator.is_basic_structure_created:
            remove(self.project_path())
            mkdir([f"{self.include_dir()}",
                   f"{self.src_dir()}",
                   f"{self.services_dir()}",
                   f"{self.test_dir()}",
                   f"{self.licence_dir()}",
                   f"{self.build_dir()}",
                   f"{self.vscode_dir()}"], force=True, recreate=True)
            write_file(f"{self.project_path()}/licence/licence", self.licence())
            ABCFileSetCreator.is_basic_structure_created = True
            self.write_project_files()

    def commented_licence_string(self, licence_text: str, comment_style: CommentStyle, filename: str) -> str:
        lic_with_comments = comment_style.start() + "\n"
        filename = filename.replace(f"{self.__project_path}", self.__project_name)
        lic_with_comments += comment_style.cont() + f"Filename: {filename}\n"
        lic_with_comments += comment_style.cont() + "\n"
        for line in licence_text.split("\n"):
            lic_with_comments += comment_style.cont() + line + "\n"
        lic_with_comments += comment_style.end()

        return lic_with_comments

    def write_project_files(self):
        if not ABCFileSetCreator.is_basic_structure_created:
            self.__create_basic_dir_structure()
        file_maps = self.get_file_map_list()
        for file_map in file_maps:
            content = read_file(file_map.template_file())
            log_info(f"template={file_map.template_file()}")
            self.__common_replacements["{{cookiecutter.licence}}"] = \
                self.commented_licence_string(licence_text=self.__licence,
                                              comment_style=file_map.comment_style(),
                                              filename=file_map.target_file())
            content = replace_all(content, self.get_tag_replacements())
            content = replace_all(content, self.__common_replacements)
            content = replace_all(content, self.get_tag_replacements())
            write_file(filename=file_map.target_file(), content=content)
            log_info(f"proj_file={file_map.target_file()}")

    def project_dir(self):
        return self.__project_path

    @staticmethod
    def tpl_dir():
        return f"{this_dir}/templates"

    @staticmethod
    def tpl_include_dir():
        return f"{ABCFileSetCreator.tpl_dir()}/include"

    @staticmethod
    def tpl_src_dir():
        return f"{ABCFileSetCreator.tpl_dir()}/src"

    @staticmethod
    def tpl_proto_dir():
        return f"{ABCFileSetCreator.tpl_dir()}/protos"

    @staticmethod
    def tpl_grpc_dir():
        return f"{ABCFileSetCreator.tpl_src_dir()}/grpc"

    @staticmethod
    def tpl_classes_dir():
        return f"{ABCFileSetCreator.tpl_src_dir()}/classes"

    @staticmethod
    def tpl_services_dir():
        return f"{ABCFileSetCreator.tpl_src_dir()}/services"

    @staticmethod
    def tpl_licence_dir():
        return f"{ABCFileSetCreator.tpl_dir()}/licence"

    @staticmethod
    def tpl_test_dir():
        return f"{ABCFileSetCreator.tpl_dir()}/test"

    @staticmethod
    def tpl_vscode_dir():
        return f"{ABCFileSetCreator.tpl_dir()}/.vscode"

    def include_dir(self):
        return f"{self.project_dir()}/include"

    def src_dir(self):
        return f"{self.project_dir()}/src"

    def proto_dir(self):
        return f"{self.project_dir()}/protos"

    def services_dir(self):
        return f"{self.src_dir()}/services"

    def grpc_dir(self):
        return f"{self.src_dir()}/grpc"

    def classes_dir(self):
        return f"{self.src_dir()}/classes"

    def licence_dir(self):
        return f"{self.project_dir()}/licence"

    def test_dir(self):
        return f"{self.project_dir()}/test"

    def vscode_dir(self):
        return f"{self.project_dir()}/.vscode"

    def build_dir(self):
        return f"{self.project_dir()}/build"
