import os
import sys
from os import PathLike

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/../../../Python-utilities")
if not os.path.isdir(dk_lib_dir):
    raise FileNotFoundError(f"Library directory '{dk_lib_dir}' cannot be found")
sys.path.insert(0, dk_lib_dir)

from lib.file_system_object import remove, mkdir
from lib.file_utils import write_file
from lib.overrides import overrides
from tools.cpp_project.abc_file_set_creator import ABCFileSetCreator
from tools.cpp_project.file_name_mapper import FileNameMapper
from tools.cpp_project.comment_style import CommentStyle


class BasicFileSetCreator(ABCFileSetCreator):
    """
    @brief base class for creating *one* set of files for a feature of a project.
    """

    def __init__(self, project_path: (str | PathLike), add_docker: bool):
        super().__init__(project_path)
        self.__add_docker = add_docker
        self.__create_basic_dir_structure()

    def __create_basic_dir_structure(self):
        # Create the project directory and subdirectories
        if not ABCFileSetCreator.is_basic_structure_created:
            remove(self.project_path())
            mkdir([f"{self.include_dir()}",
                   f"{self.src_dir()}",
                   f"{self.services_dir()}",
                   f"{self.test_dir()}",
                   f"{self.licence_dir()}",
                   f"{self.build_dir()}",
                   f"{self.vscode_dir()}"], force=True, recreate=True)
            write_file(f"{self.project_path()}/licence/licence", self.licence())
            ABCFileSetCreator.is_basic_structure_created = True
            self.write_project_files()

    @overrides(ABCFileSetCreator)
    def get_file_map_list(self) -> list[FileNameMapper]:
        file_list = list()
        ######################################
        # add common project files.
        for tmplt in [(".vscode/c_cpp_properties.json", CommentStyle.NONE),
                      (".vscode/launch.json", CommentStyle.NONE),
                      (".vscode/settings.json", CommentStyle.NONE),
                      (".vscode/tasks.json", CommentStyle.NONE),
                      (".gitignore", CommentStyle.BASH),
                      (".clang-format", CommentStyle.BASH),
                      (".clang-tidy", CommentStyle.BASH),
                      ("Doxyfile", CommentStyle.BASH)]:

            file_list.append(
                FileNameMapper(template_file=f"{self.tpl_dir()}/{tmplt[0]}",
                               target_file=f"{self.project_path()}/{tmplt[0]}",
                               comment_style=tmplt[1]))
        if self.__add_docker:
            file_list.append(
                FileNameMapper(template_file=f"{self.tpl_dir()}/bash_aliases_for_docker",
                               target_file=f"{self.project_path()}/bash_aliases_for_docker",
                               comment_style=tmplt[1]))

            return file_list

    @overrides(ABCFileSetCreator)
    def get_tag_replacements(self) -> dict[str, str]:
        return dict()
