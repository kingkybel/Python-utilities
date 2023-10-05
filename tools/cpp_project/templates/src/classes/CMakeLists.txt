[[LICENCE]]

####################################################################
## class - libraries
####################################################################

foreach(class_target [[CMAKE_CLASS_LIB_TARGETS]])

    add_library(${class_target}_lib ${class_target}.cc)
    set_property(TARGET ${class_target}_lib PROPERTY OUTPUT_NAME ${class_target})

endforeach()
