{{cookiecutter.licence}}

####################################################################
## class - libraries
####################################################################

foreach(class_target {{cookiecutter.cmake_class_lib_targets}})

    add_library(${class_target}_lib ${class_target}.cc)
    set_property(TARGET ${class_target}_lib PROPERTY OUTPUT_NAME ${class_target})

endforeach()
