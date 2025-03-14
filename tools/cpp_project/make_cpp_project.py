#!/bin/env python3

# Repository:   https://github.com/Python-utilities
# File Name:    tools/cpp_project/make_cpp_project.py
# Description:  main file for creating C++ projects base on templates
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
import argparse
import os
import sys

from colorama import Fore, Style

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/../../../Python-utilities")
if not os.path.isdir(dk_lib_dir):
    raise FileNotFoundError(f"Library directory '{dk_lib_dir}' cannot be found")
sys.path.insert(0, dk_lib_dir)

# pylint: disable=wrong-import-position
from lib.bash import getuser
from lib.basic_functions import valid_absolute_path
from lib.file_system_object import remove
from lib.logger import error, log_info
from lib.string_utils import is_cpp_id, input_value
from tools.cpp_project.project_creator import ProjectCreator

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
                        metavar="[msging_type-type]:proto-name[:service-name[:request-name]]",
                        nargs='+',
                        help='List of grpc client-servers')
    parser.add_argument("--templates", "-t",
                        metavar="<template-name>:Type1,Type2,...",
                        nargs='+',
                        help='List of templates to create')
    parser.add_argument("--force-overwrite", "-f",
                        action='store_true',
                        default=False,
                        help='Overwrite directory if exists, default: False')

    found_args = parser.parse_args()
    if not is_cpp_id(found_args.project_name):
        error(f"project name '{found_args.project_name}' is not a C++ identifier")
    project_path = valid_absolute_path(f"{found_args.root_dir}/{found_args.project_name}")

    if os.path.exists(project_path) and not found_args.force_overwrite:
        overwrite = input_value(var_name="createProjDir",
                                help_str=f"folder {project_path} exists. Overwrite?",
                                var_type=bool)
        if overwrite:
            remove(project_path)
        else:
            error(f"Folder '{project_path}' exists")

    project_creator = ProjectCreator(project_path=project_path,
                                     class_names=found_args.classes,
                                     grpc_service_config_strings=found_args.grpc_client_servers,
                                     templates=found_args.templates,
                                     add_docker=found_args.add_docker)

    project_creator.create_cmake_project()

    log_info(f"Project '{found_args.project_name}' has been created successfully in "
             f"{Fore.MAGENTA}{project_path}{Style.RESET_ALL}.")
