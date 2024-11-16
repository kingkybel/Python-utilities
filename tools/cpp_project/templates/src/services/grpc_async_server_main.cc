{{cookiecutter.licence}}

#include "{{cookiecutter.service_name_lower}}_async_service.h"

#include <cstdlib>
#include <string>

{{cookiecutter.using_namespace}}

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

    {{cookiecutter.service_name}}AsynchServiceImpl server;
    server.Run(std::atoi(port.c_str()));

    return 0;
}
