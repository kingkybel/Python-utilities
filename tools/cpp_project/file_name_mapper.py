import os
import sys
from enum import auto
from os import PathLike

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/..")
sys.path.insert(0, dk_lib_dir)

from lib.basic_functions import valid_absolute_path
from lib.extended_enum import ExtendedEnum


class CommentStyle(ExtendedEnum):
    NONE = auto()
    CPP = auto()
    PYTHON = auto()
    JAVA = auto()
    BASH = auto()
    CMAKE = auto()
    DOCKER = auto()
    PROTO = auto()

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
        if self == CommentStyle.PROTO:
            return "////"

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
        if self == CommentStyle.PROTO:
            return "// "

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
        if self == CommentStyle.PROTO:
            return "////"


class FileNameMapper:
    def __init__(self,
                 template_file: (str | PathLike),
                 target_file: (str | PathLike),
                 comment_style: (str | CommentStyle)):
        self.__template_file = valid_absolute_path(template_file)
        self.__target_file = valid_absolute_path(target_file)
        if isinstance(comment_style, str):
            comment_style = CommentStyle.from_string(comment_style)
        self.__comment_style = comment_style
        self.__tag_replacements = dict()

    def template_file(self) -> str:
        return self.__template_file

    def target_file(self) -> str:
        return self.__target_file

    def comment_style(self) -> CommentStyle:
        return self.__comment_style
