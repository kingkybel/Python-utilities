import os
import sys
from os import PathLike

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/../../../Python-utilities")
if not os.path.isdir(dk_lib_dir):
    raise FileNotFoundError(f"Library directory '{dk_lib_dir}' cannot be found")
sys.path.insert(0, dk_lib_dir)

from lib.overrides import overrides
from tools.cpp_project.comment_style import CommentStyle
from tools.cpp_project.file_name_mapper import FileNameMapper
from tools.cpp_project.abc_file_set_creator import ABCFileSetCreator


class SimpleFileSetCreator(ABCFileSetCreator):
    """
    @brief Create files for one class
    """

    def __init__(self, project_path: (str | PathLike)):
        super().__init__(project_path)

    @overrides(ABCFileSetCreator)
    def get_file_map_list(self) -> list[FileNameMapper]:
        return [FileNameMapper(template_file=f"{self.tpl_services_dir()}/project_main.cc",
                               target_file=f"{self.services_dir()}/{self.project_name().lower()}_main.cc",
                               comment_style=CommentStyle.CPP)]

    @overrides(ABCFileSetCreator)
    def get_tag_replacements(self) -> dict[str, str]:
        return dict()
