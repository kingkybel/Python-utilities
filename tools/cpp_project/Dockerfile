# Repository:   https://github.com/Python-utilities
# File Name:    tools/cpp_project/Dockerfile
# Description:  Dockerfile for the C++ project maker
#
# Copyright (C) 2024 Dieter J Kybelksties <github@kybelksties.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# @date: 2024-07-13
# @author: Dieter J Kybelksties

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

