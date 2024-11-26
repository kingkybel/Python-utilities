#!/bin/env python3

# Repository:   https://github.com/Python-utilities
# File Name:    tools/gitlab/check_merge_request.py
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
import argparse
import json
import os
import sys
from os import PathLike
import requests


GITLAB_COM_API_V_4 = "https://gitlab.com/api/v4"

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/../../../Python-utilities")
if not os.path.isdir(dk_lib_dir):
    raise FileNotFoundError(f"Library directory '{dk_lib_dir}' cannot be found")
sys.path.insert(0, dk_lib_dir)

# pylint: disable=wrong-import-position
from lib.exceptions import JsonError
from lib.file_utils import write_file
from lib.basic_functions import valid_absolute_path
from lib.logger import error, log_info, log_warning
from lib.file_system_object import pushdir, popdir, find, FileSystemObjectType
from lib.json_object import JsonObject
from lib.bash import run_command


def get_current_local_branch(project_dir: PathLike | str):
    """
    Get the current local git branch name.
    :param: project_dir: the directory where the current branch is located.
    :return: local branch name
    """
    pushdir(project_dir)
    result, std_out, std_err = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], raise_errors=False)
    popdir()
    if result != 0:
        log_warning(f"Failed to get current branch name: {std_err}. Skipping.")

    return std_out.strip()


def get_git_remote_url():
    """
    Get the Git remote URL.
    :return: the url of the Git remote on gitlab.
    """
    result, std_out, std_err = run_command(["git", "remote", "get-url", "origin"])
    if result != 0:
        error(f"Failed to get remote-url: {std_err}", error_code=result)
    return std_out.strip()


def extract_gitlab_project_id(access_token: str, repo_name: str) -> str | None:
    """
    Extract the GitLab project ID from the remote URL.
    :param: access_token: Access token for the current user
    :param: repo_name: name of the repository/project
    :return: the project id for the repository/project
    """
    result, std_out, std_err = run_command(
        ['curl',
         '--header',
         f'Private-Token: {access_token}',
         '-X',
         'GET',
         f'https://gitlab.com/api/v4/projects?search={repo_name}'])
    if result != 0:
        log_warning(f"Failed to get remote-url: {std_err}")
        return None

    try:
        project_id = (JsonObject(json_str=std_out.strip())).get("[^]/id")
    except JsonError as e:
        log_warning(f"Failed to get project-ID from '{std_out}': {e}")
        return None
    return project_id


def get_merge_request_status(api_url: str, project_id: str, branch_name: str, access_token: str) -> JsonObject:
    """
    Get the merge request status for the current branch.
    :param api_url: Gitlab-API URL
    :param project_id: the project ID for the repository/project
    :param branch_name: branch name to find merge-requests for
    :param access_token: Access token for the current user
    :return: a JsonObject with the merge request information
    """
    headers = {"PRIVATE-TOKEN": access_token}
    url = f"{api_url}/projects/{project_id}/merge_requests"
    params = {"source_branch": branch_name}
    response = requests.get(url=url, headers=headers, params=params, timeout=30)

    reval = JsonObject("[]")

    if response.status_code != 200:
        print()
        reval.set("success", False, force=True)
        reval.set("error",
                  f" Unable to fetch merge requests. {response.text} for {project_id} and branch {branch_name}",
                  force=True)
        reval.set("status_code",response.status_code, force=True)
        return reval

    merge_request_json = JsonObject(json.dumps(response.json()))
    if merge_request_json.empty():
        reval.set("success", False, force=True)
        reval.set("error",
                  f"no merge-request on gitlab-project_id {project_id} for branch {branch_name}",
                  force=True)
        return reval

    for i in range(0, merge_request_json.size()):
        reval.set("success", True, force=True)
        reval.set(f"merge_requests/[{i}]/branch", branch_name, force=True)
        reval.set(f"merge_requests/[{i}]/title", merge_request_json.get(f"[{i}]/title"), force=True)
        reval.set(f"merge_requests/[{i}]/author", merge_request_json.get(f"[{i}]/author/name"), force=True)
        reval.set(f"merge_requests/[{i}]/merge_request_id", merge_request_json.get(f"[{i}]/id"), force=True)
        reval.set(f"merge_requests/[{i}]/state", merge_request_json.get(f"[{i}]/state"), force=True)
        reval.set(f"merge_requests/[{i}]/url", merge_request_json.get(f"[{i}]/web_url"), force=True)
        reval.set(f"merge_requests/[{i}]/source_branch", merge_request_json.get(f"[{i}]/source_branch"), force=True)
        reval.set(f"merge_requests/[{i}]/target_branch", merge_request_json.get(f"[{i}]/target_branch"), force=True)

    return reval


def merge_requests_on_local_directories(project_dirs: list[PathLike | str]) -> JsonObject:
    access_token = os.getenv("GITLAB_TOKEN")  # Set as an environment variable

    if not access_token:
        print("Error: Please set the GITLAB_TOKEN environment variable.")
        sys.exit(1)

    merge_requests_combined = JsonObject("[]")
    for project_dir in project_dirs:
        branch_name = get_current_local_branch(project_dir)
        log_info(f"processing project_dir '{project_dir}'")
        project = os.path.basename(project_dir)
        project_id = extract_gitlab_project_id(access_token=access_token, repo_name=project)
        if project_id is not None:
            requests_on_this_project = get_merge_request_status(GITLAB_COM_API_V_4, project_id, branch_name,
                                                                access_token)
            merge_requests_combined.set("[$]", requests_on_this_project.get(), force=True)

    return merge_requests_combined


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check the status of open merge requests.")
    parser.add_argument("--output-file", "-o",
                        type=str,
                        default=None,
                        help="output file name, default output to stdout")
    local_or_remote = parser.add_mutually_exclusive_group(required=True)
    local_or_remote.add_argument("--project-name", "-p",
                                 type=str,
                                 default=None,
                                 nargs='+',
                                 help='Projects to check the status of merge requests.')
    local_or_remote.add_argument("--local-project-dir", "-l",
                                 type=str,
                                 default=None,
                                 nargs='+',
                                 help='individually listed local project directories.')
    local_or_remote.add_argument("--repo-base-dir", "-r",
                                 type=str,
                                 default=None,
                                 nargs='+',
                                 help='directories under which repo-directories are located.')

    local_dirs = []
    args = parser.parse_args()
    if args.project_name:
        do_local = False
    elif args.local_project_dir:
        local_dirs = args.local_project_dir
    elif args.repo_base_dir:
        local_dirs = find(paths=args.repo_base_dir, file_type_filter=FileSystemObjectType.DIR, min_depth=1, max_depth=1)
        print(local_dirs)

    merge_requests = merge_requests_on_local_directories(local_dirs)

    if args.output_file is not None:
        write_file(filename=valid_absolute_path(f"{this_dir}/{args.output_file}"), content=merge_requests.to_str())
    else:
        print(merge_requests.to_str())
