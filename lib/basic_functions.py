import os
import re
from datetime import datetime
from os import PathLike

LINUX_PROTECTED_DIR_PATTERNS = ["^/$", "^/bin", "^/boot", "^/dev", "^/lib",
                                "^/media", "^/proc", "^/root", "^/run",
                                "^/sbin", "^/sys", "^/usr"]


def is_empty_string(string: str = None):
    return string is None or string == ""


def now_string() -> str:
    return datetime.now(tz=None).strftime("%Y%m%d-%H:%M:%S.%f")


def now_string_short() -> str:
    return datetime.now(tz=None).strftime("%Y%m%d-%H:%M")


def now_date() -> str:
    return datetime.now(tz=None).strftime("%Y-%m-%d")


def valid_absolute_path(path: (str | PathLike),
                        protect_system_patterns: (str | list[str]) = None):
    """
    Create an absolute path from the given path.
    :param path: the original path.
    :param protect_system_patterns: a list of patterns to prevent the returned path to be a protected system-path.
                                    By default, the Unix/Linux system paths are protected.
    :return: the absolute path as string.
    """
    if protect_system_patterns is None:
        protect_system_patterns = LINUX_PROTECTED_DIR_PATTERNS
    if isinstance(path, PathLike):
        path = str(path)
    if is_empty_string(path):
        path = "."
    path = os.path.abspath(path)
    if isinstance(protect_system_patterns, str):
        protect_system_patterns = [protect_system_patterns]
    for protected in protect_system_patterns:
        if bool(re.match(pattern=protected, string=path)):
            raise SystemError(f"Path '{path}' is a protected path. Change protect_system_patterns - parameter")
    if path.find("/") and not path.startswith("/") and not path.startswith("."):
        path = f"./{path}"
    return os.path.abspath(path)
