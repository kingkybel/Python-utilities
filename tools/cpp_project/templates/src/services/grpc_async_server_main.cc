[[LICENCE]]

#include "[[SERVICE_NAME_LOWER]]_async_service.h"

#include <cstdlib>
#include <string>

[[USING_NAMESPACE]]

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

    [[SERVICE_NAME]]AsynchServiceImpl server;
    server.Run(std::atoi(port.c_str()));

    return 0;
}
