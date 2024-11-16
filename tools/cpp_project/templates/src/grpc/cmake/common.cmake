{{cookiecutter.licence}}

cmake_minimum_required(VERSION 3.8)

if(MSVC)
  add_definitions(-D_WIN32_WINNT=0x600)
endif()

find_package(Threads REQUIRED)

if(GRPC_AS_SUBMODULE)
  add_subdirectory(../../.. ${CMAKE_CURRENT_BINARY_DIR}/grpc EXCLUDE_FROM_ALL)
  message(STATUS "Using gRPC via add_subdirectory.")

  set(_PROTOBUF_LIBPROTOBUF libprotobuf)
  set(_REFLECTION grpc++_reflection)
  if(CMAKE_CROSSCOMPILING)
    find_program(_PROTOBUF_PROTOC protoc)
  else()
    set(_PROTOBUF_PROTOC $<TARGET_FILE:protobuf::protoc>)
  endif()
  set(_GRPC_GRPCPP grpc++)
  if(CMAKE_CROSSCOMPILING)
    find_program(_GRPC_CPP_PLUGIN_EXECUTABLE grpc_cpp_plugin)
  else()
    set(_GRPC_CPP_PLUGIN_EXECUTABLE $<TARGET_FILE:grpc_cpp_plugin>)
  endif()
elseif(GRPC_FETCHCONTENT)
  message(STATUS "Using gRPC via add_subdirectory (FetchContent).")
  include(FetchContent)
  FetchContent_Declare(
    grpc
    GIT_REPOSITORY https://github.com/grpc/grpc.git
    GIT_TAG vGRPC_TAG_VERSION_OF_YOUR_CHOICE)
  FetchContent_MakeAvailable(grpc)

  set(_PROTOBUF_LIBPROTOBUF libprotobuf)
  set(_REFLECTION grpc++_reflection)
  set(_PROTOBUF_PROTOC $<TARGET_FILE:protoc>)
  set(_GRPC_GRPCPP grpc++)
  if(CMAKE_CROSSCOMPILING)
    find_program(_GRPC_CPP_PLUGIN_EXECUTABLE grpc_cpp_plugin)
  else()
    set(_GRPC_CPP_PLUGIN_EXECUTABLE $<TARGET_FILE:grpc_cpp_plugin>)
  endif()
else()
  option(protobuf_MODULE_COMPATIBLE TRUE)
  find_package(Protobuf CONFIG REQUIRED)
  message(STATUS "Using protobuf ${Protobuf_VERSION}")

  set(_PROTOBUF_LIBPROTOBUF protobuf::libprotobuf)
  set(_REFLECTION gRPC::grpc++_reflection)
  if(CMAKE_CROSSCOMPILING)
    find_program(_PROTOBUF_PROTOC protoc)
  else()
    set(_PROTOBUF_PROTOC $<TARGET_FILE:protobuf::protoc>)
  endif()

  find_package(gRPC CONFIG REQUIRED)
  message(STATUS "Using gRPC ${gRPC_VERSION}")

  set(_GRPC_GRPCPP gRPC::grpc++)
  if(CMAKE_CROSSCOMPILING)
    find_program(_GRPC_CPP_PLUGIN_EXECUTABLE grpc_cpp_plugin)
  else()
    set(_GRPC_CPP_PLUGIN_EXECUTABLE $<TARGET_FILE:gRPC::grpc_cpp_plugin>)
  endif()
endif()

####
# Generate sources from proto-files
# @param PROTOS_DIR: directory where *.proto-file is located
# @param CPP_TARGET_PATH: path where generated *.h and *.cc files will be written
# @param ...: names of the protos without path and extension
####
function(create_cpp_from_protos PROTO_DIR TARGET_DIR)
    # Check if the protoc executable is available
    find_program(PROTOC_EXECUTABLE protoc)
    if(NOT PROTOC_EXECUTABLE)
        message(FATAL_ERROR "protoc compiler not found. Please install Protocol Buffers.")
    endif()
    # Check if the protobuf CMake package is available
    find_package(protobuf CONFIG REQUIRED)

    # Check if the gRPC C++ generator plugin is available
    find_program(GRPC_CPP_PLUGIN grpc_cpp_plugin)
    if(NOT GRPC_CPP_PLUGIN)
        message(FATAL_ERROR "grpc_cpp_plugin not found. Please install grpc_cpp_plugin.")
    endif()
    # Check if the gRPC CMake package is available
    find_package(gRPC CONFIG REQUIRED)

    # Loop through the remaining function arguments (proto names)
    foreach(proto_name IN LISTS ARGN)
        string(TOLOWER ${proto_name} proto_name)
        set(proto_file "${PROTO_DIR}/${proto_name}.proto")

        # Generate C++ header and source files from the proto file
        set(proto_output_h "${TARGET_DIR}/${proto_name}.pb.h")
        set(proto_output_cc "${TARGET_DIR}/${proto_name}.pb.cc")

        add_custom_command(
            OUTPUT "${proto_output_h}" "${proto_output_cc}"
            COMMAND "${PROTOC_EXECUTABLE}"
            ARGS "--cpp_out=${TARGET_DIR}"
            "--proto_path=${PROTO_DIR}"
            "${proto_file}"
            DEPENDS "${proto_file}"
            WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
            COMMENT "Generating C++ files from ${proto_file}"
        )

        # Generate gRPC files from the proto file
        set(grpc_output_h "${TARGET_DIR}/${proto_name}.grpc.pb.h")
        set(grpc_output_cc "${TARGET_DIR}/${proto_name}.grpc.pb.cc")

        add_custom_command(
            OUTPUT "${grpc_output_h}" "${grpc_output_cc}"
            COMMAND "${PROTOC_EXECUTABLE}"
            ARGS "--grpc_out=${TARGET_DIR}"
            "--plugin=protoc-gen-grpc=${GRPC_CPP_PLUGIN}"
            "--proto_path=${PROTO_DIR}"
            "${proto_file}"
            DEPENDS "${proto_file}"
            WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
            COMMENT "Generating gRPC files from ${proto_file}"
        )

        list(APPEND proto_headers "${proto_output_h}" "${grpc_output_h}")
        list(APPEND proto_sources "${proto_output_cc}" "${grpc_output_cc}")
    endforeach()

    # Return the generated C++ and gRPC files as lists
    set(PROTO_FILES_HEADERS ${proto_headers} PARENT_SCOPE)
    set(PROTO_FILES_SOURCES ${proto_sources} PARENT_SCOPE)
endfunction()
