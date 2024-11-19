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

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/../../../Python-utilities")
if not os.path.isdir(dk_lib_dir):
    raise FileNotFoundError(f"Library directory '{dk_lib_dir}' cannot be found")
sys.path.insert(0, dk_lib_dir)

# pylint: disable=wrong-import-position
from lib.logger import error
from lib.file_system_object import pushdir, popdir
from lib.json_object import JsonObject
from lib.bash import run_command


def get_current_branch(project_dir: PathLike):
    """Get the current Git branch name."""
    pushdir(project_dir)
    result, std_out, std_err = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    popdir()
    if result != 0:
        error(f"Failed to get current branch name: {std_err}", error_code=result)

    return std_out.strip()


def get_git_remote_url():
    """Get the Git remote URL."""
    result, std_out, std_err = run_command(["git", "remote", "get-url", "origin"])
    if result != 0:
        error(f"Failed to get remote-url: {std_err}", error_code=result)
    return std_out.strip()


def extract_gitlab_project_id(access_token, repo_name):
    """Extract the GitLab project ID from the remote URL."""

    result, std_out, std_err = run_command(
        ['curl',
         '--header',
         f'Private-Token: {access_token}',
         '-X',
         'GET',
         f'https://gitlab.com/api/v4/projects?search={repo_name}'])
    if result != 0:
        error(f"Failed to get remote-url: {std_err}", error_code=result)
    project_id = JsonObject(json_str=std_out.strip()).get("[^]/id")
    return project_id


def get_merge_request_status(api_url, project_id, branch_name, access_token) -> JsonObject:
    """Get the merge request status for the current branch."""
    headers = {"PRIVATE-TOKEN": access_token}
    url = f"{api_url}/projects/{project_id}/merge_requests"
    params = {"source_branch": branch_name}
    response = requests.get(url=url, headers=headers, params=params, timeout=30)

    if response.status_code != 200:
        print(f"Error: Unable to fetch merge requests. {response.text}")
        sys.exit(1)

    reval = JsonObject("[]")
    merge_requests = JsonObject(json.dumps(response.json()))
    if merge_requests.empty():
        reval.set("success", False, force=True)
        reval.set("error",
                  f"no merge-request on gitlab-project_id {project_id} for branch {branch_name}",
                  force=True)
        return reval

    for i in range(0, merge_requests.size()):
        reval.set(f"[{i}]/success", True, force=True)
        reval.set(f"[{i}]/branch", branch_name, force=True)
        reval.set(f"[{i}]/title", merge_requests.get(f"[{i}]/title"), force=True)
        reval.set(f"[{i}]/author", merge_requests.get(f"[{i}]/author/name"), force=True)
        reval.set(f"[{i}]/merge_request_id", merge_requests.get(f"[{i}]/id"), force=True)
        reval.set(f"[{i}]/state", merge_requests.get(f"[{i}]/state"), force=True)
        reval.set(f"[{i}]/url", merge_requests.get(f"[{i}]/web_url"), force=True)
        reval.set(f"[{i}]/source_branch", merge_requests.get(f"[{i}]/source_branch"), force=True)
        reval.set(f"[{i}]/target_branch", merge_requests.get(f"[{i}]/target_branch"), force=True)

    return reval


def main(project_dir: PathLike | str) -> JsonObject:
    api_url = "https://gitlab.com/api/v4"  # Adjust for self-hosted GitLab instances
    access_token = os.getenv("GITLAB_TOKEN")  # Set as an environment variable

    if not access_token:
        print("Error: Please set the GITLAB_TOKEN environment variable.")
        sys.exit(1)

    branch_name = get_current_branch(project_dir)
    print(f"Current branch: {branch_name}")

    project = os.path.basename(project_dir)
    project_id = extract_gitlab_project_id(access_token=access_token, repo_name=project)
    print(f"Project ID: {project_id}")

    return get_merge_request_status(api_url, project_id, branch_name, access_token)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check the status of open merge requests.")
    parser.add_argument("--project", "-p",
                        type=str,
                        required=True,
                        default=None,
                        help='Project to check the status of merge requests.',
                        )
    args = parser.parse_args()
    merge_requests = main(f"/home/dkybelksties/Repos/{args.project}")
    print(merge_requests.to_str())
