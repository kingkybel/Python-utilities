import os
import sys
from os import PathLike

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/../../../Python-utilities")
if not os.path.isdir(dk_lib_dir):
    raise FileNotFoundError(f"Library directory '{dk_lib_dir}' cannot be found")
sys.path.insert(0, dk_lib_dir)

from lib.logger import error
from lib.string_utils import is_cpp_id
from lib.basic_functions import is_empty_string
from lib.overrides import overrides
from tools.cpp_project.file_name_mapper import FileNameMapper, CommentStyle
from tools.cpp_project.abc_file_set_creator import ABCFileSetCreator


class TemplateFileSetCreator(ABCFileSetCreator):
    """
    @brief Create files for one class
    """

    def __init__(self, project_path: (str | PathLike), template_config_str: str):
        super().__init__(project_path)
        if is_empty_string(template_config_str):
            error(f"Configuration for template is empty")
        name_and_type = template_config_str.split(":")
        if len(name_and_type) < 2:
            error(f"Invalid template config str '{template_config_str}. Needs at least one type.")
        if not is_cpp_id(name_and_type[0]):
            error(f"Template name '{name_and_type[0]}' is not a valid C++ identifier")
        typenames = name_and_type[1].split(",")
        for typename in typenames:
            if not is_cpp_id(typename):
                error(f"Type '{typename}' is not a valid C++ identifier")
        self.__template_name = name_and_type[0]
        self.__typenames = typenames
        self.__concrete_types_to_rotate = [("std::size_t", "4711UL"),
                                           ("double", "3.1415"),
                                           ("std::int32_t", "666"),
                                           ("char", "'c'"),
                                           ("float", "-112.233")]

    @overrides(ABCFileSetCreator)
    def get_tag_replacements(self) -> dict[str, str]:
        return {
            "[[TEMPLATE_CLASS_NAME]]": self.__template_name,
            "[[TEMPLATE_CLASS_NAME_LOWER]]": self.__template_name.lower(),
            "[[TEMPLATE_CLASS_NAME_UPPER]]": self.__template_name.upper(),
            "[[TEMPLATE_ARGS_DEF]]": self.__make_template_args_def(),
            "[[TEMPLATE_ARGS_HASH_DEFINES]]": self.__make_template_args_hash_defines(),
            "[[TEMPLATE_ARGS_MEMBERS]]": self.__make_template_args_members(),
            "[[TEMPLATE_CLASS_CONSTRUCTOR_ARGS]]": self.__make_template_class_constructor_args(),
            "[[TEMPLATE_CLASS_CONSTRUCTOR_INIT]]": self.__make_template_class_constructor_init(),
            "[[TEMPLATE_INCLUDES]]": f'#include "{self.__template_name.lower()}.h"',
            "[[TEMPLATE_ARGS_VARIABLES]]": self.__make_template_args_variables(concrete=False),
            "[[TEMPLATE_SPECIALISATION]]": self.__make_template_specialisation(concrete=False),
            "[[TEMPLATE_VARIABLES_IN_CALL]]": self.__make_template_variables_in_call(),
            "[[TEMPLATE_ARGS_VARIABLES_CONCRETE]]": self.__make_template_args_variables(concrete=True),
            "[[TEMPLATE_SPECIALISATION_CONCRETE]]": self.__make_template_specialisation(concrete=True),
        }

    @overrides(ABCFileSetCreator)
    def get_file_map_list(self) -> list[FileNameMapper]:
        return [FileNameMapper(template_file=f"{self.tpl_include_dir()}/template.h",
                               target_file=f"{self.include_dir()}/{self.__template_name.lower()}.h",
                               comment_style=CommentStyle.CPP),
                FileNameMapper(template_file=f"{self.tpl_test_dir()}/template_tests.cc",
                               target_file=f"{self.test_dir()}/{self.__template_name.lower()}_tests.cc",
                               comment_style=CommentStyle.CPP),
                FileNameMapper(template_file=f"{self.tpl_test_dir()}/run_tests.cc",
                               target_file=f"{self.test_dir()}/run_{self.project_name().lower()}_tests.cc",
                               comment_style=CommentStyle.CPP)]

    def template_name(self):
        return self.__template_name

    def __make_template_args_def(self) -> str:
        template_args = ""
        num_types = len(self.__typenames)
        for i in range(num_types):
            type_str = self.__typenames[i]
            if len(self.__typenames) > 1 and i > 0:
                template_args += "\n         "
            template_args += f"typename {type_str}"
            if i < num_types - 1:
                template_args += ","
        return template_args

    def __make_template_args_hash_defines(self) -> str:
        hash_defines = ""
        num_types = len(self.__typenames)
        for i in range(num_types):
            tmpl_type = self.__concrete_types_to_rotate[i % len(self.__concrete_types_to_rotate)]
            type_str = self.__typenames[i]
            hash_defines += f"typedef {tmpl_type[0]} {type_str};\n"
        return hash_defines

    def __make_template_class_constructor_args(self) -> str:
        constructor_args = ""
        indent_len = len(self.template_name()) + 5
        indent = " " * indent_len
        num_types = len(self.__typenames)
        for i in range(num_types):
            type_str = self.__typenames[i]
            if len(self.__typenames) > 1 and i > 0:
                constructor_args += "\n" + indent
            constructor_args += f"{type_str} {type_str.lower()}_val"
            if i < num_types - 1:
                constructor_args += ","

        return constructor_args

    def __make_template_class_constructor_init(self) -> str:
        constructor_init = ""

        num_types = len(self.__typenames)
        for i in range(num_types):
            type_str = self.__typenames[i]
            if len(self.__typenames) > 1:
                constructor_init += "\n        "
            if i == 0:
                constructor_init += ": "
            else:
                constructor_init += ", "
            constructor_init += f"{type_str.lower()}_val_({type_str.lower()}_val)"

        return constructor_init

    def __make_template_args_members(self) -> str:
        members = ""
        num_types = len(self.__typenames)
        for i in range(num_types):
            type_str = self.__typenames[i]
            members += f"    {type_str} {type_str.lower()}_val_;\n"

        return members

    def __make_template_args_variables(self, concrete: bool) -> str:
        variable_definitions = ""
        num_types = len(self.__typenames)
        for i in range(num_types):
            concrete_type = self.__concrete_types_to_rotate[i % len(self.__concrete_types_to_rotate)]
            var_name = f"{self.__typenames[i].lower()}_var"
            if concrete:
                type_str = concrete_type[0]
            else:
                type_str = self.__typenames[i]
            variable_definitions += f"    {type_str} {var_name}{{{concrete_type[1]}}};\n"

        return variable_definitions

    def __make_template_specialisation(self, concrete: bool) -> str:
        template_args = ""
        num_types = len(self.__typenames)
        for i in range(num_types):
            if concrete:
                concrete_type = self.__concrete_types_to_rotate[i % len(self.__concrete_types_to_rotate)]
                type_str = concrete_type[0]
            else:
                type_str = self.__typenames[i]
            template_args += type_str
            if i < num_types - 1:
                template_args += ", "
        return template_args

    def __make_template_variables_in_call(self) -> str:
        variable_definitions = ""
        num_types = len(self.__typenames)
        for i in range(num_types):
            tmpl_type = self.__concrete_types_to_rotate[i % len(self.__concrete_types_to_rotate)]
            variable_definitions += f"{self.__typenames[i].lower()}_var"
            if i < num_types - 1:
                variable_definitions += ", "

        return variable_definitions
