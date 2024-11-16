{{cookiecutter.licence}}
#include "{{cookiecutter.service_name_lower}}_client.h"

#include "{{cookiecutter.proto_name_lower}}.grpc.pb.h"

#include <grpcpp/grpcpp.h>
#include <iostream>
#include <memory>
#include <string>

namespace ns_{{cookiecutter.project_name_lower}}
{

{{cookiecutter.service_name}}Client::{{cookiecutter.service_name}}Client(std::shared_ptr<grpc::Channel> channel)
: stub_({{cookiecutter.proto_name_lower}}::{{cookiecutter.service_name}}Service::NewStub(channel))
{
}

// Assembles the client's payload, sends it and presents the response back
// from the server.
std::string {{cookiecutter.service_name}}Client::Handle{{cookiecutter.request}}Request(const std::string& request_str)
{
    // Data we are sending to the server.
    {{cookiecutter.proto_name_lower}}::{{cookiecutter.request}}RequestMessage request;
    request.set_request_string(request_str);

    // Container for the data we expect from the server.
    {{cookiecutter.proto_name_lower}}::{{cookiecutter.request}}ReplyMessage reply;

    // Context for the client. It could be used to convey extra information to
    // the server and/or tweak certain RPC behaviors.
    grpc::ClientContext context;

    // The actual RPC.
    grpc::Status status = stub_->Handle{{cookiecutter.request}}Request(&context, request, &reply);

    // Act upon its status.
    if(status.ok())
    {
        return reply.reply_string();
    }
    else
    {
        std::cout << status.error_code() << ": " << status.error_message() << std::endl;
        return "RPC failed";
    }
}

};  // namespace ns_{{cookiecutter.project_name_lower}}
