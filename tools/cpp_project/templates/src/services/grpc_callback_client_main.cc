[[LICENCE]]

#include "[[PROTO_NAME_LOWER]].grpc.pb.h"
#include "[[SERVICE_NAME_LOWER]]_callback_client.h"

#include <condition_variable>
#include <grpcpp/grpcpp.h>
#include <iostream>
#include <memory>
#include <mutex>
#include <string>

using grpc::Channel;
using grpc::ClientContext;
using grpc::Status;

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
    // We indicate that the channel isn't authenticated (use of InsecureChannelCredentials()).
    [[SERVICE_NAME]]CallbackClient [[SERVICE_NAME_LOWER]](grpc::CreateChannel(target_str, grpc::InsecureChannelCredentials()));
    std::string answer_string("some answer to the request");
    std::string reply = [[SERVICE_NAME_LOWER]].Handle[[REQUEST]]Request(answer_string);
    std::cout << "Answer to [[REQUEST]] received: " << reply << std::endl;

    return 0;
}
