#!/bin/env python3

# Repository:   https://github.com/Python-utilities
# File Name:    tools/gitlab/gitlab_tools.py
# Description:  Check status of merge-requests on gitlab
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
# @date: 2024-11-18
# @author: Dieter J Kybelksties

from __future__ import annotations
import re
from pathlib import Path
import os
import sys
from os import PathLike

from lib.file_utils import write_file
from lib.string_utils import make_cpp_id

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/../../../Python-utilities")
if not os.path.isdir(dk_lib_dir):
    raise FileNotFoundError(f"Library directory '{dk_lib_dir}' cannot be found")
sys.path.insert(0, dk_lib_dir)

# pylint: disable=wrong-import-position
from lib.file_system_object import find, FileSystemObjectType


def convert_dependency_dict_to_graphviz(dependency_dict: dict[str, list[str]]) -> str:
    graph = "\ndigraph G {\n"

    for service_node in dependency_dict.keys():
        graph += f'\t{make_cpp_id(service_node)} [label="{service_node}"];\n'

    for service_node in dependency_dict.keys():
        for dep in dependency_dict[service_node]:
            graph += f"\t{make_cpp_id(service_node)} -> {make_cpp_id(dep)};\n"
    graph += "}\n"

    return graph


def extract_helm_chart_dependencies(file_path: str | PathLike):
    """
    Extracts dependencies from the helmChartDeploy block in a build.gradle file.
    :param file_path: Path to the build.gradle file.
    :return: A dictionary of helmChartDeploy properties and their values.
    """
    properties = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            in_helm_block = False
            current_property = None

            for line in file:
                stripped_line = line.strip()

                # Detect the start of the helmChartDeploy block
                if stripped_line.startswith("helmChartDeploy"):
                    in_helm_block = True
                    continue

                # Detect the end of the helmChartDeploy block
                if in_helm_block and stripped_line == "}":
                    in_helm_block = False
                    continue

                # Process properties within the helmChartDeploy block
                if in_helm_block:
                    # Match properties in the form `key "value"` or `key 'value'`
                    match = re.match(r'(\w+)\s+["\']([^"\']+)["\']', stripped_line)
                    if match:
                        key, value = match.groups()
                        properties[key] = value
                        current_property = key
                        continue

                    # Match a dependencies list in the form `dependencies 'item1', 'item2', ...`
                    match = re.match(r'dependencies\s+((["\']([^"\']+)["\'],?\s*)+)', stripped_line)
                    if match:
                        items = re.findall(r'["\']([^"\']+)["\']', stripped_line)
                        properties["dependencies"] = items
                        continue

                    # Handle multi-line dependencies
                    if current_property == "dependencies" and stripped_line.endswith(","):
                        items = re.findall(r'["\']([^"\']+)["\']', stripped_line)
                        if not properties["dependencies"] is None:
                            if isinstance(properties["dependencies"], str):
                                properties["dependencies"] = [properties["dependencies"]]
                        properties["dependencies"].extend(items)
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return properties


def find_deploy_dependencies(build_gradle: str | PathLike) -> dict[str, list[str]]:
    """
    Finds and extracts helmChartDeploy properties from all build.gradle files in a given directory.
    :param build_gradle: build.gradle.
    """
    dependency_map = {}
    service_name = os.path.basename(os.path.dirname(build_gradle))
    properties = extract_helm_chart_dependencies(build_gradle)
    if properties:
        dependency_map[service_name] = []
        for _, value in properties.items():
            if isinstance(value, list):
                for item in value:
                    dependency_map[service_name].append(item)
            else:
                dependency_map[service_name].append(value)
    return dependency_map

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Extract helmChartDeploy properties from build.gradle files.")
    parser.add_argument('directory', type=str, help='Directory containing build.gradle files')
    args = parser.parse_args()

    gradle_files = find(args.directory, name_patterns="build.gradle", exclude_patterns=r".*test.*")

    all_dependencies = {}
    for gradle_file in gradle_files:
        all_dependencies = all_dependencies | find_deploy_dependencies(gradle_file)
    write_file(filename="deps.gviz", content=convert_dependency_dict_to_graphviz(all_dependencies))


