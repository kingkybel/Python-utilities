[[LICENCE]]

add_executable(run_[[PROJECT_NAME_LOWER]]_tests
                run_[[PROJECT_NAME_LOWER]]_tests.cc)
[[TEST_EXE_LINK_LIBRARIES]]
add_test(NAME [[PROJECT_NAME]]_tests COMMAND run_[[PROJECT_NAME_LOWER]]_tests)
include(Dart)

