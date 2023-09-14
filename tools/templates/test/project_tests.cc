[[LICENCE]]

#include "[[PROJECT_NAME_TEMPLATE_LOWER]].h"

#include <gtest/gtest.h>
#include <iostream>
#include <map>
#include <set>
#include <vector>

using namespace std;

class [[PROJECT_NAME_TEMPLATE]] : public ::testing::Test
{
    protected:
    void SetUp() override
    {
    }

    void TearDown() override
    {
    }
};

TEST_F([[PROJECT_NAME_TEMPLATE]], [[PROJECT_NAME_TEMPLATE_LOWER]]_test)
{
    ASSERT_EQ(false, true);
}
