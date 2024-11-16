{{cookiecutter.licence}}
#include "{{cookiecutter.service_name_lower}}_service.h"

#include "{{cookiecutter.proto_name_lower}}.grpc.pb.h"

#include <grpcpp/ext/proto_server_reflection_plugin.h>
#include <grpcpp/grpcpp.h>
#include <grpcpp/health_check_service_interface.h>
#include <iostream>
#include <memory>
#include <sstream>
#include <string>
#include <thread>

namespace ns_{{cookiecutter.project_name_lower}}
{

grpc::Status {{cookiecutter.service_name}}ServiceImpl::Handle{{cookiecutter.request}}Request(
        grpc::ServerContext* context,
        const {{cookiecutter.proto_name_lower}}::{{cookiecutter.request}}RequestMessage* request,
        {{cookiecutter.proto_name_lower}}::{{cookiecutter.request}}ReplyMessage* reply)
{
    std::string prefix{"Dispatched "};
    reply->set_reply_string(prefix + request->request_string());
    return grpc::Status::OK;
}

std::thread {{cookiecutter.service_name}}ServiceImpl::Run(uint16_t port)
{
    grpc::EnableDefaultHealthCheckService(true);
    grpc::reflection::InitProtoReflectionServerBuilderPlugin();
    std::stringstream ss;
    ss << "0.0.0.0:" << port;
    std::string server_address = ss.str();

    grpc::ServerBuilder builder;

    // Listen on the given address without any authentication mechanism.
    builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());

    // Register "service" as the instance through which we'll communicate with
    // clients. In this case it corresponds to an *synchronous* service.
    builder.RegisterService(this);

    // Finally assemble the server.
    std::cout << "Server listening on " << server_address << std::endl;
    server_ = builder.BuildAndStart();

    // Wait for the server to shutdown. Note that some other thread must be
    // responsible for shutting down the server for this call to ever return.
    return std::thread{[&](){this->started_ = true; this->server_->Wait();}};
}

void {{cookiecutter.service_name}}ServiceImpl::ShutDown()
{
    if(server_ != nullptr && started_)
        server_->Shutdown();
}

};  // namespace ns_{{cookiecutter.project_name_lower}}
