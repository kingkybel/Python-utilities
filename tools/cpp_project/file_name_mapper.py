import os
import sys
from os import PathLike

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/..")
sys.path.insert(0, dk_lib_dir)

from tools.cpp_project.comment_style import CommentStyle
from lib.basic_functions import valid_absolute_path


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

