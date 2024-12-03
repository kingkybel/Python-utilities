from __future__ import annotations

from os import PathLike

from lib.bash import assert_tools_installed, run_command
from lib.basic_functions import valid_absolute_path
from lib.file_system_object import pushdir, popdir
from lib.file_utils import extract_dict_from_string
from lib.logger import error, log_warning


def get_git_remote_url(path: (str | PathLike) = None,
                       allow_system_paths: bool = False,
                       dryrun: bool = False):
    """
    Get the Git remote URL.
    :param path: optional git repository path to check, default is the current working directory
    :param allow_system_paths: allow paths relative to the current working directory
    :param dryrun: go through the motions only
    :return: the url of the Git remote on gitlab.
    """
    if path is None:
        path = valid_absolute_path(".", allow_system_paths=allow_system_paths)
    assert_tools_installed("git")
    result, std_out, std_err = run_command(["git", "remote", "get-url", "origin"], dryrun=dryrun)
    if result != 0:
        error(f"Failed to get remote-url: {std_err}", error_code=result)
    return std_out.strip()


def get_git_config(path: (str | PathLike) = None,
                   allow_system_paths: bool = False,
                   dryrun: bool = False) -> dict[str, str]:
    """
    Extract git config from given git repository located at path.
    :param path: path to git repository.
    :param allow_system_paths: allow to manipulate system paths
    :param dryrun: if set to True, then do not execute but just output a comment describing the command.
    :return:
    """
    key_val_dict = {}
    if path is None:
        path = valid_absolute_path(".", allow_system_paths=allow_system_paths)
    assert_tools_installed("git")
    reval, s_out, s_err = run_command(cmd="git config --list", cwd=path, raise_errors=False, dryrun=dryrun)
    if reval != 0:
        error(f"Could not retrieve git-config in path '{path}': {s_err}")
    if not dryrun:
        key_val_dict = extract_dict_from_string(s_out)

    return key_val_dict


def get_current_local_branch(path: PathLike | str,
                             allow_system_paths: bool = False,
                             dryrun: bool = False):
    """
    Get the current local git branch name.
    :param: project_dir: the directory where the current branch is located.
    :return: local branch name
    """
    if path is None:
        path = valid_absolute_path(".", allow_system_paths=allow_system_paths)
    pushdir(path)
    result, std_out, std_err = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                                           raise_errors=False,
                                           dryrun=dryrun)
    popdir()
    if result != 0:
        log_warning(f"Failed to get current branch name: {std_err}. Skipping.")

    return std_out.strip()
