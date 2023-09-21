#!/bin/env python3

import argparse
import os
import sys

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/..")
sys.path.insert(0, dk_lib_dir)

from lib.bash import get_logged_in_user, assert_is_root
from lib.file_system_object import mkdir, find, FileSystemObjectType, symbolic_link, cp, chown

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

    local_inc_dir = mkdir(f"{found_args.local_dir}/include{prj_sub}", expect_1=True)
    inc_dir = mkdir(f"{found_args.install_dir}/include{prj_sub}",  expect_1=True, allow_system_paths=True)

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
        symbolic_link(existing_path=target,  new_link=bin_dir, overwrite_link=True, allow_system_paths=True)
