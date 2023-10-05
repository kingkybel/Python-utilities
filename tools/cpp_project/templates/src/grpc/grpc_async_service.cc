[[LICENCE]]

#include "[[SERVICE_NAME_LOWER]]_async_service.h"

#include "[[PROTO_NAME_LOWER]].grpc.pb.h"

#include <grpc/support/log.h>
#include <grpcpp/grpcpp.h>
#include <iostream>
#include <memory>
#include <sstream>
#include <string>
#include <thread>

namespace ns_[[PROJECT_NAME_LOWER]]
{

[[SERVICE_NAME]]AsynchServiceImpl::~[[SERVICE_NAME]]AsynchServiceImpl()
{
    server_->Shutdown();
    // Always shutdown the completion queue after the server.
    cq_->Shutdown();
}

// There is no shutdown handling in this code.
void [[SERVICE_NAME]]AsynchServiceImpl::Run(uint16_t port)
{
    std::stringstream ss;
    ss << "0.0.0.0:" << port;
    std::string server_address = ss.str();

    grpc::ServerBuilder builder;
    // Listen on the given address without any authentication mechanism.
    builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
    // Register "service_" as the instance through which we'll communicate with
    // clients. In this case it corresponds to an *asynchronous* service.
    builder.RegisterService(&service_);
    // Get hold of the completion queue used for the asynchronous communication
    // with the gRPC runtime.
    cq_ = builder.AddCompletionQueue();
    // Finally assemble the server.
    server_ = builder.BuildAndStart();
    std::cout << "Server listening on " << server_address << std::endl;

    // Proceed to the server's main loop.
    HandleRpcs();
}

// Take in the "service" instance (in this case representing an asynchronous
// server) and the completion queue "cq" used for asynchronous communication
// with the gRPC runtime.
[[SERVICE_NAME]]AsynchServiceImpl::CallData::CallData(
    [[PROTO_NAME_LOWER]]::[[SERVICE_NAME]]Service::AsyncService* service,
    grpc::ServerCompletionQueue* cq)
: service_(service)
, cq_(cq)
, responder_(&ctx_)
, status_(CREATE)
{
    // Invoke the serving logic right away.
    Proceed();
}

void [[SERVICE_NAME]]AsynchServiceImpl::CallData::Proceed()
{
    if(status_ == CREATE)
    {
        // Make this instance progress to the PROCESS state.
        status_ = PROCESS;

        // As part of the initial CREATE state, we *request* that the system
        // start processing Handle[[REQUEST]]Request requests. In this request, "this" acts are
        // the tag uniquely identifying the request (so that different CallData
        // instances can serve different requests concurrently), in this case
        // the memory address of this CallData instance.
        service_->RequestHandle[[REQUEST]]Request(&ctx_, &request_, &responder_, cq_, cq_, this);
    }
    else if(status_ == PROCESS)
    {
        // Spawn a new CallData instance to serve new clients while we process
        // the one for this CallData. The instance will deallocate itself as
        // part of its FINISH state.
        new CallData(service_, cq_);

        // The actual processing.
        std::string prefix("[[SERVICE_NAME]]AsynchService handled '");
        reply_.set_reply_string(prefix + request_.request_string() + "'");

        // And we are done! Let the gRPC runtime know we've finished, using the
        // memory address of this instance as the uniquely identifying tag for
        // the event.
        status_ = FINISH;
        responder_.Finish(reply_, grpc::Status::OK, this);
    }
    else
    {
        GPR_ASSERT(status_ == FINISH);
        // Once in the FINISH state, deallocate ourselves (CallData).
        delete this;
    }
}

// This can be run in multiple threads if needed.
void [[SERVICE_NAME]]AsynchServiceImpl::HandleRpcs()
{
    // Spawn a new CallData instance to serve new clients.
    new CallData(&service_, cq_.get());
    void* tag;  // uniquely identifies a request.
    bool  ok;
    while(true)
    {
        // Block waiting to read the next event from the completion queue. The
        // event is uniquely identified by its tag, which in this case is the
        // memory address of a CallData instance.
        // The return value of Next should always be checked. This return value
        // tells us whether there is any kind of event or cq_ is shutting down.
        GPR_ASSERT(cq_->Next(&tag, &ok));
        GPR_ASSERT(ok);
        static_cast<CallData*>(tag)->Proceed();
    }
}

};  // namespace ns_[[PROJECT_NAME_LOWER]]
