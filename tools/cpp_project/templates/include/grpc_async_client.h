{{cookiecutter.licence}}

#ifndef {{cookiecutter.service_name_upper}}_ASYNCH_CLIENT_H_INCLUDED
#define {{cookiecutter.service_name_upper}}_ASYNCH_CLIENT_H_INCLUDED

#include "{{cookiecutter.proto_name_lower}}.grpc.pb.h"

#include <grpc/support/log.h>
#include <grpcpp/grpcpp.h>
#include <memory>
#include <string>

namespace ns_{{cookiecutter.project_name_lower}}
{

class {{cookiecutter.service_name}}AsyncClient
{
    public:
    explicit {{cookiecutter.service_name}}AsyncClient(std::shared_ptr<grpc::Channel> channel);

    // Assembles the client's payload, sends it and presents the response back
    // from the server.
    std::string Handle{{cookiecutter.request}}Request(const std::string& user);

    private:
    // Out of the passed in Channel comes the stub, stored here, our view of the
    // server's exposed services.
    std::unique_ptr<{{cookiecutter.proto_name_lower}}::{{cookiecutter.service_name}}Service::Stub> stub_;
};

};  // namespace ns_{{cookiecutter.project_name_lower}}

#endif  // {{cookiecutter.service_name_upper}}_ASYNCH_CLIENT_H_INCLUDED
