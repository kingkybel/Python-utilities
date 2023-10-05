[[LICENCE]]

#ifndef [[SERVICE_NAME_UPPER]]_CALLBACK_CLIENT_H_INCLUDED
#define [[SERVICE_NAME_UPPER]]_CALLBACK_CLIENT_H_INCLUDED

#include "[[PROTO_NAME_LOWER]].grpc.pb.h"

#include <condition_variable>
#include <grpcpp/grpcpp.h>
#include <iostream>
#include <memory>
#include <mutex>
#include <string>

namespace ns_[[PROJECT_NAME_LOWER]]
{

class [[SERVICE_NAME]]CallbackClient
{
    public:
    [[SERVICE_NAME]]CallbackClient(std::shared_ptr<grpc::Channel> channel);

    // Assembles the client's payload, sends it and presents the response back
    // from the server.
    std::string Handle[[REQUEST]]Request(const std::string& user);

    private:
    std::unique_ptr<[[PROTO_NAME_LOWER]]::[[SERVICE_NAME]]Service::Stub> stub_;
};

};  // namespace ns_[[PROJECT_NAME_LOWER]]

#endif  // [[SERVICE_NAME_UPPER]]_CALLBACK_CLIENT_H_INCLUDED
