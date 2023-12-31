[[LICENCE]]

#ifndef [[SERVICE_NAME_UPPER]]_CALLBACK_SERVICE_H_INCLUDED
#define [[SERVICE_NAME_UPPER]]_CALLBACK_SERVICE_H_INCLUDED

#include "[[PROTO_NAME_LOWER]].grpc.pb.h"

#include <absl/flags/flag.h>
#include <absl/flags/parse.h>
#include <absl/strings/str_format.h>
#include <grpcpp/ext/proto_server_reflection_plugin.h>
#include <grpcpp/grpcpp.h>
#include <grpcpp/health_check_service_interface.h>
#include <iostream>
#include <memory>
#include <string>

namespace ns_[[PROJECT_NAME_LOWER]]
{

// Logic and data behind the server's behavior.
class [[SERVICE_NAME]]CallbackServiceImpl final : public [[PROTO_NAME_LOWER]]::[[SERVICE_NAME]]Service::CallbackService
{
    grpc::ServerUnaryReactor* Handle[[REQUEST]]Request(
        grpc::CallbackServerContext* context,
        const [[PROTO_NAME_LOWER]]::[[REQUEST]]RequestMessage* request,
        [[PROTO_NAME_LOWER]]::[[REQUEST]]ReplyMessage* reply) override;
    public:
    static void RunServer(uint16_t port);
};

};  // namespace ns_[[PROJECT_NAME_LOWER]]

#endif  // [[SERVICE_NAME_UPPER]]_CALLBACK_SERVICE_H_INCLUDED
