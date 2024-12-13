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
from os import PathLike
from pathlib import Path


def extract_dependencies(file_path: str | PathLike):
    """
    Extracts dependencies from a build.gradle file.
    :param file_path: Path to the build.gradle file.
    :return: A list of dependencies.
    """
    dependencies = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            in_dependencies_block = False
            for line in file:
                stripped_line = line.strip()

                # Check if we're entering or exiting the dependencies block
                if stripped_line.startswith('dependencies {'):
                    in_dependencies_block = True
                    continue
                if stripped_line.startswith('}') and in_dependencies_block:
                    in_dependencies_block = False
                    continue

                # Extract dependencies within the block
                if in_dependencies_block:
                    match = re.match(
                        r'(implementation|api|compile|runtimeOnly|testImplementation|testCompile)\s+["\']([^"\']+)["\']',
                        stripped_line)
                    if match:
                        dependency_type = match.group(1)
                        dependency = match.group(2)
                        dependencies.append((dependency_type, dependency))
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return dependencies


def find_dependencies(directory_list: str | PathLike | list[str | PathLike]):
    """
    Finds and extracts dependencies from all build.gradle files in a given directory.
    :param directory_list: Directory to search for build.gradle files.
    """
    if isinstance(directory_list, (str, PathLike)):
        directories = [directory_list]
    else:
        directories = directory_list

    for directory in directories:
        directory_path = Path(directory)
        if not directory_path.is_dir():
            print(f"Error: {directory} is not a valid directory.")
            return

        for gradle_file in directory_path.rglob('build.gradle'):
            print(f"Extracting dependencies from: {gradle_file}")
            dependencies = extract_dependencies(gradle_file)
            if dependencies:
                print(f"Dependencies found in {gradle_file}:")
                for dep_type, dep in dependencies:
                    print(f"  {dep_type}: {dep}")
            else:
                print(f"No dependencies found in {gradle_file}.")
            print()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Extract dependencies from build.gradle files.")
    parser.add_argument('directory',
                        type=str,
                        nargs='+',
                        help='Directories containing build.gradle files')
    args = parser.parse_args()

    find_dependencies(args.directory)
