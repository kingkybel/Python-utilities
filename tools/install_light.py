#!/bin/env python3
# Repository:   https://github.com/Python-utilities
# File Name:    tools/install_light.py
# Description:  copy files from this library to a folder in the $PATH
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

import argparse
import os
import sys

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/../../Python-utilities")
if not os.path.isdir(dk_lib_dir):
    raise FileNotFoundError(f"Library directory '{dk_lib_dir}' cannot be found")
sys.path.insert(0, dk_lib_dir)

from lib.bash import get_logged_in_user, assert_is_root
from lib.file_system_object import mkdir, find, FileSystemObjectType, symbolic_link, cp, chown
from lib.string_utils import input_value

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=
        """Install "light": copy include, libs, bins into a local folder and symbolically link from a system folder""")

    parser.add_argument(
        "--project", "-p",
        default=None,
        type=str,
        help="alnum project-name. will be appended to include-directory as sub-dir, if not None, default None")
    parser.add_argument(
        "--root_dir", "-r",
        default=f".",
        type=str,
        help='Location of include, build/bin and build/lib folders')
    parser.add_argument(
        "--install-dir", "-i",
        default="/usr/local",
        type=str,
        help='folder to install to')
    parser.add_argument(
        "--local-dir", "-l",
        default=f"/home/{get_logged_in_user()}/local_install",
        type=str,
        help='local folder to copy files to')

    found_args = parser.parse_args()
    assert_is_root()
    user = get_logged_in_user()

    prj_sub = ""
    if found_args.project is not None:
        prj_sub = f"/{found_args.project}"
    else:
        accept_empty_prj_sub = input_value(var_name="accept_empty_prj_sub",
                                           var_type=bool,
                                           help_str="Accept empty project sub-directory? ")
        if not accept_empty_prj_sub:
            exit(0)

    local_inc_dir = mkdir(f"{found_args.local_dir}/include{prj_sub}", expect_1=True)
    inc_dir = mkdir(f"{found_args.install_dir}/include{prj_sub}", expect_1=True, allow_system_paths=True)

    local_lib_dir = mkdir(f"{found_args.local_dir}/lib{prj_sub}", expect_1=True)
    lib_dir = mkdir(f"{found_args.install_dir}/lib{prj_sub}", expect_1=True, allow_system_paths=True)

    bin_dir = mkdir(f"{found_args.install_dir}/bin{prj_sub}", expect_1=True, allow_system_paths=True)
    local_bin_dir = mkdir(f"{found_args.local_dir}/bin{prj_sub}", expect_1=True)

    chown([f"{found_args.local_dir}/*", f"{found_args.local_dir}/*/*"], user)

    include_files = find(paths=f"{found_args.root_dir}/include", file_type_filter=FileSystemObjectType.FILE)
    for inc in include_files:
        target = f"{local_inc_dir}/{os.path.basename(inc)}"
        cp(paths=inc, target=target)
        chown(target, user)
        symbolic_link(existing_path=target, new_link=inc_dir, overwrite_link=True, allow_system_paths=True)

    lib_files = find(paths=f"{found_args.root_dir}/build/lib", file_type_filter=FileSystemObjectType.FILE)
    for lib in lib_files:
        target = f"{local_lib_dir}/{os.path.basename(lib)}"
        cp(paths=lib, target=target)
        chown(target, user)
        symbolic_link(existing_path=target, new_link=lib_dir, overwrite_link=True, allow_system_paths=True)

    bin_files = find(paths=f"{found_args.root_dir}/build/bin", file_type_filter=FileSystemObjectType.FILE)
    for exe in bin_files:
        target = f"{local_bin_dir}/{os.path.basename(exe)}"
        cp(exe, target)
        chown(target, user)
        symbolic_link(existing_path=target, new_link=bin_dir, overwrite_link=True, allow_system_paths=True)
