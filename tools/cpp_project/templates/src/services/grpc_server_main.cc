[[LICENCE]]
#include "[[SERVICE_NAME_LOWER]]_service.h"

#include <csignal>
#include <cstdlib>
#include <string>
#include <thread>
#include <iostream>

[[USING_NAMESPACE]]

std::thread server_thread;

auto service = [[SERVICE_NAME]]ServiceImpl{};

void signalHandler(int signum)
{
    service.ShutDown();
}

int main(int argc, char** argv)
{
    // default to serving on 0.0.0.0:[[PORT]]
    std::string port = "[[PORT]]";
    for(int count = 0; count < argc; count++)
    {
        if(std::string(argv[count]) == "--port" || std::string(argv[count]) == "-p")
        {
            count++;
            port = argv[count];
        }
    }

    signal(SIGTERM, signalHandler);
    server_thread = service.Run(std::atoi(port.c_str()));

    server_thread.join();
    return 0;
}
