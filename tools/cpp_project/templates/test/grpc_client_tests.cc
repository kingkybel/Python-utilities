[[LICENCE]]

[[GRPC_CLIENT_TEST_HASH_INCLUDES]]
#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include <iostream>
#include <map>
#include <set>
#include <vector>

using namespace std;
[[USING_NAMESPACE]]

class [[PROJECT_NAME]][[PROTO_NAME]]ClientTest : public ::testing::Test
{
    protected:
    void SetUp() override
    {
    }

    void TearDown() override
    {
    }
};

TEST_F([[PROJECT_NAME]][[PROTO_NAME]]ClientTest, [[SERVICE_NAME]]_[[REQUEST]]_test)
{
    ASSERT_EQ(false, true);
}
