# Repository:   https://github.com/Python-utilities
# File Name:    lib/logger.py
# Description:  logging facility
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
import datetime
import logging
import os
import os.path
import sys
from logging import LogRecord
from os import PathLike
from colorama import Fore, Style

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/../../Python-utilities")
if not os.path.isdir(dk_lib_dir):
    raise FileNotFoundError(f"Library directory '{dk_lib_dir}' cannot be found")
sys.path.insert(0, dk_lib_dir)

# pylint: disable=wrong-import-position
from lib.basic_functions import is_empty_string, now_string
from lib.extended_enum import ExtendedEnum
from lib.overrides import overrides


class LogLevels(ExtendedEnum):
    """
    Enum encapsulates the log-levels from the logging library and adds additional named log-levels.
    """
    CRITICAL = int(logging.CRITICAL)
    FATAL = int(logging.FATAL)
    ERROR = int(logging.ERROR)
    WARNING = int(logging.WARNING)
    COMMAND = int(logging.WARNING) - 2
    COMMAND_OUTPUT = int(logging.WARNING) - 4
    COMMAND_STDERR = int(logging.WARNING) - 6
    INFO = int(logging.INFO)
    DEBUG = int(logging.DEBUG)

    def __str__(self):
        return self.name.lower()

    def logging_level(self) -> int:
        """
        Gets the logging level as int.
        :return: the logging level as it
        """
        return int(self.value)


class CustomFormatter(logging.Formatter):
    """
    A formatter class to customize how log-entries should be displayed.
    """

    def __init__(self, fmt='[%(asctime]s\t[%(levelname)s] [%(threadname)s] %(messages)s'):
        logging.Formatter.__init__(self, fmt=fmt)

    @overrides(logging.Formatter)
    def format(self, record: LogRecord) -> str:
        """
        Overriding the format function in order to handle custom log-levels appropriately.
        :param record: the logging record.
        :return: the formatted record as string.
        """
        # remember the original
        format_orig = self._style._fmt

        if record.levelno == LogLevels.COMMAND:
            self._style._fmt = "\n######## execute command:\n%(messages)s\n#########################"

        if record.levelno == LogLevels.COMMAND_OUTPUT:
            self._style._fmt = "%(messages)s"

        if record.levelno == LogLevels.COMMAND_STDERR:
            self._style._fmt = "%(messages)s"

        result = logging.Formatter.format(self, record)

        self._style._fmt = format_orig

        return result

    @overrides(logging.Formatter)
    def formatTime(self, record, datefmt=None):
        """
        Higher precision timestamps.
        :param: record: the log-record to format.
        :param: datefmt:  the format string for dates and timestamps.
        :return: the formatted timestamp as string.
        """
        ct = datetime.datetime.fromtimestamp(record.created)
        if datefmt is not None:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")
            s = f"{t}.{record.msecs:.05d}"
        return s


class ScriptLogger:
    """
    A logger class that uses the LogLevels enum to format log entries for logfiles and console.
    """

    def __init__(self,
                 logfile_name: (str | PathLike) = None,
                 verbosity: (str | LogLevels) = LogLevels.INFO,
                 logfile_open_mode: str = "w",
                 encoding="utf-8"):
        self.do_file_log = False
        self.verbosity = self.set_verbosity(verbosity)

        if not is_empty_string(logfile_name):
            log_dir = os.path.dirname(logfile_name)
            if not os.path.isdir(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            with open(file=logfile_name, mode=logfile_open_mode, encoding=encoding) as log_file:
                log_file.close()
            self.do_file_log = True

            filehandler = logging.FileHandler(logfile_name, mode=logfile_open_mode)
            filehandler.setFormatter(CustomFormatter())
            logging.basicConfig(format='[%(asctime]s\t[%(levelname)s] [%(threadname)s] %(messages)s',
                                datefmt="%Y%m%d-%H:%M:%S",
                                level=self.verbosity.logging_level(),
                                handlers=[filehandler])

    def set_verbosity(self, verbosity: (str | LogLevels) = LogLevels.INFO):
        """
        Set the verbosity (log-level) of the logger.
        :param: verbosity: LogLevels - value.
        :return: None
        """
        if isinstance(verbosity, str):
            self.verbosity = LogLevels.from_string(verbosity)
        else:
            self.verbosity = verbosity
        return self.verbosity

    def get_verbosity(self):
        return self.verbosity

    def __error__(self, err_type: str, message):
        if self.do_file_log:
            logging.error("%s: %s", err_type, message)
        print(f"{Fore.RED}{err_type}{Style.RESET_ALL}: {Fore.YELLOW}{message}{Style.RESET_ALL}")

    def log_critical(self, message):
        self.__error__(err_type="CRITICAL", message=message)

    def log_fatal(self, message):
        self.__error__(err_type="FATAL", message=message)

    def log_error(self, message):
        self.__error__(err_type="ERROR", message=message)

    def log_warning(self, message):
        if self.do_file_log:
            logging.warning(message)
        if self.verbosity.logging_level() <= logging.WARNING:
            print(f"[{now_string()}] {Fore.YELLOW}WARNING{Style.RESET_ALL}: {message}")

    def log_info(self, message):
        if self.do_file_log:
            logging.info(message)
        if self.verbosity.logging_level() <= logging.INFO:
            print(f"[{now_string()}] {Fore.GREEN}INFO{Style.RESET_ALL}: {message}")

    def log_debug(self, message):
        if self.do_file_log:
            logging.debug(message)
        if self.verbosity.logging_level() <= logging.DEBUG:
            print(f"[{now_string()}] {Fore.LIGHTWHITE_EX}DEBUG{Style.RESET_ALL}: {message}")

    def log_command(self, command_str: str, extra_comment: str = None, dryrun: bool = False):
        comment = ""
        sep = ""
        if dryrun:
            comment = "not executed"
            sep = "; "
        if not is_empty_string(extra_comment):
            comment += f"{sep}{extra_comment}"
        if not is_empty_string(comment):
            comment = " ### " + comment
        if self.do_file_log:
            logging.log(level=LogLevels.COMMAND.logging_level(), msg=f"{command_str}{comment}")
        if self.verbosity.logging_level() <= LogLevels.COMMAND.value:
            spaces_len = max(100 - len(command_str) - len(comment), 1)
            spaces = " " * spaces_len
            print(f"{Fore.MAGENTA}{command_str}{Fore.LIGHTBLACK_EX}{spaces}{comment}{Style.RESET_ALL}")

    def log_command_stdout(self, command_stdout: str):
        if self.do_file_log:
            logging.log(level=LogLevels.COMMAND_OUTPUT.logging_level(),
                        msg=command_stdout)
        if self.verbosity.logging_level() <= LogLevels.COMMAND_OUTPUT.value:
            print(f"{Fore.GREEN}(stdout){Style.RESET_ALL} {Fore.LIGHTWHITE_EX}{command_stdout}{Style.RESET_ALL}")

    def log_command_stderr(self, command_stderr: str):
        if self.do_file_log:
            logging.log(level=LogLevels.COMMAND_STDERR.logging_level(),
                        msg=command_stderr)
        if self.verbosity.logging_level() <= LogLevels.COMMAND_STDERR.value:
            print(f"{Fore.RED}(stderr){Style.RESET_ALL} {Fore.LIGHTWHITE_EX}{command_stderr}{Style.RESET_ALL}")

    def log_header(self, header, filler: str = "="):
        if len(header) <= 96:
            filler_len = int((100 - len(header) - 2) / 2)
            filler = filler * filler_len
        if self.do_file_log:
            logging.info("%s %s %s", filler, header, filler)
        if self.verbosity.logging_level() <= logging.INFO:
            print(f"{Fore.YELLOW}{filler}{Style.RESET_ALL} {header} {Fore.YELLOW}{filler}{Style.RESET_ALL}")

    def log_progress_output(self,
                            message,
                            verbosity: (str | LogLevels) = LogLevels.INFO,
                            extra_comment: str = None):
        if isinstance(verbosity, str):
            verbosity = LogLevels.from_string(verbosity)
        match verbosity:
            case LogLevels.DEBUG:
                self.log_debug(message)
            case LogLevels.INFO:
                self.log_info(message)
            case LogLevels.WARNING:
                self.log_warning(message)
            case LogLevels.ERROR:
                self.log_error(message)
            case LogLevels.CRITICAL:
                self.log_critical(message)
            case LogLevels.FATAL:
                self.log_fatal(message)
            case LogLevels.COMMAND:
                self.log_command(message, extra_comment=extra_comment)
            case LogLevels.COMMAND_OUTPUT:
                self.log_command_stdout(message)
            case LogLevels.COMMAND_STDERR:
                self.log_command_stderr(message)


global_logger = ScriptLogger()


def set_logger(script_logger: ScriptLogger = None,
               logfile_name: (str | PathLike) = None,
               logfile_open_mode: str = "w",
               verbosity: (str | LogLevels) = None) -> ScriptLogger:
    global global_logger
    if not is_empty_string(logfile_name):
        global_logger = ScriptLogger(logfile_name=logfile_name,
                                     verbosity=verbosity,
                                     logfile_open_mode=logfile_open_mode)
    elif script_logger is not None:
        if verbosity is not None:
            script_logger.set_verbosity(verbosity)
        global_logger = script_logger
    else:
        global_logger = ScriptLogger(verbosity=verbosity)
    return global_logger


def get_logger() -> ScriptLogger:
    return global_logger


def fatal(message, exception=SystemExit, error_code=1):
    get_logger().log_fatal(message=message)
    raise exception(error_code)


def critical(message, exception=SystemExit, error_code=1):
    get_logger().log_critical(message=message)
    raise exception(error_code)


def error(message, exception=SystemExit, error_code=1):
    get_logger().log_error(message=message)
    raise exception(error_code)


def log_error(message: str):
    get_logger().log_error(message=message)


def log_warning(message: str):
    get_logger().log_warning(message=message)


def log_info(message: str):
    get_logger().log_info(message=message)


def log_debug(message: str):
    get_logger().log_debug(message=message)


def log_header(header: str):
    get_logger().log_header(header=header)


def log_command(message: str, extra_comment: str = None, dryrun: bool = False):
    get_logger().log_command(command_str=message, extra_comment=extra_comment, dryrun=dryrun)


def log_progress_output(message: str,
                        verbosity: (str | LogLevels) = LogLevels.INFO,
                        extra_comment: str = None):
    get_logger().log_progress_output(message=message,
                                     verbosity=verbosity,
                                     extra_comment=extra_comment)
