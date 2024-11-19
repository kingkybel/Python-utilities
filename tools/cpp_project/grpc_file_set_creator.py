# Repository:   https://github.com/Python-utilities
# File Name:    tools/cpp_project/grpc_file_set_creator.py
# Description:  creator for a set of gRPC files
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
import os
import sys
from os import PathLike

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/../../../Python-utilities")
if not os.path.isdir(dk_lib_dir):
    raise FileNotFoundError(f"Library directory '{dk_lib_dir}' cannot be found")
sys.path.insert(0, dk_lib_dir)

# pylint: disable=wrong-import-position
from tools.cpp_project.abc_file_set_creator import ABCFileSetCreator
from tools.cpp_project.grpc_messaging_type import GrpcMessagingType
from tools.cpp_project.file_name_mapper import FileNameMapper, CommentStyle
from lib.basic_functions import is_empty_string
from lib.exceptions import ExtendedEnumError
from lib.logger import error, log_warning
from lib.overrides import overrides
from lib.string_utils import is_cpp_id


class GrpcFileSetCreator(ABCFileSetCreator):

    def __init__(self, project_path: (str | PathLike),
                 proto_service_request_str: str,
                 port: int,
                 add_docker: bool = False):
        super().__init__(project_path)
        if is_empty_string(proto_service_request_str):
            error("Illegal (empty) gRPC string - don't now what to do.")
        self.__port = port
        self.__add_docker = add_docker
        self.__proto = ""
        self.__service = ""
        self.__request = ""
        self.__messaging_type = GrpcMessagingType.DEFAULT

        proto_service_request = proto_service_request_str.split(":")
        if len(proto_service_request) < 2:
            error(f"{proto_service_request_str} must at least have two fields: "
                  "<msging_type-type>:<service-name>")
        if not is_empty_string(proto_service_request[0]):
            try:
                self.__messaging_type = GrpcMessagingType.from_string(proto_service_request[0])
            except ExtendedEnumError:
                self.__messaging_type = GrpcMessagingType.DEFAULT
                log_warning(f"Cannot convert {proto_service_request[0]} to GrpcConnectivity. "
                            f"'{proto_service_request_str}' might be ill-formed")

        if not is_empty_string(proto_service_request[1]):
            self.__proto = proto_service_request[1]
            self.__service = self.__proto
            if len(proto_service_request) > 2:
                self.__service = proto_service_request[2]
                self.__request = self.__service
                if len(proto_service_request) > 3:
                    self.__request = proto_service_request[3]
        self.__tag_dict = self.get_tag_replacements()

    @overrides(ABCFileSetCreator)
    def get_file_map_list(self) -> list[FileNameMapper]:
        file_list = []
        service = self.service()
        # request = self.request()
        conn_type_str = self.msging_type()
        if not is_empty_string(conn_type_str):
            conn_type_str += "_"
        if not is_cpp_id(service):
            error(f"Service-name '{service}' is not a valid C++ identifier")
        # CLIENT header and implementation
        file_list.append(FileNameMapper(
            template_file=f"{self.tpl_include_dir()}/{self.tpl_client_h()}",
            target_file=f"{self.include_dir()}/{self.client_h()}",
            comment_style=CommentStyle.CPP))
        file_list.append(FileNameMapper(
            template_file=f"{self.tpl_grpc_dir()}/{self.tpl_client_cc()}",
            target_file=f"{self.grpc_dir()}/{self.client_cc()}",
            comment_style=CommentStyle.CPP))

        # SERVICE header and implementation
        file_list.append(FileNameMapper(
            template_file=f"{self.tpl_include_dir()}/{self.tpl_service_h()}",
            target_file=f"{self.include_dir()}/{self.service_h()}",
            comment_style=CommentStyle.CPP))
        file_list.append(FileNameMapper(
            template_file=f"{self.tpl_grpc_dir()}/{self.tpl_service_cc()}",
            target_file=f"{self.grpc_dir()}/{self.service_cc()}",
            comment_style=CommentStyle.CPP))

        # CLIENT main-file
        file_list.append(FileNameMapper(
            template_file=f"{self.tpl_services_dir()}/{self.tpl_client_main_cc()}",
            target_file=f"{self.services_dir()}/{self.client_main_cc()}",
            comment_style=CommentStyle.CPP))

        # SERVER main-file
        file_list.append(FileNameMapper(
            template_file=f"{self.tpl_services_dir()}/{self.tpl_server_main_cc()}",
            target_file=f"{self.services_dir()}/{self.server_main_cc()}",
            comment_style=CommentStyle.CPP))

        # PROTO protobuf-file
        file_list.append(FileNameMapper(
            template_file=f"{self.tpl_proto_dir()}/simple_connect.proto",
            target_file=f"{self.proto_dir()}/{self.proto().lower()}.proto",
            comment_style=CommentStyle.PROTO))

        # TEST files
        file_list.append(FileNameMapper(
            template_file=f"{self.tpl_test_dir()}/grpc_client_tests.cc",
            target_file=f"{self.test_dir()}/{self.service_with_type().lower()}_client_tests.cc",
            comment_style=CommentStyle.CPP))
        file_list.append(FileNameMapper(
            template_file=f"{self.tpl_test_dir()}/grpc_service_tests.cc",
            target_file=f"{self.test_dir()}/{self.service_with_type().lower()}_service_tests.cc",
            comment_style=CommentStyle.CPP))
        file_list.append(FileNameMapper(
            template_file=f"{self.tpl_test_dir()}/run_tests.cc",
            target_file=f"{self.test_dir()}/run_{self.project_name().lower()}_tests.cc",
            comment_style=CommentStyle.CPP))

        if self.__add_docker:
            for tmplt in [("Dockerfile._server", CommentStyle.DOCKER),
                          ("Dockerfile._client", CommentStyle.DOCKER),
                          ("docker-compose.client-server.yml", CommentStyle.DOCKER),
                          (".client-server.env", CommentStyle.DOCKER)]:
                target_name = tmplt[0]
                target_name = target_name.replace(".client-server.", f".{self.service().lower()}.")
                target_name = target_name.replace("._server", f".{self.service().lower()}_server")
                target_name = target_name.replace("._client", f".{self.service().lower()}_client")
                file_list.append(
                    FileNameMapper(template_file=f"{this_dir}/templates/{tmplt[0]}",
                                   target_file=f"{self.project_path()}/{target_name}",
                                   comment_style=tmplt[1]))
        return file_list

    @overrides(ABCFileSetCreator)
    def get_tag_replacements(self) -> dict[str, str]:
        java_domain = ""
        email_dom = self.git_config["user.email"].split("@")
        if len(email_dom) > 1:
            comps = email_dom[1].split(".")
            comps.reverse()
            for comp in comps:
                if is_cpp_id(comp):
                    java_domain += comp.lower() + "."
            if is_empty_string(java_domain):
                java_domain = "com"
        java_domain += self.project_name().lower()

        return {
            "{{cookiecutter.java_domain}}": java_domain,
            "{{cookiecutter.proto_name}}": self.proto(),
            "{{cookiecutter.proto_name_lower}}": self.proto().lower(),
            "{{cookiecutter.proto_name_upper}}": self.proto().upper(),
            "{{cookiecutter.service_name}}": self.service(),
            "{{cookiecutter.service_name_lower}}": self.service().lower(),
            "{{cookiecutter.service_name_upper}}": self.service().upper(),
            "{{cookiecutter.service_name_with_messaging_type}}": self.service_with_type(),
            "{{cookiecutter.request}}": self.request(),
            "{{cookiecutter.request_lower}}": self.request().lower(),
            "{{cookiecutter.request_upper}}": self.request().upper(),
            "{{cookiecutter.messaging_type}}": self.msging_type(),
            "{{cookiecutter.port}}": self.port(),
            "{{cookiecutter.grpc_client_test_hash_includes}}": f'#include "{self.client_h()}"\n',
            "{{cookiecutter.grpc_service_test_hash_includes}}": f'#include "{self.service_h()}"\n',
        }

    def proto(self):
        return self.__proto

    def service(self):
        return self.__service

    def request(self):
        return self.__request

    def msging_type(self):
        return str(self.__messaging_type)

    def port(self):
        return str(self.__port)

    def service_with_type(self):
        service = self.service().lower()
        msg_type = str(self.__messaging_type)
        if not is_empty_string(msg_type):
            msg_type = "_" + msg_type
        return f"{service}{msg_type}"

    def __make_file_name(self, ext: str, file_type_str: str, is_template: bool):
        dash = ""
        if self.__messaging_type != GrpcMessagingType.DEFAULT:
            dash = "_"
        service = self.service().lower()
        if is_template:
            service = "grpc"
        return f"{service}_{self.__messaging_type}{dash}{file_type_str}.{ext}"

    def service_h(self):
        return self.__make_file_name(ext="h", file_type_str="service", is_template=False)

    def service_cc(self):
        return self.__make_file_name(ext="cc", file_type_str="service", is_template=False)

    def tpl_service_h(self):
        return self.__make_file_name(ext="h", file_type_str="service", is_template=True)

    def tpl_service_cc(self):
        return self.__make_file_name(ext="cc", file_type_str="service", is_template=True)

    def client_h(self):
        return self.__make_file_name(ext="h", file_type_str="client", is_template=False)

    def client_cc(self):
        return self.__make_file_name(ext="cc", file_type_str="client", is_template=False)

    def tpl_client_h(self):
        return self.__make_file_name(ext="h", file_type_str="client", is_template=True)

    def tpl_client_cc(self):
        return self.__make_file_name(ext="cc", file_type_str="client", is_template=True)

    def client_main_cc(self):
        return self.__make_file_name(ext="cc", file_type_str="client_main", is_template=False)

    def tpl_client_main_cc(self):
        return self.__make_file_name(ext="cc", file_type_str="client_main", is_template=True)

    def server_main_cc(self):
        return self.__make_file_name(ext="cc", file_type_str="server_main", is_template=False)

    def tpl_server_main_cc(self):
        return self.__make_file_name(ext="cc", file_type_str="server_main", is_template=True)
