# Repository:   https://github.com/Python-utilities
# File Name:    lib/file_system_object.py
# Description:  classes and functions to deal with files, folders, symbolic links etc.
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
import glob
import grp
import os
import pwd
import shutil
import sys
from datetime import datetime
from enum import auto
from os import PathLike
from pathlib import Path
from shutil import copytree
import psutil

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/../../Python-utilities")
if not os.path.isdir(dk_lib_dir):
    raise FileNotFoundError(f"Library directory '{dk_lib_dir}' cannot be found")
sys.path.insert(0, dk_lib_dir)

# pylint: disable=wrong-import-position
from lib.basic_functions import is_empty_string, valid_absolute_path
from lib.extended_enum import ExtendedFlag, ExtendedEnum, always_match
from lib.logger import error, log_warning, log_command
from lib.overrides import overrides
from lib.string_utils import matches_any


class FindSortField(ExtendedEnum):
    NONE = 0
    BY_NAME = 1
    BY_TYPE = 2
    BY_DEPTH = 3


class FileSystemObjectType(ExtendedFlag):
    NONE = 0
    FILE = 1
    EMPTY_DIR = auto()
    NOT_EMPTY_DIR = auto()
    STALE_LINK = auto()
    NOT_STALE_LINK = auto()
    MOUNT = auto()
    DIR = EMPTY_DIR | NOT_EMPTY_DIR
    LINK = STALE_LINK | NOT_STALE_LINK
    ALL = FILE | DIR | LINK | MOUNT

    @classmethod
    def from_file_system_object(cls, file_system_object: (str | PathLike)):
        if isinstance(file_system_object, PathLike):
            file_system_object = str(file_system_object)
        if is_empty_string(file_system_object):
            return FileSystemObjectType.NONE

        if os.path.exists(file_system_object):
            if os.path.isfile(file_system_object):
                return FileSystemObjectType.FILE
            if os.path.isdir(file_system_object):
                if len((os.listdir(file_system_object))) == 0:
                    return FileSystemObjectType.EMPTY_DIR
                return FileSystemObjectType.NOT_EMPTY_DIR
            if os.path.islink(file_system_object):
                return FileSystemObjectType.NOT_STALE_LINK
            if os.path.ismount(file_system_object):
                return FileSystemObjectType.MOUNT
        elif os.path.islink(file_system_object):
            return FileSystemObjectType.STALE_LINK
        return FileSystemObjectType.NONE

    @classmethod
    @overrides
    def from_string(cls, partial: str, predicate=always_match):
        sorted_partial = "".join(sorted(partial, key=str.lower))
        if sorted_partial == "f":
            return FileSystemObjectType.FILE
        if sorted_partial == "d":
            return FileSystemObjectType.DIR
        if sorted_partial == "df":
            return FileSystemObjectType.FILE | FileSystemObjectType.DIR
        if sorted_partial == "fl":
            return FileSystemObjectType.FILE | FileSystemObjectType.LINK
        if sorted_partial == "dl":
            return FileSystemObjectType.DIR | FileSystemObjectType.LINK
        if sorted_partial == "dfl":
            return FileSystemObjectType.DIR | FileSystemObjectType.FILE | FileSystemObjectType.LINK
        return super().from_string(partial=partial, predicate=predicate)


class GlobMode(ExtendedEnum):
    IGNORE_EMPTY = auto()
    FAIL_ON_EMPTY = auto()
    KEEP_EMPTY = auto()
    WARN_EMPTY = auto()


def make_path_list(paths: (str | PathLike | list)) -> list[str]:
    if isinstance(paths, PathLike):
        paths = str(paths)
    if isinstance(paths, str):
        paths = [paths]
    if len(paths) == 0:
        error("path-list is empty")
    reval_paths = []
    for path in paths:
        if not isinstance(path, (str, PathLike)):
            error(f"paths contains path with invalid type '{path}'({type(path)})")
        if is_empty_string(path):
            error(f"paths contains empty path-strings {paths}")
        else:
            reval_paths.append(str(path))
    return reval_paths


def glob_path_patterns(paths: (str | PathLike | list), glob_mode: GlobMode = GlobMode.FAIL_ON_EMPTY) -> list:
    results = []
    paths = make_path_list(paths)

    for path in paths:
        globbed_paths = glob.glob(path)
        if globbed_paths is not None:
            if len(globbed_paths) > 0:
                results.extend(globbed_paths)
            elif glob_mode == GlobMode.KEEP_EMPTY:
                results.append(path)
            elif glob_mode == GlobMode.FAIL_ON_EMPTY:
                raise (FileNotFoundError(f"Globbing of path '{path}' did not yield results"))
            elif glob_mode == GlobMode.WARN_EMPTY:
                log_warning(f"Globbing of path '{path}' did not yield results")
            else:  # GobMode.IGNORE_EMPTY
                pass
        else:
            raise FileNotFoundError(f"Path '{path}' cannot be resoled by globbing")
    return results


def remove(paths: (str | PathLike | list),
           force: bool = False,
           allow_system_paths: bool = False,
           dryrun: bool = False):
    glob_mode = GlobMode.WARN_EMPTY
    if force:
        glob_mode = GlobMode.KEEP_EMPTY
    paths = glob_path_patterns(paths, glob_mode=glob_mode)
    log_command(f"rm -rf {paths}", dryrun=dryrun)
    if not dryrun:
        for path in paths:
            path = valid_absolute_path(path, allow_system_paths=allow_system_paths)
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=force)
                elif os.path.islink(path):
                    os.unlink(path)
                else:
                    os.remove(path)
            except FileNotFoundError:
                pass


def set_file_last_modified(paths: (str | PathLike | list), dt: datetime, dryrun: bool = False) -> list:
    paths = glob_path_patterns(paths, glob_mode=GlobMode.WARN_EMPTY)
    modified = []
    if not dryrun:
        for path in paths:
            dt_epoch = dt.timestamp()
            os.utime(path, (dt_epoch, dt_epoch))
            modified.append(path)
    return modified


def touch(paths: (str | PathLike | list),
          glob_mode: GlobMode = GlobMode.KEEP_EMPTY,
          allow_system_paths: bool = False,
          dryrun: bool = False):
    paths = glob_path_patterns(paths, glob_mode=glob_mode)
    if not dryrun:
        touched = []
        for path in paths:
            path = valid_absolute_path(path, allow_system_paths=allow_system_paths)
            parent_path = os.path.dirname(path)
            log_command(f"touch {path}")
            if not os.path.isdir(parent_path):
                mkdir(parent_path)
                touched.append(parent_path)
            if os.path.islink(path) or os.path.isdir(path):
                set_file_last_modified(path, dt=datetime.now())
            else:
                with open(path, "a", encoding="utf-8") as f:
                    f.close()
            touched.append(path)
    else:
        return 0, []
    if len(touched) == 0:
        return -1, None
    return 0, touched


def mkdir(paths: (str | PathLike | list),
          force: bool = False,
          recreate: bool = False,
          expect_1: bool = False,
          allow_system_paths: bool = False,
          dryrun: bool = False):
    paths = glob_path_patterns(paths, glob_mode=GlobMode.KEEP_EMPTY)
    log_command(f"mkdir {paths}", dryrun=dryrun)
    created_paths = []
    if not dryrun:
        for path in paths:
            path = valid_absolute_path(path, allow_system_paths=allow_system_paths)
            if os.path.isfile(path) and not recreate:
                raise FileExistsError(f"Cannot create directory {path}. Path is regular file")
            try:
                if recreate:
                    remove(paths=path, force=force)
                os.makedirs(path, exist_ok=force)
                created_paths.append(path)
            except FileExistsError:
                created_paths.append(path)

    if len(created_paths) == 1 and expect_1:
        return created_paths[0]
    if expect_1:
        error(f"Expected to create exactly one directory but created {len(created_paths)} {created_paths}")
    return created_paths


def symbolic_link(existing_path: (str | PathLike),
                  new_link: (str | PathLike),
                  overwrite_link: bool = False,
                  allow_system_paths: bool = False,
                  dryrun: bool = False):
    if isinstance(existing_path, PathLike):
        existing_path = str(existing_path)
    if isinstance(new_link, PathLike):
        new_link = str(new_link)
    if os.path.isdir(new_link):
        new_link = f"{new_link}/{os.path.basename(existing_path)}"
    if not dryrun:
        if is_empty_string(existing_path):
            error(f"Cannot link empty path to {new_link}")
        force = ""
        if overwrite_link and (os.path.exists(new_link) or os.path.islink(new_link)):
            remove(new_link, allow_system_paths=allow_system_paths, force=True)
            force = "-f "
        log_command(f"ln {force}-s {existing_path} {new_link}")
        symlink = Path(new_link)
        symlink.symlink_to(existing_path)


def current_dir() -> str:
    try:
        cwd = os.getcwd()
    except OSError:
        cwd = psutil.Process(os.getpid()).cwd()
    return valid_absolute_path(cwd, protect_system_patterns=[])


push_stack = []


def pushdir(path: (str | PathLike), dryrun: bool = False):
    global push_stack
    push_stack.append(current_dir())
    log_command(f"pushd {path}", dryrun=dryrun)
    if not dryrun:
        os.chdir(path)


def popdir(dryrun: bool = False):
    global push_stack
    current = current_dir()
    if len(push_stack) > 0:
        current = push_stack.pop()
        os.chdir(current)
        log_command("popd", extra_comment=f"leaving {current}", dryrun=dryrun)
    else:
        log_command(";", extra_comment=f"popd stack empty. Staying in {current}")


def find(paths: (str | PathLike | list),
         file_type_filter: (str | FileSystemObjectType) = FileSystemObjectType.ALL,
         name_patterns: (str | list) = None,
         exclude_patterns: (str | list) = None,
         sort_field: FindSortField = FindSortField.NONE,
         reverse: bool = False,
         allow_system_paths: bool = False,
         dryrun: bool = False):
    paths = glob_path_patterns(paths)
    _validate_paths_are_directories(paths)

    pattern_str = _build_name_pattern_string(name_patterns)
    file_type_str = f" -type ({file_type_filter})"
    log_command(f"find {' '.join(paths)}{file_type_str}{pattern_str}", dryrun=dryrun)

    if dryrun:
        return []

    augmented_path_list = _collect_augmented_paths(
        paths, file_type_filter, name_patterns, exclude_patterns, allow_system_paths
    )

    result_path_list = _sort_and_extract_paths(
        augmented_path_list, sort_field, reverse
    )

    return result_path_list


def _validate_paths_are_directories(paths):
    """Validate that all paths are directories."""
    list_of_non_directories = [path for path in paths if not os.path.isdir(path)]
    if list_of_non_directories:
        error(f"The following paths are not directories {list_of_non_directories}")


def _build_name_pattern_string(name_patterns):
    """Build the name pattern string for the find command."""
    if not name_patterns:
        return ""
    if isinstance(name_patterns, str):
        return f' -name "{name_patterns}"'
    return " ".join(f'-name "{pattern}"' + (" -o" if idx < len(name_patterns) - 1 else "")
                    for idx, pattern in enumerate(name_patterns))


def _collect_augmented_paths(paths,
                             file_type_filter,
                             name_patterns,
                             exclude_patterns,
                             allow_system_paths,
                             max_dive: int = None):
    """Collect paths with additional properties such as type and depth."""
    augmented_path_list = []
    for path in paths:
        min_depth = path.count(os.path.sep)
        # pylint: disable=unused-variable
        for dir_name, sub_dir_list, file_list in os.walk(path):
            depth = dir_name.count(os.path.sep)
            if max_dive is None or (depth - min_depth) < max_dive:
                path.count(os.path.sep)
                _process_directory(
                    dir_name, file_type_filter, name_patterns, exclude_patterns, allow_system_paths, depth,
                    augmented_path_list
                )
                _process_files(
                    dir_name, file_list, file_type_filter, name_patterns, exclude_patterns, allow_system_paths, depth,
                    augmented_path_list
                )
    return augmented_path_list


def _process_directory(dir_name, file_type_filter, name_patterns, exclude_patterns, allow_system_paths, depth, result):
    """Process directories and add matching ones to the result."""
    if FileSystemObjectType.DIR & file_type_filter == FileSystemObjectType.DIR:
        if _matches_filters(dir_name, name_patterns, exclude_patterns):
            result.append(
                (valid_absolute_path(dir_name, allow_system_paths=allow_system_paths),
                 FileSystemObjectType.DIR.value,
                 depth)
            )


def _process_files(dir_name, file_list, file_type_filter, name_patterns, exclude_patterns, allow_system_paths, depth,
                   result):
    """Process files and add matching ones to the result."""
    for file in file_list:
        file_path = f"{dir_name}/{file}"
        if _matches_filters(file, name_patterns, exclude_patterns):
            full_path = valid_absolute_path(file_path, allow_system_paths=allow_system_paths)
            file_type = FileSystemObjectType.from_file_system_object(full_path)
            if file_type & file_type_filter == file_type:
                result.append((full_path, file_type.value, depth))


def _matches_filters(search_string, name_patterns, exclude_patterns):
    """Check if a string matches the include and exclude patterns."""
    matches = True
    if name_patterns:
        matches = matches_any(search_string=search_string, patterns=name_patterns)
    if exclude_patterns and matches:
        matches = not matches_any(search_string=search_string, patterns=exclude_patterns)
    return matches


def _sort_and_extract_paths(augmented_path_list, sort_field, reverse):
    """Sort the augmented paths and extract the path strings."""
    if sort_field != FindSortField.NONE:
        sort_index = sort_field.value - 1
        augmented_path_list.sort(key=lambda i: i[sort_index], reverse=reverse)
    else:
        augmented_path_list.sort(reverse=reverse)
    return [item[0] for item in augmented_path_list]


def is_stale_link(path: (str | PathLike)):
    return FileSystemObjectType.from_file_system_object(path) == FileSystemObjectType.STALE_LINK


def is_empty_dir(path: (str | PathLike)):
    return FileSystemObjectType.from_file_system_object(path) == FileSystemObjectType.EMPTY_DIR


def remove_stale_links(paths: (str | PathLike | list), dryrun: bool = False):
    log_command(f"remove_stale_links {paths}", extra_comment="python function", dryrun=dryrun)
    if not dryrun:
        paths = glob_path_patterns(paths)
        all_stale_links = find(paths=paths,
                               file_type_filter=FileSystemObjectType.STALE_LINK,
                               sort_field=FindSortField.BY_DEPTH,
                               reverse=True)
        for stale_link in all_stale_links:
            remove(stale_link)


def remove_empty_dirs(paths: (str | PathLike | list), dryrun: bool = False):
    log_command(f"remove_stale_links {paths}", extra_comment="python function", dryrun=dryrun)
    if not dryrun:
        paths = glob_path_patterns(paths)
        all_empty_dirs = find(paths=paths,
                              file_type_filter=FileSystemObjectType.EMPTY_DIR,
                              sort_field=FindSortField.BY_DEPTH,
                              reverse=True)
        for empty_dir in all_empty_dirs:
            remove(empty_dir)


def cp(paths: (str | PathLike | list), target: (str | PathLike), dryrun: bool = False):
    """
    Copy file-system objects to a target
    cases:
        1) path is a directory and target is existing directory:
           -> copy whole directory into the target(-dir), thus making a subdirectory
        2) path is a directory and target is existing file or symbolic link:
           -> ERROR: cannot copy a directory onto file or link
        3) path is directory and target is link to existing directory:
           -> copy directory onto target, thus making a subdirectory to the one the link is referring
        4) path is directory and target does not exist and is no link
           -> mkdir the target and copy contents of path into this new directory
        5) path is file and target is (link to) directory
           -> copy the file into the directory
        6) path is file and target existing file or does not exist at all
          -> create the target path if necessary and (possibly over-)write the file
    :param paths:
    :param target:
    :param dryrun:
    """
    log_command(f"cp -R {paths} {target}", dryrun=dryrun)
    if not dryrun:
        paths = glob_path_patterns(paths)
        for path in paths:
            if os.path.isdir(path) and os.path.isdir(target):
                target_dir = f"{target}/{os.path.basename(path)}"
                if (os.path.exists(target_dir) or os.path.islink(target_dir)) and not os.path.isfile(target_dir):
                    remove(target_dir)
                shutil.copytree(path, target_dir)
            elif os.path.isdir(path) and os.path.isfile(target):
                error(f"Cannot copy directory '{path}' onto regular file '{target}'")
            elif os.path.isdir(path) and not os.path.exists(target):
                # make sure there's no dangling link
                remove(target)
                mkdir(target)
                copytree(src=path, dst=f"{target}/{os.path.basename(path)}")
            elif os.path.isfile(path) and os.path.isdir(target):
                target_file = f"{target}/{os.path.basename(path)}"
                if os.path.exists(target_file) or os.path.isdir(target_file):
                    remove(target_file)
                    shutil.copy(path, target_file)
            elif os.path.isfile(path):  # and (os.path.isdir(target)) or not os.path.exists(target)
                mkdir(os.path.dirname(target))
                remove(target)
                shutil.copy(path, target)
            else:
                error(f"Cannot copy '{path}' to '{target}'")


def mv(paths: (str | PathLike | list[str | PathLike]), target: (str | PathLike), dryrun: bool = False):
    log_command(f"mv {paths} {target}", dryrun=dryrun)
    paths = glob_path_patterns(paths)
    if len(paths) > 1 and not os.path.isdir(target):
        error(f"Cannot move multiple files to target-file '{target}'")
    for path in paths:
        shutil.move(path, target)


def chown(paths: (str | PathLike | list[str | PathLike]),
          user: (str | int),
          group: (str | int) = None,
          dryrun: bool = False):
    if group is None:
        group = user
    log_command(f"chown {user}:{group} {paths}", dryrun=dryrun)
    paths = glob_path_patterns(paths)
    for path in paths:
        uid = pwd.getpwnam(user).pw_uid
        gid = grp.getgrnam(group).gr_gid
        os.chown(path, uid, gid)
