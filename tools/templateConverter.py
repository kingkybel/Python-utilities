#!/bin/env python3

import os
import sys
from enum import auto

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/..")
sys.path.insert(0, dk_lib_dir)

from os import PathLike
from lib.bash import run_command
from lib.basic_functions import now_date, is_empty_string, valid_absolute_path, now_year
from lib.file_system_object import mkdir, find, FileSystemObjectType, remove
from lib.file_utils import read_file, write_file, get_git_config
from lib.logger import error
from lib.extended_enum import ExtendedEnum
from lib.string_utils import is_cpp_id


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


class FileListElement:
    def __init__(self,
                 template_file: (str | PathLike),
                 target_file: (str | PathLike),
                 comment_style: CommentStyle,
                 class_name: str = None,
                 grpc_proto: str = None,
                 grpc_service: str = None,
                 grpc_request: str = None,
                 port: int = None):
        self.template_file = template_file
        self.target_file = target_file
        self.comment_style = comment_style
        self.class_name = class_name
        self.grpc_proto = grpc_proto
        self.grpc_service = grpc_service
        self.grpc_request = grpc_request
        self.port = port


class TemplatePopulator:
    git_config = get_git_config()

    def __init__(self,
                 project_path: (str | PathLike),
                 class_names: (str | list[str]) = None,
                 grpc_client_server_names: (str | list[str]) = None,
                 add_docker: bool = False):
        self.project_path = valid_absolute_path(project_path)
        self.project_name = os.path.basename(self.project_path)

        ##############################################################################
        # create basic directory structure
        self.licence_content = self.populate_licence()
        self.create_directories(self.project_path)
        write_file(filename=f"{project_path}/licence/licence", content=self.licence_content)
        self.file_list = list()
        ##############################################################################

        ##############################################################################
        # Create tags needed when there are any classes to be created
        self.class_names = list()
        if isinstance(class_names, str):
            self.class_names = {class_names}
        elif class_names is not None:
            self.class_names = set(class_names)

        # create tags for multiple project-class files
        self.project_hash_includes = ""
        self.cmake_project_lib_target = ""
        self.cmake_exe_link_libraries = ""
        self.cmake_test_exe_link_libraries = ""
        self.using_namespace = ""
        self.create_tags_for_classes()
        ##############################################################################

        ##############################################################################
        # Create tags needed for any grpc-client/servers to be created.
        self.grpc_client_server_names = dict()
        # split all <proto-name>:<service-name> strings as key/val and add to map.
        if isinstance(grpc_client_server_names, str):
            grpc_client_server_names = [grpc_client_server_names]
        if grpc_client_server_names is not None:
            for proto_service_request_str in grpc_client_server_names:
                proto_service_request = proto_service_request_str.split(":")
                if not is_empty_string(proto_service_request[0]):
                    service = proto_service_request[0]
                    request = service
                    if len(proto_service_request) > 1:
                        service = proto_service_request[1]
                        if len(proto_service_request) > 2:
                            request = proto_service_request[2]
                    self.grpc_client_server_names[proto_service_request[0]] = (service, request)
        self.java_domain = ""
        self.cmake_include_grpc = ""
        self.cmake_generate_cpp_from_proto = ""
        self.cmake_grpc_services = ""
        self.cmake_proto_grpc_cpp_sources = ""
        self.java_domain = ""
        self.create_tags_for_grpc()
        ##############################################################################

        ##############################################################################
        # docker build command to be executed, if add-docker == true
        self.add_docker = add_docker
        self.docker_build_command = ""
        if self.add_docker:
            self.docker_build_command = "docker-compose build"
            for service, request in self.grpc_client_server_names.values():
                self.docker_build_command += \
                    f"\ndocker-compose --file docker-compose.{service}.yml --env-file .{service}.env build"
        ##############################################################################

        ##############################################################################
        # create a list of all files for the project
        self.file_list = list()
        self.make_project_file_list()
        ##############################################################################

    @classmethod
    def create_directories(cls, project_path: (str | PathLike)):
        # Create the project directory and subdirectories
        remove(project_path)
        mkdir([f"{project_path}/include",
               f"{project_path}/src/proto_cpp",
               f"{project_path}/test",
               f"{project_path}/licence",
               f"{project_path}/build"], force=True, recreate=True)

    @classmethod
    def populate_licence(cls) -> str:
        licence_str = read_file(filename=f"{this_dir}/templates/licence/licence")
        licence_str = licence_str.replace("[[YEAR]]", now_year())
        licence_str = licence_str.replace("[[AUTHOR]]", cls.git_config["user.name"])
        licence_str = licence_str.replace("[[EMAIL]]", cls.git_config["user.email"])
        licence_str = licence_str.replace("[[TODAY]]", now_date())

        return licence_str

    def commented_licence_string(self, pure_text: str, comment_style: CommentStyle, filename: str) -> str:
        lic_with_comments = comment_style.start() + "\n"
        filename = filename.replace(f"{self.project_path}", self.project_name)
        lic_with_comments += comment_style.cont() + f"Filename: {filename}\n"
        lic_with_comments += comment_style.cont() + "\n"
        for line in pure_text.split("\n"):
            lic_with_comments += comment_style.cont() + line + "\n"
        lic_with_comments += comment_style.end()

        return lic_with_comments

    def create_tags_for_classes(self):
        self.cmake_exe_link_libraries = ""
        self.cmake_test_exe_link_libraries = f"target_link_libraries(run_{self.project_name.lower()}_tests " \
                                             f"gtest gtest_main)"
        if len(self.class_names) == 0:
            return

        self.project_hash_includes = ""
        self.cmake_project_lib_target = f"add_library({self.project_name.lower()} STATIC\n"
        for class_name in self.class_names:
            self.cmake_project_lib_target += f"\t{class_name.lower()}.cc\n"
            self.project_hash_includes += f'#include "{class_name.lower()}.h"\n'

        self.cmake_project_lib_target += ")"
        self.cmake_exe_link_libraries = f"target_link_libraries({self.project_name.lower()}_exe " \
                                        f"PRIVATE {self.project_name.lower()})"
        self.cmake_test_exe_link_libraries = f"target_link_libraries(run_{self.project_name.lower()}_tests " \
                                             f"PRIVATE gtest gtest_main {self.project_name.lower()})"
        self.using_namespace = f"using namespace ns_{self.project_name.lower()};"

    def create_tags_for_grpc(self):
        if len(self.grpc_client_server_names) == 0:
            return

        self.java_domain = ""

        email_dom = TemplatePopulator.git_config["user.email"].split("@")
        if len(email_dom) > 1:
            comps = email_dom[1].split(".")
            comps.reverse()
            for comp in comps:
                if is_cpp_id(comp):
                    self.java_domain += comp.lower() + "."
            if is_empty_string(self.java_domain):
                self.java_domain = "com"
        self.java_domain += self.project_name.lower()
        self.cmake_generate_cpp_from_proto = ""
        self.cmake_grpc_services = ""
        self.cmake_proto_grpc_cpp_sources = ""
        protos = ""
        for proto in self.grpc_client_server_names.keys():
            if len(self.grpc_client_server_names) > 1:
                protos += "\n\t"
            protos += proto
            service = self.grpc_client_server_names[proto][0]
            request = self.grpc_client_server_names[proto][1]
            self.cmake_grpc_services += f'\n\t{service.lower()}'
            self.cmake_proto_grpc_cpp_sources += f'\n\t${{{proto.upper()}_PROTO_CPP_SOURCE}}'
            self.cmake_proto_grpc_cpp_sources += f'\n\t${{{proto.upper()}_PROTO_CPP_HEADER}}'
            self.cmake_proto_grpc_cpp_sources += f'\n\t${{{proto.upper()}_GRPC_CPP_SOURCE}}'
            self.cmake_proto_grpc_cpp_sources += f'\n\t${{{proto.upper()}_GRPC_CPP_HEADER}}'

        self.cmake_generate_cpp_from_proto += \
            f'create_cpp_from_protos("${{CMAKE_SOURCE_DIR}}/protos" ${{PROTO_CPP_SRC_DIR}} {protos})\n'
        self.cmake_include_grpc = read_file(f"{this_dir}/templates/src/CMakeListsGrpc.txt")
        self.cmake_include_grpc = self.cmake_include_grpc.replace("[[CMAKE_GENERATE_CPP_FROM_PROTOS]]",
                                                                  self.cmake_generate_cpp_from_proto)
        self.cmake_include_grpc = self.cmake_include_grpc.replace("[[PROJECT_NAME_LOWER]]",
                                                                  self.project_name.lower())
        self.cmake_include_grpc = self.cmake_include_grpc.replace("[[CMAKE_PROTO_GRPC_CPP_SOURCES]]",
                                                                  self.cmake_proto_grpc_cpp_sources)
        self.cmake_include_grpc = self.cmake_include_grpc.replace("[[CMAKE_GRPC_SERVICES]]",
                                                                  self.cmake_grpc_services)

    def make_project_file_list(self):
        self.file_list = list()
        # add non-project-dependent files
        for tmplt in [(".vscode/c_cpp_properties.json", CommentStyle.NONE),
                      (".vscode/launch.json", CommentStyle.NONE),
                      (".vscode/settings.json", CommentStyle.NONE),
                      (".vscode/tasks.json", CommentStyle.NONE),
                      ("CMakeLists.txt", CommentStyle.CMAKE),
                      ("do_build", CommentStyle.BASH),
                      ("src/CMakeLists.txt", CommentStyle.CMAKE),
                      ("test/CMakeLists.txt", CommentStyle.CMAKE),
                      (".gitignore", CommentStyle.BASH),
                      (".clang-format", CommentStyle.BASH),
                      (".clang-tidy", CommentStyle.BASH),
                      ("Doxyfile", CommentStyle.BASH)]:
            self.file_list.append(
                FileListElement(template_file=f"{this_dir}/templates/{tmplt[0]}",
                                target_file=f"{self.project_path}/{tmplt[0]}",
                                comment_style=tmplt[1]))

        # add C++ main and test-main files
        self.file_list.append(
            FileListElement(template_file=f"{this_dir}/templates/src/project_main.cc",
                            target_file=f"{self.project_path}/src/{self.project_name.lower()}_main.cc",
                            comment_style=CommentStyle.CPP))
        self.file_list.append(
            FileListElement(template_file=f"{this_dir}/templates/test/project_tests.cc",
                            target_file=f"{self.project_path}/test/run_{self.project_name.lower()}_tests.cc",
                            comment_style=CommentStyle.CPP))

        # add classes split in header and implementation
        for class_name in self.class_names:
            if not is_cpp_id(class_name):
                error(f"Class-name {class_name} is not a valid C++ identifier")
            self.file_list.append(
                FileListElement(template_file=f"{this_dir}/templates/include/class_include.h",
                                target_file=f"{self.project_path}/include/{class_name.lower()}.h",
                                comment_style=CommentStyle.CPP,
                                class_name=class_name))
            self.file_list.append(
                FileListElement(template_file=f"{this_dir}/templates/src/class_source.cc",
                                target_file=f"{self.project_path}/src/{class_name.lower()}.cc",
                                comment_style=CommentStyle.CPP,
                                class_name=class_name))

        # add grpc-clients and -servers split in headers, implementation and main
        if len(self.grpc_client_server_names) > 0:
            self.file_list.append(
                FileListElement(template_file=f"{this_dir}/templates/src/cmake/common.cmake",
                                target_file=f"{self.project_path}/src/cmake/common.cmake",
                                comment_style=CommentStyle.CMAKE))

        # all client server pairs will use a different port
        port = 50050
        for proto in self.grpc_client_server_names.keys():
            port += 1
            service = self.grpc_client_server_names[proto][0]
            request = self.grpc_client_server_names[proto][1]
            if not is_cpp_id(service):
                error(f"Class-name {service} is not a valid C++ identifier")
            self.file_list.append(
                FileListElement(template_file=f"{this_dir}/templates/include/grpc_client.h",
                                target_file=f"{self.project_path}/include/{service.lower()}_client.h",
                                comment_style=CommentStyle.CPP,
                                class_name=f"{service}Client",
                                grpc_proto=proto,
                                grpc_service=service,
                                grpc_request=request,
                                port=port))
            self.file_list.append(
                FileListElement(template_file=f"{this_dir}/templates/include/grpc_service.h",
                                target_file=f"{self.project_path}/include/{service.lower()}_service.h",
                                comment_style=CommentStyle.CPP,
                                class_name=f"{service}Service",
                                grpc_proto=proto,
                                grpc_service=service,
                                grpc_request=request,
                                port=port))
            self.file_list.append(
                FileListElement(template_file=f"{this_dir}/templates/src/grpc_client.cc",
                                target_file=f"{self.project_path}/src/{service.lower()}_client.cc",
                                comment_style=CommentStyle.CPP,
                                class_name=f"{service}Client",
                                grpc_proto=proto,
                                grpc_service=service,
                                grpc_request=request,
                                port=port))
            self.file_list.append(
                FileListElement(template_file=f"{this_dir}/templates/src/grpc_client_main.cc",
                                target_file=f"{self.project_path}/src/{service.lower()}_client_main.cc",
                                comment_style=CommentStyle.CPP,
                                grpc_proto=proto,
                                grpc_service=service,
                                grpc_request=request,
                                port=port))
            self.file_list.append(
                FileListElement(template_file=f"{this_dir}/templates/src/grpc_service.cc",
                                target_file=f"{self.project_path}/src/{service.lower()}_service.cc",
                                comment_style=CommentStyle.CPP,
                                class_name=f"{service}Service",
                                grpc_proto=proto,
                                grpc_service=service,
                                grpc_request=request,
                                port=port))
            self.file_list.append(
                FileListElement(template_file=f"{this_dir}/templates/src/grpc_server_main.cc",
                                target_file=f"{self.project_path}/src/{service.lower()}_server_main.cc",
                                comment_style=CommentStyle.CPP,
                                grpc_proto=proto,
                                grpc_service=service,
                                grpc_request=request,
                                port=port))
            self.file_list.append(
                FileListElement(template_file=f"{this_dir}/templates/protos/simple_connect.proto",
                                target_file=f"{self.project_path}/protos/{proto.lower()}.proto",
                                comment_style=CommentStyle.PROTO,
                                grpc_proto=proto,
                                grpc_service=service,
                                grpc_request=request))
            if self.add_docker:
                for tmplt in [("Dockerfile.server", CommentStyle.DOCKER),
                              ("Dockerfile.client", CommentStyle.DOCKER),
                              ("docker-compose.client-server.yml", CommentStyle.DOCKER),
                              (".client-server.env", CommentStyle.DOCKER)]:
                    target_name = tmplt[0]
                    target_name = target_name.replace(".client-server.", f".{service}.")
                    target_name = target_name.replace(".server", f".{service}_server")
                    target_name = target_name.replace(".client", f".{service}_client")
                    self.file_list.append(
                        FileListElement(template_file=f"{this_dir}/templates/{tmplt[0]}",
                                        target_file=f"{self.project_path}/{target_name}",
                                        comment_style=tmplt[1],
                                        grpc_proto=proto,
                                        grpc_service=service,
                                        port=port))

        # if we want dockerisation then add docker-files
        if self.add_docker:
            for tmplt in [("Dockerfile", CommentStyle.DOCKER),
                          ("docker-compose.yml", CommentStyle.DOCKER),
                          (".env", CommentStyle.DOCKER),
                          ("bash_aliases_for_docker", CommentStyle.BASH)]:
                self.file_list.append(
                    FileListElement(template_file=f"{this_dir}/templates/{tmplt[0]}",
                                    target_file=f"{self.project_path}/{tmplt[0]}",
                                    comment_style=tmplt[1]))

    def replace_templates(self, file_list_element: FileListElement) -> str:
        tmplt_text = read_file(file_list_element.template_file)
        comment_style = file_list_element.comment_style
        filename_for_licence_header = file_list_element.target_file
        licence_str = self.commented_licence_string(self.licence_content, comment_style, filename_for_licence_header)

        class_name = ""
        if file_list_element.class_name is not None:
            class_name = file_list_element.class_name

        grpc_proto = ""
        if file_list_element.grpc_proto is not None:
            grpc_proto = file_list_element.grpc_proto

        port = ""
        if file_list_element.port is not None:
            port = str(file_list_element.port)

        grpc_service = ""
        if file_list_element.grpc_service is not None:
            grpc_service = str(file_list_element.grpc_service)

        grpc_request = ""
        if file_list_element.grpc_request is not None:
            grpc_request = str(file_list_element.grpc_request)

        tmplt_text = tmplt_text.replace("[[FILENAME]]", filename_for_licence_header)
        tmplt_text = tmplt_text.replace("[[CLASS_NAME]]", class_name)
        tmplt_text = tmplt_text.replace("[[CLASS_NAME_UPPER]]", class_name.upper())
        tmplt_text = tmplt_text.replace("[[CLASS_NAME_LOWER]]", class_name.lower())
        tmplt_text = tmplt_text.replace("[[LICENCE]]", licence_str)
        tmplt_text = tmplt_text.replace("[[PROJECT_NAME]]", self.project_name)
        tmplt_text = tmplt_text.replace("[[PROJECT_NAME_UPPER]]", self.project_name.upper())
        tmplt_text = tmplt_text.replace("[[PROJECT_NAME_LOWER]]", self.project_name.lower())
        tmplt_text = tmplt_text.replace("[[CLASS_INCLUDES]]", self.project_hash_includes)
        tmplt_text = tmplt_text.replace("[[PROJECT_LIB_TARGET]]", self.cmake_project_lib_target)
        tmplt_text = tmplt_text.replace("[[EXE_LINK_LIBRARIES]]", self.cmake_exe_link_libraries)
        tmplt_text = tmplt_text.replace("[[TEST_EXE_LINK_LIBRARIES]]", self.cmake_test_exe_link_libraries)
        tmplt_text = tmplt_text.replace("[[DOCKER_BUILD_COMMAND]]", self.docker_build_command)
        tmplt_text = tmplt_text.replace("[[USING_NAMESPACE]]", self.using_namespace)
        tmplt_text = tmplt_text.replace("[[PROTO_NAME]]", grpc_proto)
        tmplt_text = tmplt_text.replace("[[PROTO_NAME_LOWER]]", grpc_proto.lower())
        tmplt_text = tmplt_text.replace("[[PROTO_NAME_UPPER]]", grpc_proto.upper())
        tmplt_text = tmplt_text.replace("[[SERVICE_NAME]]", grpc_service)
        tmplt_text = tmplt_text.replace("[[SERVICE_NAME_LOWER]]", grpc_service.lower())
        tmplt_text = tmplt_text.replace("[[SERVICE_NAME_UPPER]]", grpc_service.upper())
        tmplt_text = tmplt_text.replace("[[REQUEST]]", grpc_request)
        tmplt_text = tmplt_text.replace("[[JAVA_DOMAIN]]", self.java_domain)
        tmplt_text = tmplt_text.replace("[[PORT]]", str(port))
        tmplt_text = tmplt_text.replace("[[CMAKE_INCLUDE_GRPC]]", self.cmake_include_grpc)
        # tmplt_text = tmplt_text.replace("[[CMAKE_GENERATE_CPP_FROM_PROTOS]]", self.cmake_generate_cpp_from_proto)
        # tmplt_text = tmplt_text.replace("[[CMAKE_GRPC_SERVICES]]", self.cmake_grpc_services)
        # tmplt_text = tmplt_text.replace("[[CMAKE_PROTO_GRPC_CPP_SOURCES]]", self.cmake_proto_grpc_cpp_sources)

        return tmplt_text

    def write_project_files(self):
        for file_list_element in self.file_list:
            content = self.replace_templates(file_list_element=file_list_element)
            write_file(filename=file_list_element.target_file, content=content)

    def add_git(self):
        run_command(cmd="git init", cwd=self.project_path)
        files_to_add_to_git = find(paths=self.project_path, file_type_filter=FileSystemObjectType.FILE)
        for file in files_to_add_to_git:
            run_command(cmd=f"git add {file}", cwd=self.project_path)
        run_command(cmd=["git", "commit", "-m", "initial checkin"], cwd=self.project_path)

    def create_cmake_project(self):
        self.write_project_files()
        os.chmod(f"{self.project_path}/do_build", 0o776)
        self.add_git()
        run_command(f"{self.project_path}/do_build", cwd=self.project_path)
