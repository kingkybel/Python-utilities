[[LICENCE]]

####################################################################
## gRPC - libraries
####################################################################

file(MAKE_DIRECTORY ${PROTO_CPP_SRC_DIR})

[[CMAKE_GENERATE_CPP_FROM_PROTOS]]

##############################################
# Put all gRPC/proto functions into a library
add_library([[PROJECT_NAME_LOWER]]_grpc_proto STATIC ${PROTO_FILES_HEADERS} ${PROTO_FILES_SOURCES})
target_link_libraries([[PROJECT_NAME_LOWER]]_grpc_proto PUBLIC
  ${_REFLECTION}
  ${_GRPC_GRPCPP}
  ${_PROTOBUF_LIBPROTOBUF})

foreach(service_target [[CMAKE_GRPC_SERVICES]])

  ###############################
  # server functionality library
  add_library("${service_target}_service_lib" "${service_target}_service.cc")
  set_property(TARGET "${service_target}_service_lib" PROPERTY OUTPUT_NAME "${service_target}_service")
  target_include_directories("${service_target}_service_lib" PUBLIC ${PROTO_CPP_SRC_DIR})
  target_link_libraries("${service_target}_service_lib"
    [[PROJECT_NAME_LOWER]]_grpc_proto
    "${service_target}_server")

  ###############################
  # client functionality library
  add_library("${service_target}_client_lib" "${service_target}_client.cc")
  set_property(TARGET "${service_target}_client_lib" PROPERTY OUTPUT_NAME "${service_target}_client")
  target_include_directories("${service_target}_client_lib" PUBLIC ${PROTO_CPP_SRC_DIR})
  target_link_libraries("${service_target}_client_lib"
    [[PROJECT_NAME_LOWER]]_grpc_proto)

endforeach()
