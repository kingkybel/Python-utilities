{{cookiecutter.licence}}

#include "{{cookiecutter.service_name_lower}}_callback_service.h"

#include "{{cookiecutter.proto_name_lower}}.grpc.pb.h"

#include <grpcpp/ext/proto_server_reflection_plugin.h>
#include <grpcpp/grpcpp.h>
#include <grpcpp/health_check_service_interface.h>
#include <iostream>
#include <memory>
#include <string>
#include <sstream>

namespace ns_{{cookiecutter.project_name_lower}}
{

// Logic and data behind the server's behavior.
grpc::ServerUnaryReactor* {{cookiecutter.service_name}}CallbackServiceImpl::Handle{{cookiecutter.request}}Request(
    grpc::CallbackServerContext* context,
    const {{cookiecutter.proto_name_lower}}::{{cookiecutter.request}}RequestMessage* request,
    {{cookiecutter.proto_name_lower}}::{{cookiecutter.request}}ReplyMessage* reply)
{
    std::string prefix("{{cookiecutter.service_name}} just handled ");
    reply->set_reply_string(prefix + request->request_string());

    grpc::ServerUnaryReactor* reactor = context->DefaultReactor();
    reactor->Finish(grpc::Status::OK);
    return reactor;
}

void {{cookiecutter.service_name}}CallbackServiceImpl::RunServer(uint16_t port)
{
    std::stringstream ss;
    ss << "0.0.0.0:" << port;
    std::string server_address = ss.str();
    {{cookiecutter.service_name}}CallbackServiceImpl service;

    grpc::EnableDefaultHealthCheckService(true);
    grpc::reflection::InitProtoReflectionServerBuilderPlugin();
    grpc::ServerBuilder builder;
    // Listen on the given address without any authentication mechanism.
    builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
    // Register "service" as the instance through which we'll communicate with
    // clients. In this case it corresponds to an *synchronous* service.
    builder.RegisterService(&service);
    // Finally assemble the server.
    std::unique_ptr<grpc::Server> server(builder.BuildAndStart());
    std::cout << "Server listening on " << server_address << std::endl;

    // Wait for the server to shutdown. Note that some other thread must be
    // responsible for shutting down the server for this call to ever return.
    server->Wait();
}

};  // namespace ns_{{cookiecutter.project_name_lower}}
