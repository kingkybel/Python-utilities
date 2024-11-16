{{cookiecutter.licence}}

FROM ubuntu:latest

COPY ./bash_aliases_for_docker /tmp
RUN cat /tmp/bash_aliases_for_docker > ~/.bash_aliases
RUN rm /tmp/bash_aliases_for_docker

# Copy project files and build the project
WORKDIR /app

COPY ./build/bin/{{cookiecutter.project_name_lower}} .

ENTRYPOINT ["bash"]
