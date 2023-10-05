import os
import sys
from os import PathLike

from lib.basic_functions import is_empty_string

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/../../../Python-utilities")
if not os.path.isdir(dk_lib_dir):
    raise FileNotFoundError(f"Library directory '{dk_lib_dir}' cannot be found")
sys.path.insert(0, dk_lib_dir)

from lib.file_utils import read_file
from lib.overrides import overrides
from tools.cpp_project.grpc_file_set_creator import GrpcFileSetCreator
from tools.cpp_project.comment_style import CommentStyle
from tools.cpp_project.file_name_mapper import FileNameMapper
from tools.cpp_project.abc_file_set_creator import ABCFileSetCreator


class CmakeFileSetCreator(ABCFileSetCreator):
    """
    @brief Create files for all the cmake files necessary for the project.
           This needs to be run last, as it might need tags from classes, gRPC, ...
    """

    def __init__(self,
                 project_path: (str | PathLike),
                 class_names: (str | list[str]),
                 grpc_service_config_strings: (str | list[str]),
                 templates: (str | list[str]),
                 add_docker: bool
                 ):
        super().__init__(project_path)
        if class_names is None:
            class_names = list()
        self.__class_names = class_names
        if grpc_service_config_strings is None:
            grpc_service_config_strings = list()
        self.__grpc_service_config_strings = grpc_service_config_strings
        if templates is None:
            templates = list()
        self.__templates = templates
        self.__add_docker = add_docker

    @overrides(ABCFileSetCreator)
    def get_file_map_list(self) -> list[FileNameMapper]:
        file_list = list()
        file_list.append(
            FileNameMapper(template_file=f"{self.tpl_dir()}/do_build",
                           target_file=f"{self.project_dir()}/do_build",
                           comment_style=CommentStyle.BASH))
        file_list.append(
            FileNameMapper(template_file=f"{self.tpl_dir()}/CMakeLists.txt",
                           target_file=f"{self.project_dir()}/CMakeLists.txt",
                           comment_style=CommentStyle.DOCKER))
        file_list.append(
            FileNameMapper(template_file=f"{self.tpl_src_dir()}/CMakeLists.txt",
                           target_file=f"{self.src_dir()}/CMakeLists.txt",
                           comment_style=CommentStyle.DOCKER))
        file_list.append(
            FileNameMapper(template_file=f"{self.tpl_test_dir()}/CMakeLists.txt",
                           target_file=f"{self.test_dir()}/CMakeLists.txt",
                           comment_style=CommentStyle.DOCKER))
        file_list.append(
            FileNameMapper(template_file=f"{self.tpl_services_dir()}/CMakeLists.txt",
                           target_file=f"{self.services_dir()}/CMakeLists.txt",
                           comment_style=CommentStyle.DOCKER))
        if len(self.__class_names) > 0:
            file_list.append(
                FileNameMapper(template_file=f"{self.tpl_classes_dir()}/CMakeLists.txt",
                               target_file=f"{self.classes_dir()}/CMakeLists.txt",
                               comment_style=CommentStyle.DOCKER))
        if len(self.__grpc_service_config_strings) > 0:
            file_list.append(
                FileNameMapper(template_file=f"{self.tpl_grpc_dir()}/CMakeLists.txt",
                               target_file=f"{self.grpc_dir()}/CMakeLists.txt",
                               comment_style=CommentStyle.DOCKER))
            file_list.append(
                FileNameMapper(template_file=f"{self.tpl_grpc_dir()}/cmake/common.cmake",
                               target_file=f"{self.grpc_dir()}/cmake/common.cmake",
                               comment_style=CommentStyle.DOCKER))
        return file_list

    @overrides(ABCFileSetCreator)
    def get_tag_replacements(self) -> dict[str, str]:
        tag_dict = dict()
        tag_dict["[[CMAKE_INCLUDE_CLASSES_SUB_DIR]]"] = ""
        tag_dict["[[CMAKE_CLASS_LIB_TARGETS]]"] = ""
        tag_dict["[[CMAKE_INCLUDE_GRPC_SUB_DIR]]"] = ""
        tag_dict["[[CMAKE_INCLUDE_SERVICES_SUB_DIR]]"] = "add_subdirectory(services)"
        tag_dict["[[CMAKE_SERVICES_PROJECT_PART]]"] = ""
        tag_dict["[[CMAKE_SERVICES_GRPC_PART]]"] = ""
        tag_dict["[[CMAKE_GRPC_SERVICES]]"] = ""
        tag_dict["[[TEST_EXE_LINK_LIBRARIES]]"] = self.__make_test_link_libraries()
        tag_dict["[[TEST_SOURCE_FILES]]"] = self.__make_test_source_files()
        tag_dict["[[CMAKE_TEST_INCLUDE_DIRS]]"] = ""
        tag_dict["[[CMAKE_TEST_EXE_LINK_LIBRARIES]]"] = self.__make_cmake_test_exe_link_libraries()
        tag_dict["[[DOCKER_BUILD_COMMAND]]"] = self.__make_docker_build_command()
        tag_dict["[[CMAKE_GRPC_COMMON_DEFS]]"] = ""
        tag_dict["[[CMAKE_GRPC_COMMON_LIBS]]"] = ""

        if len(self.__class_names) > 0:
            tag_dict["[[CMAKE_INCLUDE_CLASSES_SUB_DIR]]"] = "add_subdirectory(classes)"
            tag_dict["[[CMAKE_CLASS_LIB_TARGETS]]"] = self.__make_class_lib_targets()

        if len(self.__grpc_service_config_strings) > 0:
            tag_dict["[[CMAKE_INCLUDE_GRPC_SUB_DIR]]"] = "add_subdirectory(grpc)"
            tag_dict["[[CMAKE_GENERATE_CPP_FROM_PROTOS]]"] = self.__make_generate_from_proto()
            tag_dict["[[CMAKE_SERVICES_GRPC_PART]]"] = self.__make_services_grpc_part()
            tag_dict["[[CMAKE_GRPC_SERVICES]]"] = self.__make_cmake_grpc_services()
            tag_dict["[[CMAKE_TEST_INCLUDE_DIRS]]"] = \
                f'target_include_directories("run_{self.project_name().lower()}_tests" PRIVATE ${{PROTO_CPP_SRC_DIR}})'
            tag_dict["[[CMAKE_GRPC_COMMON_DEFS]]"] = "set(PROTO_CPP_SRC_DIR ${CMAKE_SOURCE_DIR}/src/proto_cpp)\n"\
                                                     "include(${CMAKE_SOURCE_DIR}/src/grpc/cmake/common.cmake)"
            tag_dict["[[CMAKE_GRPC_COMMON_LIBS]]"] = "  absl::flags\n"\
                                                     "  absl::flags_parse\n"\
                                                     "  ${_REFLECTION}\n"\
                                                     "  ${_GRPC_GRPCPP}\n"\
                                                     "  ${_PROTOBUF_LIBPROTOBUF}"

        if len(self.__class_names) == 0 and len(self.__grpc_service_config_strings) == 0:
            tag_dict["[[CMAKE_SERVICES_PROJECT_PART]]"] = read_file(f"{self.tpl_services_dir()}/CMake_project.part")

        return tag_dict

    def __make_class_lib_targets(self) -> str:
        class_targets = ""
        for target in self.__class_names:
            if len(self.__class_names) > 1:
                class_targets += "\n  "
            class_targets += target.lower()

        return class_targets

    def __make_generate_from_proto(self) -> str:
        protos = ""
        for grpc_service_config_string in self.__grpc_service_config_strings:
            grpc_config = GrpcFileSetCreator(project_path=self.project_path(),
                                             proto_service_request_str=grpc_service_config_string,
                                             port=-1)
            if len(self.__grpc_service_config_strings) > 1:
                protos += "\n                       "
            protos += grpc_config.proto()

        return f'create_cpp_from_protos("${{CMAKE_SOURCE_DIR}}/protos" ${{PROTO_CPP_SRC_DIR}} {protos})\n'

    def __make_services_grpc_part(self) -> str:
        grpc_part = read_file(f"{self.tpl_services_dir()}/CMake_grpc.part")
        services_str = ""
        for grpc_service_config_string in self.__grpc_service_config_strings:
            grpc_config = GrpcFileSetCreator(project_path=self.project_path(),
                                             proto_service_request_str=grpc_service_config_string,
                                             port=-1)
            if len(self.__grpc_service_config_strings) > 1:
                services_str += "\n        "
            services_str += grpc_config.service_with_type().lower()
        grpc_part = grpc_part.replace("[[CMAKE_GRPC_SERVICES]]", services_str)
        return grpc_part

    def __make_test_link_libraries(self) -> str:
        libs = ""
        multiline = len(self.__class_names) + len(self.__grpc_service_config_strings) > 1
        for cls in self.__class_names:
            if multiline:
                libs += "\n  "
            libs += cls.lower()
        for grpc_service_config_string in self.__grpc_service_config_strings:
            grpc_config = GrpcFileSetCreator(project_path=self.project_path(),
                                             proto_service_request_str=grpc_service_config_string,
                                             port=-1)
            if multiline:
                libs += "\n  "
            libs += grpc_config.service_with_type().lower()

        return libs

    def __make_test_source_files(self) -> str:
        test_sources = ""
        multiline = len(self.__class_names) + len(self.__grpc_service_config_strings) > 1
        for cls in self.__class_names:
            if multiline:
                test_sources += "\n               "
            test_sources += f"{cls.lower()}_tests.cc"
        for grpc_service_config_string in self.__grpc_service_config_strings:
            grpc_config = GrpcFileSetCreator(project_path=self.project_path(),
                                             proto_service_request_str=grpc_service_config_string,
                                             port=-1)
            if multiline:
                test_sources += "\n               "
            test_sources += f"{grpc_config.service_with_type().lower()}_client_tests.cc"
            if multiline:
                test_sources += "\n               "
            test_sources += f"{grpc_config.service_with_type().lower()}_service_tests.cc"
        if is_empty_string(test_sources):
            if multiline:
                test_sources += "\n               "
            test_sources = f"{self.project_name().lower()}_tests.cc"
        return test_sources

    def __make_cmake_test_exe_link_libraries(self) -> str:
        link_libs = ""

        multiline = len(self.__class_names) + len(self.__grpc_service_config_strings) > 1
        for cls in self.__class_names:
            if multiline:
                link_libs += "\n                      "
            link_libs += cls.lower()
        for grpc_service_config_string in self.__grpc_service_config_strings:
            grpc_config = GrpcFileSetCreator(project_path=self.project_path(),
                                             proto_service_request_str=grpc_service_config_string,
                                             port=-1)
            if multiline:
                link_libs += "\n                      "
            link_libs += f"{grpc_config.service_with_type().lower()}_client"
            if multiline:
                link_libs += "\n                      "
            link_libs += f"{grpc_config.service_with_type().lower()}_service"
        if not is_empty_string(link_libs):
            link_libs = \
                f"target_link_libraries(run_{self.project_name().lower()}_tests PRIVATE gtest gtest_main {link_libs})"
        return link_libs

    def __make_docker_build_command(self) -> str:
        docker_cmds = ""
        if self.__add_docker:
            for grpc_service_config_string in self.__grpc_service_config_strings:
                grpc_config = GrpcFileSetCreator(project_path=self.project_path(),
                                                 proto_service_request_str=grpc_service_config_string,
                                                 port=-1)
                docker_cmds += f"docker-compose "\
                               f"--file docker-compose.{grpc_config.service().lower()}.yml "\
                               f"--env-file .{grpc_config.service().lower()}.env "\
                               f"build\n"

            if is_empty_string(docker_cmds):
                docker_cmds += f"docker-compose build\n"

        return docker_cmds

    def __make_cmake_grpc_services(self) -> str:
        grpc_services = ""
        for grpc_service_config_string in self.__grpc_service_config_strings:
            grpc_config = GrpcFileSetCreator(project_path=self.project_path(),
                                             proto_service_request_str=grpc_service_config_string,
                                             port=-1)
            if len(self.__grpc_service_config_strings) > 1:
                grpc_services += "\n        "
            grpc_services += grpc_config.service_with_type().lower()
        return grpc_services

