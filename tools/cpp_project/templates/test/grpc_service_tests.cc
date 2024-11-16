{{cookiecutter.licence}}

{{cookiecutter.grpc_service_test_hash_includes}}
#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include <iostream>
#include <map>
#include <set>
#include <vector>

using namespace std;
{{cookiecutter.using_namespace}}

class {{cookiecutter.project_name}}{{cookiecutter.proto_name}}ServiceTest : public ::testing::Test
{
    protected:
    void SetUp() override
    {
    }

    void TearDown() override
    {
    }
};

TEST_F({{cookiecutter.project_name}}{{cookiecutter.proto_name}}ServiceTest, {{cookiecutter.service_name}}_{{cookiecutter.request}}_test)
{
    ASSERT_EQ(false, true);
}
