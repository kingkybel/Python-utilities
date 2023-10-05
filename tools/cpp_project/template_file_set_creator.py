import os
import sys
from os import PathLike

from lib.overrides import overrides

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/../../../Python-utilities")
if not os.path.isdir(dk_lib_dir):
    raise FileNotFoundError(f"Library directory '{dk_lib_dir}' cannot be found")
sys.path.insert(0, dk_lib_dir)

from lib.logger import error
from lib.string_utils import is_cpp_id
from tools.cpp_project.comment_style import CommentStyle
from tools.cpp_project.file_name_mapper import FileNameMapper
from tools.cpp_project.abc_file_set_creator import ABCFileSetCreator


class TemplateFileSetCreator(ABCFileSetCreator):
    """
    @brief Create files for one class
    """

    def __init__(self, project_path: (str | PathLike), template_config_str: str):
        super().__init__(project_path)

    @overrides(ABCFileSetCreator)
    def get_tag_replacements(self) -> dict[str, str]:
        return {
            "[[CLASS_NAME]]": self.__class_name,
            "[[CLASS_NAME_LOWER]]": self.__class_name.lower(),
            "[[CLASS_NAME_UPPER]]": self.__class_name.upper(),
            "[[CLASS_HASH_INCLUDE]]": f'#include "{self.__class_name.lower()}.h"\n'}

    @overrides(ABCFileSetCreator)
    def get_file_map_list(self) -> list[FileNameMapper]:
        return [FileNameMapper(template_file=f"{self.tpl_include_dir()}/class_include.h",
                               target_file=f"{self.include_dir()}/{self.__class_name.lower()}.h",
                               comment_style=CommentStyle.CPP),
                FileNameMapper(template_file=f"{self.tpl_classes_dir()}/class_source.cc",
                               target_file=f"{self.classes_dir()}/{self.__class_name.lower()}.cc",
                               comment_style=CommentStyle.CPP),
                FileNameMapper(template_file=f"{self.tpl_test_dir()}/class_tests.cc",
                               target_file=f"{self.test_dir()}/{self.__class_name.lower()}_tests.cc",
                               comment_style=CommentStyle.CPP),
                FileNameMapper(template_file=f"{self.tpl_test_dir()}/run_tests.cc",
                               target_file=f"{self.test_dir()}/run_{self.project_name().lower()}_tests.cc",
                               comment_style=CommentStyle.CPP)]
