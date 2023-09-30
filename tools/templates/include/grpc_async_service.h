[[LICENCE]]

#include "[[PROTO_NAME_LOWER]].grpc.pb.h"

#include <absl/flags/flag.h>
#include <absl/flags/parse.h>
#include <absl/strings/str_format.h>
#include <grpc/support/log.h>
#include <grpcpp/grpcpp.h>
#include <iostream>
#include <memory>
#include <string>
#include <thread>

class [[SERVICE_NAME]]AsynchServiceImpl final
{
    public:
    ~[[SERVICE_NAME]]AsynchServiceImpl();

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
        CallData([[PROTO_NAME_LOWER]]::[[SERVICE_NAME]]Service::AsyncService* service, grpc::ServerCompletionQueue* cq);

        void Proceed();

        private:
        // The means of communication with the gRPC runtime for an asynchronous
        // server.
        [[PROTO_NAME_LOWER]]::[[SERVICE_NAME]]Service::AsyncService* service_;
        // The producer-consumer queue where for asynchronous server notifications.
        grpc::ServerCompletionQueue* cq_;
        // Context for the rpc, allowing to tweak aspects of it such as the use
        // of compression, authentication, as well as to send metadata back to the
        // client.
        grpc::ServerContext ctx_;

        // What we get from the client.
        [[PROTO_NAME_LOWER]]::[[REQUEST]]RequestMessage request_;
        // What we send back to the client.
        [[PROTO_NAME_LOWER]]::[[REQUEST]]ReplyMessage reply_;

        // The means to get back to the client.
        grpc::ServerAsyncResponseWriter<[[PROTO_NAME_LOWER]]::[[REQUEST]]ReplyMessage> responder_;

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
    [[PROTO_NAME_LOWER]]::[[SERVICE_NAME]]Service::AsyncService service_;
    std::unique_ptr<grpc::Server> server_;
};
