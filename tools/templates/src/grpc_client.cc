[[LICENCE]]
#include "[[SERVICE_NAME_LOWER]]_client.h"

#include "[[PROTO_NAME_LOWER]].grpc.pb.h"

#include <grpcpp/grpcpp.h>
#include <iostream>
#include <memory>
#include <string>

using grpc::Channel;
using grpc::ClientContext;
using grpc::Status;
using [[PROTO_NAME_LOWER]]::[[SERVICE_NAME]]Service;
using [[PROTO_NAME_LOWER]]::[[REQUEST]]ReplyMessage;
using [[PROTO_NAME_LOWER]]::[[REQUEST]]RequestMessage;

[[SERVICE_NAME]]Client::[[SERVICE_NAME]]Client(std::shared_ptr<Channel> channel) : stub_([[SERVICE_NAME]]Service::NewStub(channel))
{
}

// Assembles the client's payload, sends it and presents the response back
// from the server.
std::string [[SERVICE_NAME]]Client::Handle[[REQUEST]]Request(const std::string& request_str)
{
    // Data we are sending to the server.
    [[REQUEST]]RequestMessage request;
    request.set_request_string(request_str);

    // Container for the data we expect from the server.
    [[REQUEST]]ReplyMessage reply;

    // Context for the client. It could be used to convey extra information to
    // the server and/or tweak certain RPC behaviors.
    ClientContext context;

    // The actual RPC.
    Status status = stub_->Handle[[REQUEST]]Request(&context, request, &reply);

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
