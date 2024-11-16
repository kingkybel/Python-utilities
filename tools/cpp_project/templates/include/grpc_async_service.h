{{cookiecutter.licence}}

#ifndef {{cookiecutter.service_name_upper}}_ASYNCH_SERVICE_H_INCLUDED
#define {{cookiecutter.service_name_upper}}_ASYNCH_SERVICE_H_INCLUDED

#include "{{cookiecutter.proto_name_lower}}.grpc.pb.h"

#include <absl/flags/flag.h>
#include <absl/flags/parse.h>
#include <absl/strings/str_format.h>
#include <grpc/support/log.h>
#include <grpcpp/grpcpp.h>
#include <iostream>
#include <memory>
#include <string>
#include <thread>

namespace ns_{{cookiecutter.project_name_lower}}
{

class {{cookiecutter.service_name}}AsynchServiceImpl final
{
    public:
    ~{{cookiecutter.service_name}}AsynchServiceImpl();

    // There is no shutdown handling in this code.
    void Run(uint16_t port);

    private:
    // Class encompassing the state and logic needed to serve a request.
    class CallData
    {
        public:
        // Take in the "service" instance (in this case representing an asynchronous
        // server) and the completion queue "cq" used for asynchronous communication
        // with the gRPC runtime.
        CallData({{cookiecutter.proto_name_lower}}::{{cookiecutter.service_name}}Service::AsyncService* service, grpc::ServerCompletionQueue* cq);

        void Proceed();

        private:
        // The means of communication with the gRPC runtime for an asynchronous
        // server.
        {{cookiecutter.proto_name_lower}}::{{cookiecutter.service_name}}Service::AsyncService* service_;
        // The producer-consumer queue where for asynchronous server notifications.
        grpc::ServerCompletionQueue* cq_;
        // Context for the rpc, allowing to tweak aspects of it such as the use
        // of compression, authentication, as well as to send metadata back to the
        // client.
        grpc::ServerContext ctx_;

        // What we get from the client.
        {{cookiecutter.proto_name_lower}}::{{cookiecutter.request}}RequestMessage request_;
        // What we send back to the client.
        {{cookiecutter.proto_name_lower}}::{{cookiecutter.request}}ReplyMessage reply_;

        // The means to get back to the client.
        grpc::ServerAsyncResponseWriter<{{cookiecutter.proto_name_lower}}::{{cookiecutter.request}}ReplyMessage> responder_;

        // Let's implement a tiny state machine with the following states.
        enum CallStatus
        {
            CREATE,
            PROCESS,
            FINISH
        };
        CallStatus status_;  // The current serving state.
    };

    // This can be run in multiple threads if needed.
    void HandleRpcs();

    std::unique_ptr<grpc::ServerCompletionQueue> cq_;
    {{cookiecutter.proto_name_lower}}::{{cookiecutter.service_name}}Service::AsyncService service_;
    std::unique_ptr<grpc::Server> server_;
};

};  // namespace ns_{{cookiecutter.project_name_lower}}

#endif  // {{cookiecutter.service_name_upper}}_ASYNCH_SERVICE_H_INCLUDED
