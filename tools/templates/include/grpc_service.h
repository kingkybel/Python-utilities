[[LICENCE]]

#include "[[PROTO_NAME_LOWER]].grpc.pb.h"

#include <grpcpp/grpcpp.h>
#include <grpcpp/server_context.h>
#include <thread>

/**
 * @brief Logic and data behind the server's behavior.
 */
class [[SERVICE_NAME]]ServiceImpl final : public [[PROTO_NAME_LOWER]]::[[SERVICE_NAME]]Service::Service
{
    public:
    std::thread Run(uint16_t port);
    void        ShutDown();

    private:
    grpc::Status Handle[[REQUEST]]Request(grpc::ServerContext*            context,
                          const [[PROTO_NAME_LOWER]]::[[REQUEST]]RequestMessage* request,
                          [[PROTO_NAME_LOWER]]::[[REQUEST]]ReplyMessage*         reply) override;

    std::unique_ptr<grpc::Server> server_;
    bool                          started_ = false;
};
