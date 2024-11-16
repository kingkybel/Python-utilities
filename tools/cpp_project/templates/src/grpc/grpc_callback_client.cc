{{cookiecutter.licence}}
#include "{{cookiecutter.service_name_lower}}_callback_client.h"

#include "{{cookiecutter.proto_name_lower}}.grpc.pb.h"

#include <condition_variable>
#include <grpcpp/grpcpp.h>
#include <iostream>
#include <memory>
#include <mutex>
#include <string>

namespace ns_{{cookiecutter.project_name_lower}}
{

{{cookiecutter.service_name}}CallbackClient::{{cookiecutter.service_name}}CallbackClient(std::shared_ptr<grpc::Channel> channel)
: stub_({{cookiecutter.proto_name_lower}}::{{cookiecutter.service_name}}Service::NewStub(channel))
{
}

// Assembles the client's payload, sends it and presents the response back
// from the server.
std::string {{cookiecutter.service_name}}CallbackClient::Handle{{cookiecutter.request}}Request(const std::string& user)
{
    // Data we are sending to the server.
    {{cookiecutter.proto_name_lower}}::{{cookiecutter.request}}RequestMessage request;
    request.set_request_string(user);

    // Container for the data we expect from the server.
    {{cookiecutter.proto_name_lower}}::{{cookiecutter.request}}ReplyMessage reply;

    // Context for the client. It could be used to convey extra information to
    // the server and/or tweak certain RPC behaviors.
    grpc::ClientContext context;

    // The actual RPC.
    std::mutex              mu;
    std::condition_variable cv;
    bool                    done = false;
    grpc::Status            status;
    stub_->async()->Handle{{cookiecutter.request}}Request(&context,
                             &request,
                             &reply,
                             [&mu, &cv, &done, &status](grpc::Status s)
                             {
                                 status = std::move(s);
                                 std::lock_guard<std::mutex> lock(mu);
                                 done = true;
                                 cv.notify_one();
                             });

    std::unique_lock<std::mutex> lock(mu);
    while(!done)
    {
        cv.wait(lock);
    }

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
