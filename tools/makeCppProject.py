#!/bin/env python3

import argparse
import os
import sys
from enum import auto
from colorama import Fore, Style

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


def add_licence_comments(uncommented: str, comment_style: CommentStyle, filename: str = None) -> str:
    reval = comment_style.start() + "\n"
    if filename is not None:
        reval += comment_style.cont() + f"Filename: {filename}\n"
        reval += comment_style.cont() + "\n"
    for line in uncommented.split("\n"):
        reval += comment_style.cont() + line + "\n"
    reval += comment_style.end()

    return reval


def replace_templates(project_name: str,
                      tmplt_text: str,
                      root_dir: (str | PathLike),
                      filename: str,
                      boost_dir: str,
                      comment_style: CommentStyle) -> str:
    git_config = get_git_config()
    licence_str = ""
    if os.path.isfile(f"{root_dir}/licence/licence"):
        licence_str = read_file(filename=f"{root_dir}/licence/licence")
        licence_str = add_licence_comments(licence_str, comment_style, filename)
    tmplt_text = tmplt_text.replace("[[FILENAME]]", filename)
    tmplt_text = tmplt_text.replace("[[YEAR]]", now_year())
    tmplt_text = tmplt_text.replace("[[AUTHOR]]", git_config["user.name"])
    tmplt_text = tmplt_text.replace("[[EMAIL]]", git_config["user.email"])
    tmplt_text = tmplt_text.replace("[[LICENCE]]", licence_str)
    tmplt_text = tmplt_text.replace("[[PROJECT_NAME_TEMPLATE]]", project_name)
    tmplt_text = tmplt_text.replace("[[PROJECT_NAME_TEMPLATE_UPPER]]", project_name.upper())
    tmplt_text = tmplt_text.replace("[[PROJECT_NAME_TEMPLATE_LOWER]]", project_name.lower())
    tmplt_text = tmplt_text.replace("[[TODAY]]", now_date())
    tmplt_text = tmplt_text.replace("[[BOOST_DIR]]", boost_dir)
    return tmplt_text


def write_project_file(project_name: str,
                       root_dir: (str | PathLike),
                       template_file: str,
                       project_file: str,
                       boost_dir: str,
                       comment_style: CommentStyle):
    template_file_base = os.path.basename(template_file)
    content = read_file(template_file)
    target_file = template_file.replace(f"{this_dir}/templates", root_dir).replace(template_file_base, project_file)
    content = replace_templates(project_name=project_name,
                                tmplt_text=content,
                                root_dir=root_dir,
                                filename=project_file,
                                boost_dir=boost_dir,
                                comment_style=comment_style)
    write_file(filename=target_file, content=content)


def create_cmake_project(project_path: (str, os.PathLike), boost_dir: str):
    remove(project_path)
    project_name = os.path.basename(project_path)
    # Create the project directory and subdirectories
    mkdir(f"{project_path}/include")
    mkdir(f"{project_path}/src")
    mkdir(f"{project_path}/test")

    write_project_file(project_name=project_name,
                       root_dir=project_path,
                       template_file=f"{this_dir}/templates/licence/licence",
                       project_file="licence",
                       boost_dir=boost_dir,
                       comment_style=CommentStyle.NONE)

    tmp_proj_map = {
        f"{this_dir}/templates/.vscode/c_cpp_properties.json": (f"c_cpp_properties.json", CommentStyle.NONE),
        f"{this_dir}/templates/.vscode/launch.json": (f"launch.json", CommentStyle.NONE),
        f"{this_dir}/templates/.vscode/settings.json": (f"settings.json", CommentStyle.NONE),
        f"{this_dir}/templates/.vscode/tasks.json": (f"tasks.json", CommentStyle.NONE),
        f"{this_dir}/templates/CMakeLists.txt": (f"CMakeLists.txt", CommentStyle.CMAKE),
        f"{this_dir}/templates/Dockerfile": (f"Dockerfile", CommentStyle.DOCKER),
        f"{this_dir}/templates/docker-compose.yml": (f"docker-compose.yml", CommentStyle.DOCKER),
        f"{this_dir}/templates/.env": (f".env", CommentStyle.DOCKER),
        f"{this_dir}/templates/bash_aliases_for_docker": (f"bash_aliases_for_docker", CommentStyle.DOCKER),
        f"{this_dir}/templates/makeDocker": (f"makeDocker", CommentStyle.BASH),
        f"{this_dir}/templates/.gitignore": (f".gitignore", CommentStyle.BASH),
        f"{this_dir}/templates/.clang-format": (f".clang-format", CommentStyle.BASH),
        f"{this_dir}/templates/Doxyfile": (f"Doxyfile", CommentStyle.BASH),
        f"{this_dir}/templates/include/project_include.h": (f"{project_name.lower()}.h", CommentStyle.CPP),
        f"{this_dir}/templates/src/project_main.cc": (f"{project_name.lower()}_main.cc", CommentStyle.CPP),
        f"{this_dir}/templates/src/project_source.cc": (f"{project_name.lower()}.cc", CommentStyle.CPP),
        f"{this_dir}/templates/src/CMakeLists.txt": (f"CMakeLists.txt", CommentStyle.CMAKE),
        f"{this_dir}/templates/test/project_tests.cc": (f"run_{project_name.lower()}_tests.cc", CommentStyle.CPP),
        f"{this_dir}/templates/test/CMakeLists.txt": (f"CMakeLists.txt", CommentStyle.CMAKE)
    }

    for template_file in tmp_proj_map.keys():
        project_file = tmp_proj_map[template_file][0]
        comment_style = tmp_proj_map[template_file][1]
        write_project_file(project_name=project_name,
                           root_dir=project_path,
                           template_file=template_file,
                           project_file=project_file,
                           boost_dir=boost_dir,
                           comment_style=comment_style)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a CMake project with Docker Compose files')
    parser.add_argument("--root_dir", "-r",
                        default=f"/home/{getuser()}/Repos/CPP",
                        type=str,
                        help='Root directory for the project')
    parser.add_argument("--boost_dir", "-b",
                        default=f"/usr/local",
                        type=str,
                        help='Install directory of boost - for docker-compose volume')
    parser.add_argument("--project_name", "-n",
                        type=str,
                        help='Name of the project')

    found_args = parser.parse_args()
    if is_empty_string(found_args.project_name):
        error("need a non-empty project name")
    if str(found_args.project_name).find(" ") != -1 \
            or str(found_args.project_name).find("\r") != -1 \
            or str(found_args.project_name).find("\t") != -1 \
            or str(found_args.project_name).find("\n") != -1:
        error("project name must not contain spaces")
    project_dir = valid_absolute_path(f"{found_args.root_dir}/{found_args.project_name}")

    create_cmake_project(project_dir, found_args.boost_dir)
    os.chmod(f"{project_dir}/makeDocker", 0o776)
    run_command(cmd="git init", cwd=project_dir)
    files_to_add_to_git = find(paths=project_dir, file_type_filter=FileSystemObjectType.FILE)
    for file in files_to_add_to_git:
        run_command(cmd=f"git add {file}", cwd=project_dir)
    run_command(cmd=["git", "commit", "-m", "initial checkin"], cwd=project_dir)
    run_command(cmd=f"{project_dir}/makeDocker", cwd=project_dir)
    log_info(f"Project '{found_args.project_name}' has been created successfully in "
             f"{Fore.MAGENTA}{project_dir}{Style.RESET_ALL}.")
