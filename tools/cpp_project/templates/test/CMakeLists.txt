{{cookiecutter.licence}}

add_executable(run_{{cookiecutter.project_name_lower}}_tests
               run_{{cookiecutter.project_name_lower}}_tests.cc
{{cookiecutter.test_source_files}})

{{cookiecutter.cmake_test_include_dirs}}
{{cookiecutter.cmake_test_exe_link_libraries}}

add_test(NAME {{cookiecutter.project_name_lower}}_tests COMMAND run_{{cookiecutter.project_name_lower}}_tests)
include(Dart)

