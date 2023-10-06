[[LICENCE]]

[[TEMPLATE_INCLUDES]]

#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include <iostream>
#include <map>
#include <set>
#include <vector>

using namespace std;
[[USING_NAMESPACE]]

class [[PROJECT_NAME]]_[[TEMPLATE_CLASS_NAME]]_Test : public ::testing::Test
{
    protected:
    void SetUp() override
    {
    }

    void TearDown() override
    {
    }
};

// if gdb/interactive debugging of the template is required then #define GDB_DEBUGGING in [[TEMPLATE_CLASS_NAME]].h
#ifndef GDB_DEBUGGING

// Use actual template for production code testing
TEST_F([[PROJECT_NAME]]_[[TEMPLATE_CLASS_NAME]]_Test, [[TEMPLATE_CLASS_NAME]]_simple_test)
{
[[TEMPLATE_ARGS_VARIABLES_CONCRETE]]
    [[TEMPLATE_CLASS_NAME]]<[[TEMPLATE_SPECIALISATION_CONCRETE]]> [[TEMPLATE_CLASS_NAME]]_var{[[TEMPLATE_VARIABLES_IN_CALL]]};
    ASSERT_EQ(false, true);
}

#else

// Use non-templated version for interactive debugging
TEST_F([[PROJECT_NAME]]_[[TEMPLATE_CLASS_NAME]]_Test, [[TEMPLATE_CLASS_NAME]]_simple_test)
{
[[TEMPLATE_ARGS_VARIABLES]]
    [[TEMPLATE_CLASS_NAME]] [[TEMPLATE_CLASS_NAME]]_var{[[TEMPLATE_VARIABLES_IN_CALL]]};
    ASSERT_EQ(false, true);
}

#endif