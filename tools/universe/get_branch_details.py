#!/bin/env python3

# Repository:   https://github.com/Python-utilities
# File Name:    tools/UniVerse/get_branch_details.py
# Description:  connect to UniVerse and get BranchDetails
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
# @date: 2024-10-02
# @author: Dieter J Kybelksties


import argparse
import os
import sys
import uopy
import re

from colorama import Fore, Style

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/../../../Python-utilities")
if not os.path.isdir(dk_lib_dir):
    raise FileNotFoundError(f"Library directory '{dk_lib_dir}' cannot be found")
sys.path.insert(0, dk_lib_dir)

from lib.logger import error,log_info




def validate_ip_address(ip: str) -> bool:
    """
    Checks if the given IP address is valid.
    param ip: The IP address to validate.
    returns: True if the IP address is valid, False otherwise.
    """
    # Regular expression pattern for matching a valid IPv4 address
    ip_pattern = re.compile(r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
                            r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')

    # Check if the IP address matches the pattern
    if ip_pattern.match(ip):
        return True
    return False


def get_connection_details_from_environment() -> tuple[str, str, str, str]:
    """
    Connection details are sensitive and should be stored in environment variables.
    This function gets the details from the environment variables.
    returns: universe_user, universe_password, universe_host, universe_port
    """
    return (os.environ['UNIVERSE_USER'],
            os.environ['UNIVERSE_PASSWORD'],
            os.environ['UNIVERSE_ACCOUNT'],
            os.environ['UNIVERSE_IP'])


def get_args() -> tuple[list[str], str, str, str, str]:
    """
    Get all the necessary arguments to connect to the UniVerse API.
    The sensitive arguments are stored in environment variables.
    Insensitive arguments are passed as command line arguments.
    returns: branch_numbers, universe_ip, universe_account, user, password
    """
    user, password, account, ip = get_connection_details_from_environment()

    parser = argparse.ArgumentParser(description='Get details of the given branches from UniVerse')
    parser.add_argument("--branch-numbers", "-b",
                        type=str,
                        nargs='+',
                        help=f'A list of branch numbers to get details for.')
    parser.add_argument("--universe_ip", "-i",
                        type=str,
                        default=ip,
                        help=f'IP address of the UniVerse, default:{ip}')
    parser.add_argument("--universe_account", "-a",
                        type=str,
                        default=account,
                        help=f'Account for connection, default:{account}')
    found_args = parser.parse_args()
    if not found_args.branch_numbers or len(found_args.branch_numbers) == 0:
        error("No branch numbers specified")
    if not validate_ip_address(found_args.universe_ip):
        error(f"Invalid IP address: {found_args.universe_ip}")

    return found_args.branch_numbers, found_args.universe_ip, found_args.universe_account, user, password


def connect_to_universe(uv_host: str, account: str, user, password):
    """
    Connects to the UniVerse.
    param uv_host: The hostname of the UniVerse server to connect to.
    param account: The account to connect to.
    param user: The user to use for connection.
    param password: The password to use for connection.
    returns: The connection to the UniVerse server.
    """
    session = uopy.connect(user=f'{user}', password=f'{password}', host=uv_host, account=account)
    return session


def call_get_branch_detail_subroutine(branch_code: str):
    """
    Call the UniVerse subroutine to get branch details with the given branch code.
    param branch_code: The branch code to call.
    returns: The branch details of the given branch code as an argument list.
    """
    universe_sub = uopy.Subroutine("JAS.QA.GET.BRANCH.DETAIL", 6)
    universe_sub.args[0] = branch_code
    universe_sub.call()
    return universe_sub.args


if __name__ == "__main__":
    branch_codes, ip, account, user, password = get_args()
    universe_session = None

    try:
        universe_session = connect_to_universe(uv_host=ip, account=account, user=user, password=password)
    except uopy.UOError as e:
        error(f'Cannot connect to UniVerse: {e}')

    for branch_code in branch_codes:
        try:
            get_branch_detail_args = call_get_branch_detail_subroutine(branch_code=branch_code)
        except uopy.UOError as e:
            print(e)
        else:
            branch_detail_error = str(get_branch_detail_args[5])
            if branch_detail_error != "":
                print(branch_detail_error)
            else:
                log_info(f"{str(get_branch_detail_args[1])}")
                branch_name = str(get_branch_detail_args[1])
                branch_pos_machine = str(get_branch_detail_args[2])
                branch_forward_order = str(get_branch_detail_args[3])
                branch_brand = str(get_branch_detail_args[4])
                print(f"{Style.RESET_ALL}Branch name    = {Fore.YELLOW}{branch_name}{Style.RESET_ALL}")
                print(f"{Style.RESET_ALL}Branch machine = {Fore.YELLOW}{branch_pos_machine}{Style.RESET_ALL}")
                print(f"{Style.RESET_ALL}Forward order  = {Fore.YELLOW}{branch_forward_order}{Style.RESET_ALL}")
                print(f"{Style.RESET_ALL}Brand          = {Fore.YELLOW}{branch_brand}{Style.RESET_ALL}")

    universe_session.close()
