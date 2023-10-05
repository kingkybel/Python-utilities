[[LICENCE]]

#include "[[SERVICE_NAME_LOWER]]_client.h"
#include "[[PROTO_NAME_LOWER]].grpc.pb.h"

#include <grpcpp/grpcpp.h>
#include <iostream>
#include <memory>
#include <string>
#include <thread>

[[USING_NAMESPACE]]

int main(int argc, char** argv)
{
    // default target to localhost:[[PORT]]
    std::string server = "localhost";
    std::string port = "[[PORT]]";
    for(int count = 0; count < argc; count++)
    {
        if(std::string(argv[count]) == "--server" || std::string(argv[count]) == "-s")
        {
            count++;
            server = argv[count];
        }
        if(std::string(argv[count]) == "--port" || std::string(argv[count]) == "-p")
        {
            count++;
            port = argv[count];
        }
    }

    // Instantiate the client. It requires a channel, out of which the actual RPCs
    // are created. This channel models a connection to an endpoint specified by <server>:<port>
    std::string target_str = server + ":" + port;
    [[SERVICE_NAME]]Client [[SERVICE_NAME_LOWER]](grpc::CreateChannel(target_str, grpc::InsecureChannelCredentials()));
    std::string   request_str{"request some service"};
    for(size_t i = 0; i < 5; i++)
    {
        std::string reply = [[SERVICE_NAME_LOWER]].Handle[[REQUEST]]Request(request_str);
        std::cout << "Answer to [[REQUEST]] received: " << reply << std::endl;
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }

    return 0;
}
