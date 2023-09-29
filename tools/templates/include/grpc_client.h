[[LICENCE]]

#include "[[PROTO_NAME_LOWER]].grpc.pb.h"

#include <grpcpp/grpcpp.h>

class [[SERVICE_NAME]]Client
{
    public:
    [[SERVICE_NAME]]Client(std::shared_ptr<grpc::Channel> channel);

    // Assembles the client's payload, sends it and presents the response back
    // from the server.
    std::string Handle[[REQUEST]]Request(const std::string& request_str);

    private:
    std::unique_ptr<[[PROTO_NAME_LOWER]]::[[SERVICE_NAME]]Service::Stub> stub_;
};
