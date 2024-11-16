{{cookiecutter.licence}}

#ifndef {{cookiecutter.service_name_upper}}_SERVICE_H_INCLUDED
#define {{cookiecutter.service_name_upper}}_SERVICE_H_INCLUDED

#include "{{cookiecutter.proto_name_lower}}.grpc.pb.h"

#include <grpcpp/grpcpp.h>
#include <grpcpp/server_context.h>
#include <thread>

namespace ns_{{cookiecutter.project_name_lower}}
{

/**
 * @brief Logic and data behind the server's behavior.
 */
class {{cookiecutter.service_name}}ServiceImpl final : public {{cookiecutter.proto_name_lower}}::{{cookiecutter.service_name}}Service::Service
{
    public:
    std::thread Run(uint16_t port);
    void        ShutDown();

    private:
    grpc::Status Handle{{cookiecutter.request}}Request(grpc::ServerContext* context,
                          const {{cookiecutter.proto_name_lower}}::{{cookiecutter.request}}RequestMessage* request,
                          {{cookiecutter.proto_name_lower}}::{{cookiecutter.request}}ReplyMessage* reply) override;

    std::unique_ptr<grpc::Server> server_;
    bool                          started_ = false;
};

};  // namespace ns_{{cookiecutter.project_name_lower}}

#endif  // {{cookiecutter.service_name_upper}}_SERVICE_H_INCLUDED
