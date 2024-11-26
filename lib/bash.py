# Repository:   https://github.com/Python-utilities
# File Name:    lib/bash.py
# Description:  bash script-like utilities
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
import os
import sys
from os import PathLike
import pty
import re
import select
import socket
import subprocess
import termios
import tty
import urllib.request
from getpass import getuser
from multiprocessing import cpu_count
from shutil import which
from socket import gethostname
from typing import IO
from colorama import Fore, Style

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/../../Python-utilities")
if not os.path.isdir(dk_lib_dir):
    raise FileNotFoundError(f"Library directory '{dk_lib_dir}' cannot be found")
sys.path.insert(0, dk_lib_dir)

# pylint: disable=wrong-import-position
from lib.basic_functions import is_empty_string
from lib.file_system_object import current_dir, pushdir, popdir
from lib.logger import error, log_progress_output, LogLevels
from lib.string_utils import squeeze_chars
from lib.thread_with_return import ReturningThread


def get_effective_user() -> str:
    return getuser()


def get_logged_in_user() -> str:
    """
    Get the currently logged-in user
    :return: the username
    """
    try:
        return os.getlogin()
    except FileNotFoundError:  # happens on WSL
        return squeeze_chars(source=os.popen("whoami").read(), squeeze_set="\n\t\r ")
    except OSError:  # happens on docker
        return squeeze_chars(source=os.popen("whoami").read(), squeeze_set="\n\t\r ")


def assert_is_root():
    """
    Assert that the script is run with root privileges
    :raise SystemExit:
    """
    if get_effective_user() != "root":
        error(
            f"""This script needs to be run with root privileges.
Try: {Fore.MAGENTA}sudo {which('python')} {' '.join(sys.argv)}{Style.RESET_ALL}""")


def number_of_cores() -> int:
    """
    Get the number of available cores
    :return: the number of cores
    """
    return int(cpu_count())


def hostname() -> str:
    """
    Get the hostname
    :return: the hostname
    """
    return gethostname()


def get_ip() -> str:
    """
    Get the IP address
    :return: the IP address of this machine, if connected, default localhost address otherwise
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't have to be reachable
        s.connect(("10.254.254.254", 1))
        ip = s.getsockname()[0]
    except socket.error:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def get_external_ip() -> str:
    """
    Get the external IP address
    :return: the external IP address, if connected
    """
    return urllib.request.urlopen("https://ident.me").read().decode("utf8")


def ping(host_name: str = None) -> tuple[int, str]:
    """
    Ping the host
    :param host_name: the host name to ping
    :return: a tuple error code and error message
    """
    if is_empty_string(host_name):
        host_name = "127.0.0.1"
    ip = f"- {host_name} doesn't respond -"
    # pylint: disable=unused-variable
    reval, s_out, s_err = run_command(f"ping -c 1 {host_name}", raise_errors=False)
    if reval == 0:
        ip_list = re.findall(rf"PING {host_name}\s+\(([0-9.]+)\)", s_out)
        ip = ip_list[0]
    return reval, ip


def is_tool_installed(name: str) -> bool:
    """
    Check if the tool is installed
    :param name: name of the tool
    :return: True, if tool is installed, False otherwise
    """
    return which(name) is not None


def assert_tools_installed(tools: (str | list[str])):
    """
    Assert that the whole list of tools is installed
    :param tools: all the tools to check
    :raises SystemExit:
    """
    if isinstance(tools, str):
        tools = [tools]
    missing_tools = []
    for tool in tools:
        if not is_tool_installed(tool):
            missing_tools.append(tool)
    if len(missing_tools) > 0:
        error(f"Please install the following tools {missing_tools} "
              "to run this script (or add location to PATH variable)")


# pylint: disable=unused-argument
def check_correct_tool_version(tool: str, version: str) -> bool:
    """
    Check that the correct version of a tool is installed.
    TODO
    :param tool: the tool to check
    :param version: its version
    :return: True, if the tool is installed with correct version, False otherwise
    """
    if not is_tool_installed(tool):
        return False
    return True


def pipe_monitor_thread_function(pipe: IO[str|bytes], verbosity: LogLevels):
    """
    Function that runs as thread and is monitoring the output of a pipe.
    :param pipe: file-pipe: either stdin or stdout.
    :param verbosity: log-level so out put can be customised.
    :return: the string that was piped to the pipe.
    """
    piped_str = ""
    pipe_empty = 0
    for line in pipe:
        piped_str += line
        if is_empty_string(str(line.strip())):
            pipe_empty += 1
            if pipe_empty >= 10:
                break
        else:
            pipe_empty = 0
        log_progress_output(str(line.strip()), verbosity=verbosity)
    return piped_str


def run_command(cmd: (str | list[str]),
                cwd: (str | PathLike) = None,
                raise_errors: bool = True,
                comment: str = None,
                dryrun: bool = False) -> tuple[int, str, str]:
    """
    Run a command in a sub-process.
    :param cmd: command to execute.
    :param cwd: the working directory to use.
    :param raise_errors: if set to True (default) then raise errors instead of returning an error code.
    :param comment: a comment to enhance the log-output.
    :param dryrun: if set to True, then do not execute but just output a comment describing the command.
    :return: only if raise_errors == False: tuple (error-code, stout-string, stderr-string)
    """
    cmd, cmd_str, cwd = __prepare_run(cmd, comment, cwd, dryrun)

    return_code = 0
    if dryrun:
        popdir(dryrun=dryrun)
        return 0, "", ""

    with subprocess.Popen(cmd,
                          cwd=cwd,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          bufsize=1,
                          universal_newlines=True) as process:
        log_progress_output("-" * 10 + "sub-process output" + "-" * 10, verbosity=LogLevels.COMMAND_OUTPUT)

        out_thread = ReturningThread(target=pipe_monitor_thread_function,
                                     args=(process.stdout, LogLevels.COMMAND_OUTPUT))
        err_thread = ReturningThread(target=pipe_monitor_thread_function,
                                     args=(process.stderr, LogLevels.WARNING))
        out_thread.start()
        err_thread.start()
        # let the process do its job
        # ...
        # then join the threads and read the output.
        std_out_str = str(out_thread.join())
        std_err_str = str(err_thread.join())
        process.stdout.close()
        process.stderr.close()

        return_code = process.wait()
        popdir(dryrun=dryrun)
        log_progress_output("-" * 40, LogLevels.COMMAND_OUTPUT)

        if return_code != 0:
            if raise_errors:
                error(f"run_command(cmd='{cmd_str}' failed with error-code '{return_code}':\n{std_err_str}")

    return return_code, std_out_str, std_err_str


def __prepare_run(cmd, comment, cwd, dryrun):
    if isinstance(cmd, str):
        cmd = squeeze_chars(source=cmd, squeeze_set="\t\n\r ", replace_with=" ")
        cmd = cmd.split()
    cmd_copy = []
    for c in cmd:
        if c.find(" ") != -1:
            cmd_copy.append(f"\"{c}\"")
        else:
            cmd_copy.append(c)
    cmd_str = " ".join(cmd_copy)
    if cwd is None or is_empty_string(cwd):
        cwd = current_dir()
    pushdir(cwd, dryrun=dryrun)
    log_progress_output(message=cmd_str, extra_comment=comment, verbosity=LogLevels.COMMAND)
    return cmd, cmd_str, cwd


def run_interactive_command(cmd: (str | list),
                            cwd: (str | PathLike) = None,
                            comment: str = "",
                            dryrun: bool = False):
    """
    Run an interactive command in a sub-process.
    :param cmd: command to execute.
    :param cwd: the working directory to use.
    :param comment: a comment to enhance the log-output.
    :param dryrun: if set to True, then do not execute but just output a comment describing the command.
    """

    # pylint: disable=unused-variable
    cmd, cmd_str, cwd = __prepare_run(cmd, comment, cwd, dryrun)

    if not dryrun:
        old_tty = termios.tcgetattr(sys.stdin)
        tty.setraw(sys.stdin.fileno())
        master_fd, slave_fd = pty.openpty()

        try:
            # this is interactive and has no threads
            # pylint: disable=subprocess-popen-preexec-fn
            with subprocess.Popen(cmd,
                                  # cwd=cwd,
                                  preexec_fn=os.setsid,
                                  stdin=slave_fd,
                                  stdout=slave_fd,
                                  stderr=slave_fd,
                                  universal_newlines=True) as process:
                while process.poll() is None:
                    r, w, e = select.select([sys.stdin, master_fd], [], [])
                    if sys.stdin in r:
                        d = os.read(sys.stdin.fileno(), 10240)
                        os.write(master_fd, d)
                    elif master_fd in r:
                        o = os.read(master_fd, 10240)
                        if o:
                            os.write(sys.stdout.fileno(), o)
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty)

    popdir(dryrun=dryrun)
