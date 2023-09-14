[[LICENCE]]

add_executable(run_[[PROJECT_NAME_TEMPLATE_LOWER]]_tests
                run_[[PROJECT_NAME_TEMPLATE_LOWER]]_tests.cc)

target_link_libraries(run_[[PROJECT_NAME_TEMPLATE_LOWER]]_tests gtest gtest_main gmp [[PROJECT_NAME_TEMPLATE_LOWER]])
add_test(NAME [[PROJECT_NAME_TEMPLATE]]_tests COMMAND run_[[PROJECT_NAME_TEMPLATE_LOWER]]_tests)
include(Dart)

