[[LICENCE]]

#include "[[SERVICE_NAME_LOWER]]_async_client.h"

#include "[[PROTO_NAME_LOWER]].grpc.pb.h"

#include <grpc/support/log.h>
#include <grpcpp/grpcpp.h>
#include <iostream>
#include <memory>
#include <string>

[[SERVICE_NAME]]AsyncClient::[[SERVICE_NAME]]AsyncClient(std::shared_ptr<grpc::Channel> channel)
: stub_([[PROTO_NAME_LOWER]]::[[SERVICE_NAME]]Service::NewStub(channel))
{
}

// Assembles the client's payload, sends it and presents the response back
// from the server.
std::string [[SERVICE_NAME]]AsyncClient::Handle[[REQUEST]]Request(const std::string& user)
{
    // Data we are sending to the server.
    [[PROTO_NAME_LOWER]]::[[REQUEST]]RequestMessage request;
    request.set_request_string(user);

    // Container for the data we expect from the server.
    [[PROTO_NAME_LOWER]]::[[REQUEST]]ReplyMessage reply;

    // Context for the client. It could be used to convey extra information to
    // the server and/or tweak certain RPC behaviors.
    grpc::ClientContext context;

    // The producer-consumer queue we use to communicate asynchronously with the
    // gRPC runtime.
    grpc::CompletionQueue cq;

    // Storage for the status of the RPC upon completion.
    grpc::Status status;

    std::unique_ptr<grpc::ClientAsyncResponseReader<[[PROTO_NAME_LOWER]]::[[REQUEST]]ReplyMessage>> rpc(
     stub_->AsyncHandle[[REQUEST]]Request(&context, request, &cq));

    // Request that, upon completion of the RPC, "reply" be updated with the
    // server's response; "status" with the indication of whether the operation
    // was successful. Tag the request with the integer 1.
    rpc->Finish(&reply, &status, (void*)1);
    void* got_tag;
    bool  ok = false;
    // Block until the next result is available in the completion queue "cq".
    // The return value of Next should always be checked. This return value
    // tells us whether there is any kind of event or the cq_ is shutting down.
    GPR_ASSERT(cq.Next(&got_tag, &ok));

    // Verify that the result from "cq" corresponds, by its tag, our previous
    // request.
    GPR_ASSERT(got_tag == (void*)1);
    // ... and that the request was completed successfully. Note that "ok"
    // corresponds solely to the request for updates introduced by Finish().
    GPR_ASSERT(ok);

    // Act upon the status of the actual RPC.
    if(status.ok())
    {
        return reply.reply_string();
    }
    else
    {
        return "RPC failed";
    }
}