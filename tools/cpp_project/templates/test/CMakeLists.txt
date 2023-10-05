[[LICENCE]]

add_executable(run_[[PROJECT_NAME_LOWER]]_tests
               run_[[PROJECT_NAME_LOWER]]_tests.cc
[[TEST_SOURCE_FILES]])

[[CMAKE_TEST_INCLUDE_DIRS]]
target_link_libraries(run_[[PROJECT_NAME_LOWER]]_tests gtest gtest_main)
[[CMAKE_TEST_EXE_LINK_LIBRARIES]]

add_test(NAME [[PROJECT_NAME_LOWER]]_tests COMMAND run_[[PROJECT_NAME_LOWER]]_tests)
include(Dart)

