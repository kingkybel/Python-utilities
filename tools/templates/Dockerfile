[[LICENCE]]

FROM ubuntu:latest

# Install build essentials and CMake
RUN apt-get update && apt-get install -y build-essential cmake

# Install Google Test dependencies
RUN apt-get install -y libgtest-dev

# Build and install Google Test
WORKDIR /usr/src/gtest
RUN cmake CMakeLists.txt
RUN make
RUN cp lib/*.a /usr/lib

# Clean up
WORKDIR /
RUN rm -rf /usr/src/gtest

# Copy project files and build the project
WORKDIR /app
COPY . .
RUN rm -rf build && mkdir -p build && cd build && cmake .. && make

ENTRYPOINT ["bash"]
