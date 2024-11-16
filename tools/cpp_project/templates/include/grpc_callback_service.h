{{cookiecutter.licence}}

#ifndef {{cookiecutter.service_name_upper}}_CALLBACK_SERVICE_H_INCLUDED
#define {{cookiecutter.service_name_upper}}_CALLBACK_SERVICE_H_INCLUDED

#include "{{cookiecutter.proto_name_lower}}.grpc.pb.h"

#include <absl/flags/flag.h>
#include <absl/flags/parse.h>
#include <absl/strings/str_format.h>
#include <grpcpp/ext/proto_server_reflection_plugin.h>
#include <grpcpp/grpcpp.h>
#include <grpcpp/health_check_service_interface.h>
#include <iostream>
#include <memory>
#include <string>

namespace ns_{{cookiecutter.project_name_lower}}
{

// Logic and data behind the server's behavior.
class {{cookiecutter.service_name}}CallbackServiceImpl final : public {{cookiecutter.proto_name_lower}}::{{cookiecutter.service_name}}Service::CallbackService
{
    grpc::ServerUnaryReactor* Handle{{cookiecutter.request}}Request(
        grpc::CallbackServerContext* context,
        const {{cookiecutter.proto_name_lower}}::{{cookiecutter.request}}RequestMessage* request,
        {{cookiecutter.proto_name_lower}}::{{cookiecutter.request}}ReplyMessage* reply) override;
    public:
    static void RunServer(uint16_t port);
};

};  // namespace ns_{{cookiecutter.project_name_lower}}

#endif  // {{cookiecutter.service_name_upper}}_CALLBACK_SERVICE_H_INCLUDED
