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
    grpc::Status Handle[[SERVICE_NAME]]Request(grpc::ServerContext*            context,
                          const [[PROTO_NAME_LOWER]]::[[SERVICE_NAME]]RequestMessage* request,
                          [[PROTO_NAME_LOWER]]::[[SERVICE_NAME]]ReplyMessage*         reply) override;

    std::unique_ptr<grpc::Server> server_;
    bool                          started_ = false;
};
