[[LICENCE]]

#include "[[SERVICE_NAME_LOWER]]_async_client2.h"

#include "[[PROTO_NAME_LOWER]].grpc.pb.h"

#include <grpc/support/log.h>
#include <grpcpp/grpcpp.h>
#include <iostream>
#include <memory>
#include <string>
#include <thread>

namespace ns_[[PROJECT_NAME_LOWER]]
{

[[SERVICE_NAME]]Client::[[SERVICE_NAME]]Client(std::shared_ptr<grpc::Channel> channel)
: stub_([[PROTO_NAME_LOWER]]::[[SERVICE_NAME]]Service::NewStub(channel))
{
}

// Assembles the client's payload and sends it to the server.
void [[SERVICE_NAME]]Client::Handle[[REQUEST]]Request(const std::string& user)
{
    // Data we are sending to the server.
    [[PROTO_NAME_LOWER]]::[[REQUEST]]RequestMessage request;
    request.set_request_string(user);

    // Call object to store rpc data
    AsyncClientCall* call = new AsyncClientCall{};

    // stub_->PrepareAsyncSayHello() creates an RPC object, returning
    // an instance to store in "call" but does not actually start the RPC
    // Because we are using the asynchronous API, we need to hold on to
    // the "call" instance in order to get updates on the ongoing RPC.
    call->response_reader = stub_->PrepareAsyncSayHello(&call->context, request, &cq_);

    // StartCall initiates the RPC call
    call->response_reader->StartCall();

    // Request that, upon completion of the RPC, "reply" be updated with the
    // server's response; "status" with the indication of whether the operation
    // was successful. Tag the request with the memory address of the call
    // object.
    call->response_reader->Finish(&call->reply, &call->status, (void*)call);
}

// Loop while listening for completed responses.
// Prints out the response from the server.
void [[SERVICE_NAME]]Client::AsyncCompleteRpc()
{
    void* got_tag;
    bool  ok = false;

    // Block until the next result is available in the completion queue "cq".
    while(cq_.Next(&got_tag, &ok))
    {
        // The tag in this example is the memory location of the call object
        AsyncClientCall* call = static_cast<AsyncClientCall*>(got_tag);

        // Verify that the request was completed successfully. Note that "ok"
        // corresponds solely to the request for updates introduced by Finish().
        GPR_ASSERT(ok);

        if(call->status.ok())
            std::cout << "Answer to [[REQUEST]] received: " << call->reply.reply_string() << std::endl;
        else
            std::cout << "RPC failed" << std::endl;

        // Once we're complete, deallocate the call object.
        delete call;
    }
}

};  // namespace ns_[[PROJECT_NAME_LOWER]]
