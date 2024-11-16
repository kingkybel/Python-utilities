{{cookiecutter.licence}}

#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include <iostream>
#include <map>
#include <set>
#include <vector>

using namespace std;
{{cookiecutter.using_namespace}}

class {{cookiecutter.project_name}}_Test : public ::testing::Test
{
    protected:
    void SetUp() override
    {
    }

    void TearDown() override
    {
    }
};

TEST_F({{cookiecutter.project_name}}_Test, simple_test)
{
    ASSERT_EQ(false, true);
}
