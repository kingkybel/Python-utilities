#!/bin/env python3

import argparse
import os
import sys
from enum import auto
from colorama import Fore, Style

from lib.json_object import JsonObject

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/..")
sys.path.insert(0, dk_lib_dir)

from os import PathLike
from lib.bash import run_command, getuser
from lib.basic_functions import now_date, is_empty_string, valid_absolute_path, now_year
from lib.file_system_object import mkdir, remove, find, FileSystemObjectType
from lib.file_utils import read_file, write_file, get_git_config
from lib.logger import error, log_info
from lib.extended_enum import ExtendedEnum
from lib.string_utils import is_cpp_id, input_value


class CommentStyle(ExtendedEnum):
    NONE = auto()
    CPP = auto()
    PYTHON = auto()
    JAVA = auto()
    BASH = auto()
    CMAKE = auto()
    DOCKER = auto()

    def start(self) -> str:
        if self == CommentStyle.NONE:
            return ""
        if self == CommentStyle.CPP:
            return "/*"
        if self == CommentStyle.PYTHON:
            return '"""'
        if self == CommentStyle.JAVA:
            return "/*"
        if self == CommentStyle.BASH:
            return "###"
        if self == CommentStyle.CMAKE:
            return "###"
        if self == CommentStyle.DOCKER:
            return "###"

    def cont(self) -> str:
        if self == CommentStyle.NONE:
            return ""
        if self == CommentStyle.CPP:
            return " * "
        if self == CommentStyle.PYTHON:
            return '" '
        if self == CommentStyle.JAVA:
            return " * "
        if self == CommentStyle.BASH:
            return "# "
        if self == CommentStyle.CMAKE:
            return "# "
        if self == CommentStyle.DOCKER:
            return "# "

    def end(self) -> str:
        if self == CommentStyle.NONE:
            return ""
        if self == CommentStyle.CPP:
            return " */"
        if self == CommentStyle.PYTHON:
            return '"""'
        if self == CommentStyle.JAVA:
            return " */"
        if self == CommentStyle.BASH:
            return "###"
        if self == CommentStyle.CMAKE:
            return "###"
        if self == CommentStyle.DOCKER:
            return "###"


class TemplatePopulator:
    def __init__(self,
                 project_path: (str | PathLike),
                 class_names: (str | list[str]) = None,
                 add_docker: bool = False):
        self.project_path = valid_absolute_path(project_path)
        self.project_name = os.path.basename(self.project_path)

        # create basic directory structure
        self.class_names = list()
        if isinstance(class_names, str):
            self.class_names = [class_names]
        elif class_names is not None:
            self.class_names = class_names
        self.add_docker = add_docker
        self.docker_build_command = ""
        if self.add_docker:
            self.docker_build_command = "docker-compose build"

        self.licence_content = self.populate_licence()
        self.create_directories(self.project_path)
        write_file(filename=f"{project_path}/licence/licence", content=self.licence_content)
        self.file_list = list()

        # create tags for multiple project-class files
        self.project_hash_includes = ""
        self.cmake_project_lib_target = ""
        self.cmake_exe_link_libraries = ""
        self.cmake_test_exe_link_libraries = ""
        self.using_namespace = ""
        self.create_tags_for_classes()

        # create a list of all files for the project
        self.file_list = list()
        self.make_project_file_list()

    @classmethod
    def create_directories(cls, project_path: (str | PathLike)):
        # Create the project directory and subdirectories
        mkdir([f"{project_path}/include",
               f"{project_path}/src",
               f"{project_path}/test",
               f"{project_path}/licence",
               f"{project_path}/build"])

    @classmethod
    def populate_licence(cls) -> str:
        licence_str = read_file(filename=f"{this_dir}/templates/licence/licence")
        git_config = get_git_config()
        licence_str = licence_str.replace("[[YEAR]]", now_year())
        licence_str = licence_str.replace("[[AUTHOR]]", git_config["user.name"])
        licence_str = licence_str.replace("[[EMAIL]]", git_config["user.email"])
        licence_str = licence_str.replace("[[TODAY]]", now_date())

        return licence_str

    def commented_licence_string(self, pure_text: str, comment_style: CommentStyle, filename: str = None) -> str:
        lic_with_comments = comment_style.start() + "\n"
        if filename is not None:
            filename.replace(f"{self.project_path}?", "")
            lic_with_comments += comment_style.cont() + f"Filename: {filename}\n"
            lic_with_comments += comment_style.cont() + "\n"
        for line in pure_text.split("\n"):
            lic_with_comments += comment_style.cont() + line + "\n"
        lic_with_comments += comment_style.end()

        return lic_with_comments

    def create_tags_for_classes(self):
        self.cmake_exe_link_libraries = ""
        self.cmake_test_exe_link_libraries = f"target_link_libraries(run_{self.project_name.lower()}_tests " \
                                             f"gtest gtest_main)"
        if len(self.class_names) == 0:
            return

        self.project_hash_includes = ""
        self.cmake_project_lib_target = f"add_library({self.project_name.lower()} STATIC\n"
        for class_name in self.class_names:
            self.cmake_project_lib_target += f"\t{class_name.lower()}.cc\n"
            self.project_hash_includes += f'#include "{class_name.lower()}.h"\n'

        self.cmake_project_lib_target += ")"
        self.cmake_exe_link_libraries = f"target_link_libraries({self.project_name.lower()}_exe " \
                                        f"PRIVATE {self.project_name.lower()})"
        self.cmake_test_exe_link_libraries = f"target_link_libraries(run_{self.project_name.lower()}_tests " \
                                             f"PRIVATE gtest gtest_main {self.project_name.lower()})"
        self.using_namespace = f"using namespace ns_{self.project_name.lower()};"

    def make_project_file_list(self):
        self.file_list = list()
        # add non-project-dependent files
        for tmplt in [(".vscode/c_cpp_properties.json", CommentStyle.NONE),
                      (".vscode/launch.json", CommentStyle.NONE),
                      (".vscode/settings.json", CommentStyle.NONE),
                      (".vscode/tasks.json", CommentStyle.NONE),
                      ("CMakeLists.txt", CommentStyle.CMAKE),
                      ("do_build", CommentStyle.BASH),
                      ("src/CMakeLists.txt", CommentStyle.CMAKE),
                      ("test/CMakeLists.txt", CommentStyle.CMAKE),
                      (".gitignore", CommentStyle.BASH),
                      (".clang-format", CommentStyle.BASH),
                      (".clang-tidy", CommentStyle.BASH),
                      ("Doxyfile", CommentStyle.BASH)]:
            self.file_list.append(
                (f"{this_dir}/templates/{tmplt[0]}", f"{self.project_path}/{tmplt[0]}", tmplt[1], None))

        # if we want dockerisation then add docker-files
        if self.add_docker:
            for tmplt in [("Dockerfile", CommentStyle.DOCKER),
                          ("docker-compose.yml", CommentStyle.DOCKER),
                          (".env", CommentStyle.DOCKER),
                          ("bash_aliases_for_docker", CommentStyle.BASH),
                          ("bash_aliases_for_docker", CommentStyle.BASH),
                          (".gitignore", CommentStyle.BASH),
                          (".clang-format", CommentStyle.BASH),
                          (".clang-tidy", CommentStyle.BASH),
                          ("Doxyfile", CommentStyle.BASH)]:
                self.file_list.append(
                    (f"{this_dir}/templates/{tmplt[0]}", f"{self.project_path}/{tmplt[0]}", tmplt[1], None))

        # add C++ main and test-main files
        self.file_list.append((f"{this_dir}/templates/src/project_main.cc",
                               f"{self.project_path}/src/{self.project_name.lower()}_main.cc",
                               CommentStyle.CPP,
                               None))
        self.file_list.append((f"{this_dir}/templates/test/project_tests.cc",
                               f"{self.project_path}/test/run_{self.project_name.lower()}_tests.cc",
                               CommentStyle.CPP,
                               None))

        # add classes split in header and implementation
        for class_name in self.class_names:
            if not is_cpp_id(class_name):
                error(f"Class-name {class_name} is not a valid C++ identifier")
            self.file_list.append((f"{this_dir}/templates/include/class_include.h",
                                   f"{self.project_path}/include/{class_name.lower()}.h", CommentStyle.CPP, class_name))
            self.file_list.append((f"{this_dir}/templates/src/class_source.cc",
                                   f"{self.project_path}/src/{class_name.lower()}.cc", CommentStyle.CPP, class_name))

    def replace_templates(self,
                          tmplt_text: str,
                          filename: str,
                          comment_style: CommentStyle,
                          class_name: str = "") -> str:
        licence_str = self.commented_licence_string(self.licence_content, comment_style, filename)
        if class_name is None:
            class_name = ""
        tmplt_text = tmplt_text.replace("[[FILENAME]]", filename)
        tmplt_text = tmplt_text.replace("[[CLASS_NAME]]", class_name)
        tmplt_text = tmplt_text.replace("[[CLASS_NAME_UPPER]]", class_name.upper())
        tmplt_text = tmplt_text.replace("[[CLASS_NAME_LOWER]]", class_name.lower())
        tmplt_text = tmplt_text.replace("[[LICENCE]]", licence_str)
        tmplt_text = tmplt_text.replace("[[PROJECT_NAME]]", self.project_name)
        tmplt_text = tmplt_text.replace("[[PROJECT_NAME_UPPER]]", self.project_name.upper())
        tmplt_text = tmplt_text.replace("[[PROJECT_NAME_LOWER]]", self.project_name.lower())
        tmplt_text = tmplt_text.replace("[[CLASS_INCLUDES]]", self.project_hash_includes)
        tmplt_text = tmplt_text.replace("[[PROJECT_LIB_TARGET]]", self.cmake_project_lib_target)
        tmplt_text = tmplt_text.replace("[[EXE_LINK_LIBRARIES]]", self.cmake_exe_link_libraries)
        tmplt_text = tmplt_text.replace("[[TEST_EXE_LINK_LIBRARIES]]", self.cmake_test_exe_link_libraries)
        tmplt_text = tmplt_text.replace("[[DOCKER_BUILD_COMMAND]]", self.docker_build_command)
        tmplt_text = tmplt_text.replace("[[USING_NAMESPACE]]", self.using_namespace)

        return tmplt_text

    def write_project_file(self,
                           template_file: str,
                           project_file: str,
                           comment_style: CommentStyle,
                           class_name: str):
        content = read_file(template_file)
        content = self.replace_templates(tmplt_text=content,
                                         filename=project_file,
                                         comment_style=comment_style,
                                         class_name=class_name)
        write_file(filename=project_file, content=content)

    def add_git(self):
        run_command(cmd="git init", cwd=self.project_path)
        files_to_add_to_git = find(paths=self.project_path, file_type_filter=FileSystemObjectType.FILE)
        for file in files_to_add_to_git:
            run_command(cmd=f"git add {file}", cwd=self.project_path)
        run_command(cmd=["git", "commit", "-m", "initial checkin"], cwd=self.project_path)

    def create_cmake_project(self):

        for tpl in self.file_list:
            self.write_project_file(template_file=tpl[0],
                                    project_file=tpl[1],
                                    comment_style=tpl[2],
                                    class_name=tpl[3])
        os.chmod(f"{self.project_path}/do_build", 0o776)
        self.add_git()
        run_command(f"{self.project_path}/do_build", cwd=self.project_path)
