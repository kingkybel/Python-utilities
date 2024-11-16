{{cookiecutter.licence}}

#ifndef {{cookiecutter.service_name_upper}}_CLIENT_H_INCLUDED
#define {{cookiecutter.service_name_upper}}_CLIENT_H_INCLUDED

#include "{{cookiecutter.proto_name_lower}}.grpc.pb.h"

#include <grpcpp/grpcpp.h>

namespace ns_{{cookiecutter.project_name_lower}}
{

class {{cookiecutter.service_name}}Client
{
    public:
    {{cookiecutter.service_name}}Client(std::shared_ptr<grpc::Channel> channel);

    // Assembles the client's payload, sends it and presents the response back
    // from the server.
    std::string Handle{{cookiecutter.request}}Request(const std::string& request_str);

    private:
    std::unique_ptr<{{cookiecutter.proto_name_lower}}::{{cookiecutter.service_name}}Service::Stub> stub_;
};

};  // namespace ns_{{cookiecutter.project_name_lower}}

#endif  // {{cookiecutter.service_name_upper}}_CLIENT_H_INCLUDED
