# Repository:   https://github.com/Python-utilities
# File Name:    tools/cpp_project/cmake_file_set_creator.py
# Description:  creator for a set of cmake files
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
from lib.file_utils import read_file
from lib.overrides import overrides
from lib.basic_functions import is_empty_string
from tools.cpp_project.grpc_file_set_creator import GrpcFileSetCreator
from tools.cpp_project.file_name_mapper import FileNameMapper, CommentStyle
from tools.cpp_project.abc_file_set_creator import ABCFileSetCreator
from tools.cpp_project.template_file_set_creator import TemplateFileSetCreator


class CmakeFileSetCreator(ABCFileSetCreator):
    """
    @brief Create files for all the cmake files necessary for the project.
           This needs to be run last, as it might need tags from classes, gRPC, ...
    """

    def __init__(self,
                 project_path: (str | PathLike),
                 class_names: (str | list[str]),
                 grpc_service_config_strings: (str | list[str]),
                 templates: (str | list[str]),
                 add_docker: bool
                 ):
        super().__init__(project_path)
        if class_names is None:
            class_names = []
        self.__class_names = class_names
        if grpc_service_config_strings is None:
            grpc_service_config_strings = []
        self.__grpc_service_config_strings = grpc_service_config_strings
        if templates is None:
            templates = []
        self.__templates = templates
        self.__add_docker = add_docker

    @overrides(ABCFileSetCreator)
    def get_file_map_list(self) -> list[FileNameMapper]:
        file_list = [
            FileNameMapper(template_file=f"{self.tpl_dir()}/do_build",
                           target_file=f"{self.project_dir()}/do_build",
                           comment_style=CommentStyle.BASH),
            FileNameMapper(template_file=f"{self.tpl_dir()}/CMakeLists.txt",
                           target_file=f"{self.project_dir()}/CMakeLists.txt",
                           comment_style=CommentStyle.DOCKER),
            FileNameMapper(template_file=f"{self.tpl_src_dir()}/CMakeLists.txt",
                           target_file=f"{self.src_dir()}/CMakeLists.txt",
                           comment_style=CommentStyle.DOCKER),
            FileNameMapper(template_file=f"{self.tpl_services_dir()}/CMakeLists.txt",
                           target_file=f"{self.services_dir()}/CMakeLists.txt",
                           comment_style=CommentStyle.DOCKER)]
        if len(self.__class_names) > 0:
            file_list.append(
                FileNameMapper(template_file=f"{self.tpl_classes_dir()}/CMakeLists.txt",
                               target_file=f"{self.classes_dir()}/CMakeLists.txt",
                               comment_style=CommentStyle.DOCKER))
        if len(self.__grpc_service_config_strings) > 0:
            file_list.append(
                FileNameMapper(template_file=f"{self.tpl_grpc_dir()}/CMakeLists.txt",
                               target_file=f"{self.grpc_dir()}/CMakeLists.txt",
                               comment_style=CommentStyle.DOCKER))
            file_list.append(
                FileNameMapper(template_file=f"{self.tpl_grpc_dir()}/cmake/common.cmake",
                               target_file=f"{self.grpc_dir()}/cmake/common.cmake",
                               comment_style=CommentStyle.DOCKER))
        if len(self.__grpc_service_config_strings) + len(self.__class_names) + len(self.__templates) > 0:
            file_list.append(
                FileNameMapper(template_file=f"{self.tpl_test_dir()}/CMakeLists.txt",
                               target_file=f"{self.test_dir()}/CMakeLists.txt",
                               comment_style=CommentStyle.DOCKER))
        return file_list

    @overrides(ABCFileSetCreator)
    def get_tag_replacements(self) -> dict[str, str]:
        tag_dict = {"{{cookiecutter.cmake_include_classes_sub_dir}}": "",
                    "{{cookiecutter.cmake_class_lib_targets}}": "", "{{cookiecutter.cmake_include_grpc_sub_dir}}": "",
                    "{{cookiecutter.cmake_include_services_sub_dir}}": "add_subdirectory(services)",
                    "{{cookiecutter.cmake_services_project_part}}": "", "{{cookiecutter.cmake_services_grpc_part}}": "",
                    "{{cookiecutter.cmake_grpc_services}}": "",
                    "{{cookiecutter.test_exe_link_libraries}}": self.__make_test_link_libraries(),
                    "{{cookiecutter.test_source_files}}": self.__make_test_source_files(),
                    "{{cookiecutter.cmake_test_include_dirs}}": "",
                    "{{cookiecutter.cmake_test_exe_link_libraries}}": self.__make_cmake_test_exe_link_libraries(),
                    "{{cookiecutter.docker_build_command}}": self.__make_docker_build_command(),
                    "{{cookiecutter.cmake_grpc_common_defs}}": "", "{{cookiecutter.cmake_grpc_common_libs}}": "",
                    "{{cookiecutter.cmake_include_subdir_test}}": "add_subdirectory(test)"}

        if len(self.__class_names) > 0:
            tag_dict["{{cookiecutter.cmake_include_classes_sub_dir}}"] = "add_subdirectory(classes)"
            tag_dict["{{cookiecutter.cmake_class_lib_targets}}"] = self.__make_class_lib_targets()

        if len(self.__grpc_service_config_strings) > 0:
            tag_dict["{{cookiecutter.cmake_include_grpc_sub_dir}}"] = "add_subdirectory(grpc)"
            tag_dict["{{cookiecutter.cmake_generate_cpp_from_protos}}"] = self.__make_generate_from_proto()
            tag_dict["{{cookiecutter.cmake_services_grpc_part}}"] = self.__make_services_grpc_part()
            tag_dict["{{cookiecutter.cmake_grpc_services}}"] = self.__make_cmake_grpc_services()
            tag_dict["{{cookiecutter.cmake_test_include_dirs}}"] = \
                f'target_include_directories("run_{self.project_name().lower()}_tests" PRIVATE ${{PROTO_CPP_SRC_DIR}})'
            tag_dict[
                "{{cookiecutter.cmake_grpc_common_defs}}"] = "set(PROTO_CPP_SRC_DIR ${CMAKE_SOURCE_DIR}/src/proto_cpp)\n" \
                                                             "include(${CMAKE_SOURCE_DIR}/src/grpc/cmake/common.cmake)"
            tag_dict["{{cookiecutter.cmake_grpc_common_libs}}"] = "  absl::flags\n" \
                                                                  "  absl::flags_parse\n" \
                                                                  "  ${_REFLECTION}\n" \
                                                                  "  ${_GRPC_GRPCPP}\n" \
                                                                  "  ${_PROTOBUF_LIBPROTOBUF}"

        if len(self.__class_names) == 0 and len(self.__grpc_service_config_strings) == 0:
            tag_dict["{{cookiecutter.cmake_services_project_part}}"] = read_file(
                f"{self.tpl_services_dir()}/CMake_project.part")

        if len(self.__grpc_service_config_strings) + len(self.__class_names) + len(self.__templates) == 0:
            tag_dict["{{cookiecutter.cmake_include_subdir_test}}"] = ""

        return tag_dict

    def __make_class_lib_targets(self) -> str:
        class_targets = ""
        for target in self.__class_names:
            if len(self.__class_names) > 1:
                class_targets += "\n  "
            class_targets += target.lower()

        return class_targets

    def __make_generate_from_proto(self) -> str:
        protos = ""
        for grpc_service_config_string in self.__grpc_service_config_strings:
            grpc_config = GrpcFileSetCreator(project_path=self.project_path(),
                                             proto_service_request_str=grpc_service_config_string,
                                             port=-1)
            if len(self.__grpc_service_config_strings) > 1:
                protos += "\n                       "
            protos += grpc_config.proto()

        return f'create_cpp_from_protos("${{CMAKE_SOURCE_DIR}}/protos" ${{PROTO_CPP_SRC_DIR}} {protos})\n'

    def __make_services_grpc_part(self) -> str:
        grpc_part = read_file(f"{self.tpl_services_dir()}/CMake_grpc.part")
        services_str = ""
        for grpc_service_config_string in self.__grpc_service_config_strings:
            grpc_config = GrpcFileSetCreator(project_path=self.project_path(),
                                             proto_service_request_str=grpc_service_config_string,
                                             port=-1)
            if len(self.__grpc_service_config_strings) > 1:
                services_str += "\n        "
            services_str += grpc_config.service_with_type().lower()
        grpc_part = grpc_part.replace("{{cookiecutter.cmake_grpc_services}}", services_str)
        return grpc_part

    def __make_test_link_libraries(self) -> str:
        libs = ""
        multiline = len(self.__class_names) + len(self.__grpc_service_config_strings) > 1
        for cls in self.__class_names:
            if multiline:
                libs += "\n  "
            libs += cls.lower()
        for grpc_service_config_string in self.__grpc_service_config_strings:
            grpc_config = GrpcFileSetCreator(project_path=self.project_path(),
                                             proto_service_request_str=grpc_service_config_string,
                                             port=-1)
            if multiline:
                libs += "\n  "
            libs += grpc_config.service_with_type().lower()

        return libs

    def __make_test_source_files(self) -> str:
        test_sources = ""
        for cls in self.__class_names:
            test_sources += f"\n               {cls.lower()}_tests.cc"
        for grpc_service_config_string in self.__grpc_service_config_strings:
            grpc_config = GrpcFileSetCreator(project_path=self.project_path(),
                                             proto_service_request_str=grpc_service_config_string,
                                             port=-1)
            test_sources += f"\n               {grpc_config.service_with_type().lower()}_client_tests.cc"
            test_sources += f"\n               {grpc_config.service_with_type().lower()}_service_tests.cc"
        for template_config_string in self.__templates:
            template_config = TemplateFileSetCreator(project_path=self.project_path(),
                                                     template_config_str=template_config_string)
            test_sources += f"\n               {template_config.template_name().lower()}_tests.cc"
        if is_empty_string(test_sources):
            test_sources += f"\n               {self.project_name().lower()}_tests.cc"
        return test_sources

    def __make_cmake_test_exe_link_libraries(self) -> str:
        link_libs = ""
        INDENTATION = "\n                      "
        print(f"{self.__class_names} {self.__grpc_service_config_strings}")
        multiline = (len(self.__class_names) + len(self.__grpc_service_config_strings)) > 1 or \
                    len(self.__grpc_service_config_strings) == 1
        for cls in self.__class_names:
            if multiline:
                link_libs += INDENTATION
            link_libs += cls.lower()
        for grpc_service_config_string in self.__grpc_service_config_strings:
            grpc_config = GrpcFileSetCreator(project_path=self.project_path(),
                                             proto_service_request_str=grpc_service_config_string,
                                             port=-1)
            if multiline:
                link_libs += INDENTATION
            link_libs += f"{grpc_config.service_with_type().lower()}_client"
            if multiline:
                link_libs += INDENTATION
            link_libs += f"{grpc_config.service_with_type().lower()}_service"
        if not is_empty_string(link_libs):
            link_libs = \
                f"target_link_libraries(run_{self.project_name().lower()}_tests PRIVATE gtest gtest_main {link_libs})"
        return link_libs

    def __make_docker_build_command(self) -> str:
        docker_cmds = ""
        if self.__add_docker:
            for grpc_service_config_string in self.__grpc_service_config_strings:
                grpc_config = GrpcFileSetCreator(project_path=self.project_path(),
                                                 proto_service_request_str=grpc_service_config_string,
                                                 port=-1)
                docker_cmds += f"docker compose " \
                               f"--file docker-compose.{grpc_config.service().lower()}.yml " \
                               f"--env-file .{grpc_config.service().lower()}.env " \
                               f"build\n"

            if is_empty_string(docker_cmds):
                docker_cmds += "docker compose build\n"

        return docker_cmds

    def __make_cmake_grpc_services(self) -> str:
        grpc_services = ""
        for grpc_service_config_string in self.__grpc_service_config_strings:
            grpc_config = GrpcFileSetCreator(project_path=self.project_path(),
                                             proto_service_request_str=grpc_service_config_string,
                                             port=-1)
            if len(self.__grpc_service_config_strings) > 1:
                grpc_services += "\n        "
            grpc_services += grpc_config.service_with_type().lower()
        return grpc_services
