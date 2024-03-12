FROM ubuntu:23.04

RUN apt-get update
RUN apt-get install git python3 python3-pip -y
RUN apt-get update && \
    apt-get -y --no-install-recommends install \
    build-essential g++-13 cmake gdb wget unzip autoconf git libtool \
    ssh curl apt-transport-https ca-certificates libgmp3-dev libmpfr-dev python3 python3-pip python3-venv \
    cmake ninja-build lcov && \
    update-ca-certificates && \
    apt-get clean

RUN update-alternatives --remove-all gcc || true
RUN update-alternatives --remove-all g++ || true
RUN update-alternatives --remove-all c++ || true
RUN update-alternatives --remove-all cpp || true
RUN update-alternatives --remove-all gcc-nm || true
RUN update-alternatives --remove-all gcc-ranlib || true
RUN update-alternatives --remove-all gcc-ar || true

### Install gRPC
ENV GRPC_RELEASE_TAG v1.58.1
RUN echo "== Cloning grpc version ${GRPC_RELEASE_TAG} from github.com ==" && \
    git clone -b ${GRPC_RELEASE_TAG} --recurse-submodules https://github.com/grpc/grpc ${GIT_DIR}/grpc && \
    mkdir -p ${GIT_DIR}/grpc/build && \
    cd ${GIT_DIR}/grpc/build/ && \
    cmake -DCMAKE_CXX_FLAGS=-std=c++20 .. && \
    make -j $(nproc) && \
    make -j $(nproc) install && make clean && ldconfig && \
    cd ${GIT_DIR} && rm -rf grpc

COPY ./bash_aliases_for_docker /root/.bash_aliases
COPY ./requirements.txt /requirements.txt
RUN python3 -m venv /.venv && . /.venv/bin/activate && pip3 install -r /requirements.txt
RUN rm /requirements.txt

