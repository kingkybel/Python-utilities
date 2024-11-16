{{cookiecutter.licence}}
#include "{{cookiecutter.service_name_lower}}_service.h"

#include <csignal>
#include <cstdlib>
#include <string>
#include <thread>
#include <iostream>

{{cookiecutter.using_namespace}}

std::thread server_thread;

auto service = {{cookiecutter.service_name}}ServiceImpl{};

void signalHandler(int signum)
{
    service.ShutDown();
}

int main(int argc, char** argv)
{
    // default to serving on 0.0.0.0:{{cookiecutter.port}}
    std::string port = "{{cookiecutter.port}}";
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
