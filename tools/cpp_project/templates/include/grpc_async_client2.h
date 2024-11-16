{{cookiecutter.licence}}

#ifndef {{cookiecutter.service_name_upper}}_ASYNCH_CLIENT2_H_INCLUDED
#define {{cookiecutter.service_name_upper}}_ASYNCH_CLIENT2_H_INCLUDED

#include "{{cookiecutter.proto_name_lower}}.grpc.pb.h"

#include <grpc/support/log.h>
#include <grpcpp/grpcpp.h>
#include <memory>
#include <string>

namespace ns_{{cookiecutter.project_name_lower}}
{

class {{cookiecutter.service_name}}Client
{
    public:
    explicit {{cookiecutter.service_name}}Client(std::shared_ptr<grpc::Channel> channel);

    // Assembles the client's payload and sends it to the server.
    void Handle{{cookiecutter.request}}Request(const std::string& user);

    // Loop while listening for completed responses.
    // Prints out the response from the server.
    void AsyncCompleteRpc();

    private:
    // struct for keeping state and data information
    struct AsyncClientCall
    {
        // Container for the data we expect from the server.
        {{cookiecutter.proto_name_lower}}::{{cookiecutter.request}}ReplyMessage reply;

        // Context for the client. It could be used to convey extra information to
        // the server and/or tweak certain RPC behaviors.
        grpc::ClientContext context;

        // Storage for the status of the RPC upon completion.
        grpc::Status status;

        std::unique_ptr<grpc::ClientAsyncResponseReader<{{cookiecutter.proto_name_lower}}::{{cookiecutter.request}}ReplyMessage>> response_reader;
    };

    // Out of the passed in Channel comes the stub, stored here, our view of the
    // server's exposed services.
    std::unique_ptr<{{cookiecutter.proto_name_lower}}::{{cookiecutter.service_name}}Service::Stub> stub_;

    // The producer-consumer queue we use to communicate asynchronously with the
    // gRPC runtime.
    grpc::CompletionQueue cq_;
};

};  // namespace ns_{{cookiecutter.project_name_lower}}

#endif  // {{cookiecutter.service_name_upper}}_ASYNCH_CLIENT_H_INCLUDED
