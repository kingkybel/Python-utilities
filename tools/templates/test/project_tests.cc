[[LICENCE]]

[[CLASS_INCLUDES]]
#include <gtest/gtest.h>
#include <iostream>
#include <map>
#include <set>
#include <vector>

using namespace std;
[[USING_NAMESPACE]]

class [[PROJECT_NAME]] : public ::testing::Test
{
    protected:
    void SetUp() override
    {
    }

    void TearDown() override
    {
    }
};

TEST_F([[PROJECT_NAME]], [[PROJECT_NAME_LOWER]]_test)
{
    ASSERT_EQ(false, true);
}
