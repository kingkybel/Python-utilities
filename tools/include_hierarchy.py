#!/bin/env python3

import argparse
import os
import re
import sys

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/../../Python-utilities")
if not os.path.isdir(dk_lib_dir):
    raise FileNotFoundError(f"Library directory '{dk_lib_dir}' cannot be found")
sys.path.insert(0, dk_lib_dir)

from lib.bash import get_logged_in_user
from lib.file_system_object import find, FileSystemObjectType
from lib.file_utils import read_file
from lib.json_object import JsonObject


def extract_includes(file_path: str, included_by: dict[str, set[str]]):
    content = read_file(filename=file_path)

    found_includes = re.findall(r'#include\s+(["<].*?[">])', content)

    file_key = os.path.basename(file_path)
    for include in found_includes:
        if include not in included_by.keys():
            included_by[include] = set()
        included_by[include].add(file_key)

    return included_by


def also_included_by(include: str, included_by: dict[str, set[str]]):
    if include in included_by.keys():
        for includer in included_by[include]:
            if includer in included_by.keys():
                included_by[include].union(included_by[includer])
            also_included_by(includer, included_by)
    return included_by


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=
        """Install "light": copy include, libs, bins into a local folder and symbolically link from a system folder""")

    parser.add_argument(
        "--root_dir", "-r",
        default=f"/home/{get_logged_in_user()}/Repos/CPP/CPP-utilities",
        type=str,
        help='Location of include, build/bin and build/lib folders')

    found_args = parser.parse_args()

    directory = found_args.root_dir
    cpp_files = find(paths=[f"{directory}/src", f"{directory}/include"],
                     file_type_filter=FileSystemObjectType.FILE)
    included_files = dict()

    # Extract includes from all files
    for cpp_file in cpp_files:
        print(cpp_file)
        included_files = extract_includes(cpp_file, included_files)

    for include in included_files:
        included_files = also_included_by(include, included_files)

    hierarchy = dict()
    for include in included_files:
        hierarchy[include] = 0
        for inc_by in included_files[include]:
            if inc_by not in hierarchy.keys():
                hierarchy[inc_by] = 0
            hierarchy[inc_by] += 1

    sorted_hierarchy = dict(sorted(hierarchy.items(), key=lambda item: item[1]))
    print(sorted_hierarchy)
    jsonHierarchy = JsonObject(json_obj=sorted_hierarchy)
    print(jsonHierarchy.to_str(4))
