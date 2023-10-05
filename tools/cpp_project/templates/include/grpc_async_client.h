[[LICENCE]]

#ifndef [[SERVICE_NAME]]_ASYNCH_CLIENT_H_INCLUDED
#define [[SERVICE_NAME]]_ASYNCH_CLIENT_H_INCLUDED

#include "[[PROTO_NAME_LOWER]].grpc.pb.h"

#include <grpc/support/log.h>
#include <grpcpp/grpcpp.h>
#include <memory>
#include <string>

namespace ns_[[PROJECT_NAME_LOWER]]
{

class [[SERVICE_NAME]]AsyncClient
{
    public:
    explicit [[SERVICE_NAME]]AsyncClient(std::shared_ptr<grpc::Channel> channel);

    // Assembles the client's payload, sends it and presents the response back
    // from the server.
    std::string Handle[[REQUEST]]Request(const std::string& user);

    private:
    // Out of the passed in Channel comes the stub, stored here, our view of the
    // server's exposed services.
    std::unique_ptr<[[PROTO_NAME_LOWER]]::[[SERVICE_NAME]]Service::Stub> stub_;
};

};  // namespace ns_[[PROJECT_NAME_LOWER]]

#endif  // [[SERVICE_NAME]]_ASYNCH_CLIENT_H_INCLUDED
