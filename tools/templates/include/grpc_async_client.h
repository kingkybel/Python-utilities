[[LICENCE]]

#include "[[PROTO_NAME_LOWER]].grpc.pb.h"

#include <grpc/support/log.h>
#include <grpcpp/grpcpp.h>
#include <memory>
#include <string>

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
