#!/bin/env python3

import argparse
import os
import sys

from colorama import Fore, Style

from lib.extended_enum import EnumListType

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/..")
sys.path.insert(0, dk_lib_dir)

from lib.bash import getuser
from lib.basic_functions import valid_absolute_path
from lib.file_system_object import remove
from lib.logger import error, log_info
from lib.string_utils import is_cpp_id, input_value
from tools.templateConverter import TemplatePopulator, GrpcConnectivity

DEFAULT_ROOT_DIRECTORY = f"/home/{getuser()}/Repos/CPP"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a CMake project with Docker Compose files')
    parser.add_argument("--root_dir", "-r",
                        default=DEFAULT_ROOT_DIRECTORY,
                        type=str,
                        help=f'Root directory for the project, default {DEFAULT_ROOT_DIRECTORY}')
    parser.add_argument("--project_name", "-n",
                        type=str,
                        help='Name of the project')
    parser.add_argument("--classes", "-c",
                        metavar="class-to-create",
                        type=str,
                        nargs='+',
                        help='Class-names to create')
    parser.add_argument("--add-docker", "-d",
                        action='store_true',
                        default=False,
                        help='Whether or not to add dockerisation, default: False')
    parser.add_argument("--grpc-client-servers", "-g",
                        metavar="proto-name[:service-name[:request-name]]",
                        nargs='+',
                        help='List of grpc client-servers')
    parser.add_argument("--connectivity-type", "-t",
                        default=GrpcConnectivity.DEFAULT,
                        help=f'Type of connectivity for grpc ({GrpcConnectivity.list(EnumListType.NAME)})'
                             f', default {str(GrpcConnectivity.DEFAULT)}')
    parser.add_argument("--force-overwrite", "-f",
                        action='store_true',
                        default=False,
                        help='Overwrite directory if exists, default: False')

    found_args = parser.parse_args()
    if not is_cpp_id(found_args.project_name):
        error("project name must be C++ identifier")
    project_path = valid_absolute_path(f"{found_args.root_dir}/{found_args.project_name}")

    if os.path.exists(project_path) and not found_args.force_overwrite:
        overwrite = input_value(var_name="createProjDir",
                                help_str=f"folder {project_path} exists. Overwrite?",
                                var_type=bool)
        if overwrite:
            remove(project_path)
        else:
            error(f"Folder '{project_path}' exists")

    if isinstance(found_args.connectivity_type, str):
        found_args.connectivity_type = GrpcConnectivity.from_string(found_args.connectivity_type)
    template_populator = TemplatePopulator(project_path=project_path,
                                           class_names=found_args.classes,
                                           grpc_client_server_names=found_args.grpc_client_servers,
                                           add_docker=found_args.add_docker,
                                           connectivity_type=found_args.connectivity_type)

    template_populator.create_cmake_project()

    log_info(f"Project '{found_args.project_name}' has been created successfully in "
             f"{Fore.MAGENTA}{project_path}{Style.RESET_ALL}.")
