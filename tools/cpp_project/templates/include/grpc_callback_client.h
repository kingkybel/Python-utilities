{{cookiecutter.licence}}

#ifndef {{cookiecutter.service_name_upper}}_CALLBACK_CLIENT_H_INCLUDED
#define {{cookiecutter.service_name_upper}}_CALLBACK_CLIENT_H_INCLUDED

#include "{{cookiecutter.proto_name_lower}}.grpc.pb.h"

#include <condition_variable>
#include <grpcpp/grpcpp.h>
#include <iostream>
#include <memory>
#include <mutex>
#include <string>

namespace ns_{{cookiecutter.project_name_lower}}
{

class {{cookiecutter.service_name}}CallbackClient
{
    public:
    {{cookiecutter.service_name}}CallbackClient(std::shared_ptr<grpc::Channel> channel);

    // Assembles the client's payload, sends it and presents the response back
    // from the server.
    std::string Handle{{cookiecutter.request}}Request(const std::string& user);

    private:
    std::unique_ptr<{{cookiecutter.proto_name_lower}}::{{cookiecutter.service_name}}Service::Stub> stub_;
};

};  // namespace ns_{{cookiecutter.project_name_lower}}

#endif  // {{cookiecutter.service_name_upper}}_CALLBACK_CLIENT_H_INCLUDED
