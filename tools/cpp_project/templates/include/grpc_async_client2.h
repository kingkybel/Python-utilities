[[LICENCE]]

#ifndef [[SERVICE_NAME_UPPER]]_ASYNCH_CLIENT2_H_INCLUDED
#define [[SERVICE_NAME_UPPER]]_ASYNCH_CLIENT2_H_INCLUDED

#include "[[PROTO_NAME_LOWER]].grpc.pb.h"

#include <grpc/support/log.h>
#include <grpcpp/grpcpp.h>
#include <memory>
#include <string>

namespace ns_[[PROJECT_NAME_LOWER]]
{

class [[SERVICE_NAME]]Client
{
    public:
    explicit [[SERVICE_NAME]]Client(std::shared_ptr<grpc::Channel> channel);

    // Assembles the client's payload and sends it to the server.
    void Handle[[REQUEST]]Request(const std::string& user);

    // Loop while listening for completed responses.
    // Prints out the response from the server.
    void AsyncCompleteRpc();

    private:
    // struct for keeping state and data information
    struct AsyncClientCall
    {
        // Container for the data we expect from the server.
        [[PROTO_NAME_LOWER]]::[[REQUEST]]ReplyMessage reply;

        // Context for the client. It could be used to convey extra information to
        // the server and/or tweak certain RPC behaviors.
        grpc::ClientContext context;

        // Storage for the status of the RPC upon completion.
        grpc::Status status;

        std::unique_ptr<grpc::ClientAsyncResponseReader<[[PROTO_NAME_LOWER]]::[[REQUEST]]ReplyMessage>> response_reader;
    };

    // Out of the passed in Channel comes the stub, stored here, our view of the
    // server's exposed services.
    std::unique_ptr<[[PROTO_NAME_LOWER]]::[[SERVICE_NAME]]Service::Stub> stub_;

    // The producer-consumer queue we use to communicate asynchronously with the
    // gRPC runtime.
    grpc::CompletionQueue cq_;
};

};  // namespace ns_[[PROJECT_NAME_LOWER]]

#endif  // [[SERVICE_NAME_UPPER]]_ASYNCH_CLIENT_H_INCLUDED
