[[LICENCE]]

[[CLASS_HASH_INCLUDE]]
#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include <iostream>
#include <map>
#include <set>
#include <vector>

using namespace std;
[[USING_NAMESPACE]]

class [[PROJECT_NAME]]_[[CLASS_NAME]]_Test : public ::testing::Test
{
    protected:
    void SetUp() override
    {
    }

    void TearDown() override
    {
    }
};

TEST_F([[PROJECT_NAME]]_[[CLASS_NAME]]_Test, [[CLASS_NAME]]_simple_test)
{
    ASSERT_EQ(false, true);
}
