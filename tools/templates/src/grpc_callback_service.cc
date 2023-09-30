[[LICENCE]]

#include "[[SERVICE_NAME_LOWER]]_callback_service.h"

#include "[[PROTO_NAME_LOWER]].grpc.pb.h"

#include <grpcpp/ext/proto_server_reflection_plugin.h>
#include <grpcpp/grpcpp.h>
#include <grpcpp/health_check_service_interface.h>
#include <iostream>
#include <memory>
#include <string>
#include <sstream>

using grpc::CallbackServerContext;
using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerUnaryReactor;
using grpc::Status;
using [[PROTO_NAME_LOWER]]::[[SERVICE_NAME]]Service;
using [[PROTO_NAME_LOWER]]::[[REQUEST]]ReplyMessage;
using [[PROTO_NAME_LOWER]]::[[REQUEST]]RequestMessage;

// Logic and data behind the server's behavior.
grpc::ServerUnaryReactor* [[SERVICE_NAME]]CallbackServiceImpl::Handle[[REQUEST]]Request(
    grpc::CallbackServerContext* context,
    const [[PROTO_NAME_LOWER]]::[[REQUEST]]RequestMessage* request,
    [[PROTO_NAME_LOWER]]::[[REQUEST]]ReplyMessage* reply)
{
    std::string prefix("[[SERVICE_NAME]] just handled ");
    reply->set_reply_string(prefix + request->request_string());

    ServerUnaryReactor* reactor = context->DefaultReactor();
    reactor->Finish(Status::OK);
    return reactor;
}

void [[SERVICE_NAME]]CallbackServiceImpl::RunServer(uint16_t port)
{
    std::stringstream ss;
    ss << "0.0.0.0:" << port;
    std::string server_address = ss.str();
    [[SERVICE_NAME]]CallbackServiceImpl service;

    grpc::EnableDefaultHealthCheckService(true);
    grpc::reflection::InitProtoReflectionServerBuilderPlugin();
    ServerBuilder builder;
    // Listen on the given address without any authentication mechanism.
    builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
    // Register "service" as the instance through which we'll communicate with
    // clients. In this case it corresponds to an *synchronous* service.
    builder.RegisterService(&service);
    // Finally assemble the server.
    std::unique_ptr<Server> server(builder.BuildAndStart());
    std::cout << "Server listening on " << server_address << std::endl;

    // Wait for the server to shutdown. Note that some other thread must be
    // responsible for shutting down the server for this call to ever return.
    server->Wait();
}
