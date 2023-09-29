[[LICENCE]]

#include "[[SERVICE_NAME_LOWER]]_client.h"
#include "[[PROTO_NAME_LOWER]].grpc.pb.h"

#include <grpcpp/grpcpp.h>
#include <iostream>
#include <memory>
#include <string>
#include <thread>

int main(int argc, char** argv)
{
    [[SERVICE_NAME]]Client [[SERVICE_NAME_LOWER]](grpc::CreateChannel("[[SERVICE_NAME_LOWER]]_server:[[PORT]]", grpc::InsecureChannelCredentials()));
    std::string   request_str{"request some service"};
    for(size_t i = 0; i < 5; i++)
    {
        std::string reply = [[SERVICE_NAME_LOWER]].Handle[[REQUEST]]Request(request_str);
        std::cout << "[[SERVICE_NAME]]Service received: " << reply << std::endl;
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }

    return 0;
}
