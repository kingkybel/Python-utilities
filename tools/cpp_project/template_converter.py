#!/bin/env python3

import os
import sys
from os import PathLike

from tools.cpp_project.basic_file_set_creator import BasicFileSetCreator
from tools.cpp_project.class_file_set_creator import ClassFileSetCreator
from tools.cpp_project.cmake_file_set_creator import CmakeFileSetCreator
from tools.cpp_project.grpc_file_set_creator import GrpcFileSetCreator
from tools.cpp_project.simple_file_set_creator import SimpleFileSetCreator

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/../../../Python-utilities")
if not os.path.isdir(dk_lib_dir):
    raise FileNotFoundError(f"Library directory '{dk_lib_dir}' cannot be found")
sys.path.insert(0, dk_lib_dir)

from lib.bash import run_command, assert_tools_installed
from lib.basic_functions import valid_absolute_path
from lib.file_system_object import find, FileSystemObjectType
from lib.file_utils import get_git_config


class TemplatePopulator:
    git_config = get_git_config()

    def __init__(self,
                 project_path: (str | PathLike),
                 class_names: (str | list[str]) = None,
                 grpc_service_config_strings: (str | list[str]) = None,
                 templates: (str | list[str]) = None,
                 add_docker: bool = False):
        self.__project_path = valid_absolute_path(project_path)
        self.__project_name = os.path.basename(self.__project_path)
        self.__add_docker = add_docker

        # first need to add the basic files of the project
        # the constructor creates the necessary file structure.
        self.__file_list = [BasicFileSetCreator(project_path, add_docker=self.__add_docker)]

        # then add files for all the classes
        if class_names is None:
            class_names = []
        if isinstance(class_names, str):
            class_names = [class_names]
        self.__class_names = class_names
        for class_name in self.__class_names:
            self.__file_list.append(ClassFileSetCreator(project_path=self.__project_path, class_name=class_name))

        # after that add all the files needed for all the client/server pairs requested.
        if grpc_service_config_strings is None:
            grpc_service_config_strings = []
        if isinstance(grpc_service_config_strings, str):
            grpc_service_config_strings = [grpc_service_config_strings]
        self.__grpc_service_config_strings = grpc_service_config_strings
        port = 50050
        if len(self.__grpc_service_config_strings) > 0:
            assert_tools_installed(["protoc", "grpc_cpp_plugin"])
        for grpc_service in self.__grpc_service_config_strings:
            self.__file_list.append(GrpcFileSetCreator(project_path=self.__project_path,
                                                       proto_service_request_str=grpc_service,
                                                       port=port,
                                                       add_docker=add_docker))
            port += 1

        if templates is None:
            templates = []
        if isinstance(templates, str):
            templates = [templates]
        self.__templates = templates
        for template in self.__templates:
            pass
            # TODO: need to add templates

        if len(self.__class_names) == 0 and len(self.__grpc_service_config_strings) == 0:
            self.__file_list.append(SimpleFileSetCreator(project_path=self.__project_path))

        self.__file_list.append(CmakeFileSetCreator(project_path=self.__project_path,
                                                    class_names=self.__class_names,
                                                    grpc_service_config_strings=self.__grpc_service_config_strings,
                                                    templates=self.__templates,
                                                    add_docker=self.__add_docker))

    def add_git(self):
        run_command(cmd="git init", cwd=self.__project_path)
        files_to_add_to_git = find(paths=self.__project_path,
                                   file_type_filter=FileSystemObjectType.FILE,
                                   exclude_patterns=[r".*\.git.*"])
        for file in files_to_add_to_git:
            run_command(cmd=f"git add {file}", cwd=self.__project_path)
        run_command(cmd=["git", "commit", "-m", "initial checkin"], cwd=self.__project_path)

    def create_cmake_project(self):
        for conv in self.__file_list:
            conv.write_project_files()

        os.chmod(f"{self.__project_path}/do_build", 0o776)
        self.add_git()
        run_command(f"{self.__project_path}/do_build", cwd=self.__project_path)
