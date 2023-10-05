[[LICENCE]]

#ifndef [[SERVICE_NAME_UPPER]]_CLIENT_H_INCLUDED
#define [[SERVICE_NAME_UPPER]]_CLIENT_H_INCLUDED

#include "[[PROTO_NAME_LOWER]].grpc.pb.h"

#include <grpcpp/grpcpp.h>

namespace ns_[[PROJECT_NAME_LOWER]]
{

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

};  // namespace ns_[[PROJECT_NAME_LOWER]]

#endif  // [[SERVICE_NAME_UPPER]]_CLIENT_H_INCLUDED
