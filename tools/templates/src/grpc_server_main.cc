[[LICENCE]]
#include "[[SERVICE_NAME_LOWER]]_service.h"

#include <csignal>
#include <thread>
#include <iostream>

std::thread server_thread;

auto service = [[SERVICE_NAME]]ServiceImpl{};

void signalHandler(int signum)
{
    service.ShutDown();
}

int main(int argc, char** argv)
{
    signal(SIGTERM, signalHandler);
    server_thread = service.Run(50051);

    server_thread.join();
    return 0;
}
