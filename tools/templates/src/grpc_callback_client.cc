[[LICENCE]]
#include "[[SERVICE_NAME_LOWER]]_callback_client.h"

#include "[[PROTO_NAME_LOWER]].grpc.pb.h"

#include <condition_variable>
#include <grpcpp/grpcpp.h>
#include <iostream>
#include <memory>
#include <mutex>
#include <string>

[[SERVICE_NAME]]CallbackClient::[[SERVICE_NAME]]CallbackClient(std::shared_ptr<grpc::Channel> channel)
: stub_([[PROTO_NAME_LOWER]]::[[SERVICE_NAME]]Service::NewStub(channel))
{
}

// Assembles the client's payload, sends it and presents the response back
// from the server.
std::string [[SERVICE_NAME]]CallbackClient::Handle[[REQUEST]]Request(const std::string& user)
{
    // Data we are sending to the server.
    [[PROTO_NAME_LOWER]]::[[REQUEST]]RequestMessage request;
    request.set_request_string(user);

    // Container for the data we expect from the server.
    [[PROTO_NAME_LOWER]]::[[REQUEST]]ReplyMessage reply;

    // Context for the client. It could be used to convey extra information to
    // the server and/or tweak certain RPC behaviors.
    grpc::ClientContext context;

    // The actual RPC.
    std::mutex              mu;
    std::condition_variable cv;
    bool                    done = false;
    grpc::Status            status;
    stub_->async()->Handle[[REQUEST]]Request(&context,
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
