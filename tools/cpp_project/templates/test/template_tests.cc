{{cookiecutter.licence}}

{{cookiecutter.template_includes}}

#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include <iostream>
#include <map>
#include <set>
#include <vector>

using namespace std;
{{cookiecutter.using_namespace}}

class {{cookiecutter.project_name}}_{{cookiecutter.template_class_name}}_Test : public ::testing::Test
{
    protected:
    void SetUp() override
    {
    }

    void TearDown() override
    {
    }
};

// if gdb/interactive debugging of the template is required then #define GDB_DEBUGGING in {{cookiecutter.template_class_name}}.h
#ifndef GDB_DEBUGGING

// Use actual template for production code testing
TEST_F({{cookiecutter.project_name}}_{{cookiecutter.template_class_name}}_Test, {{cookiecutter.template_class_name}}_simple_test)
{
{{cookiecutter.template_args_variables_concrete}}
    {{cookiecutter.template_class_name}}<{{cookiecutter.template_specialisation_concrete}}> {{cookiecutter.template_class_name}}_var{{{cookiecutter.template_variables_in_call}}};
    ASSERT_EQ(false, true);
}

#else

// Use non-templated version for interactive debugging
TEST_F({{cookiecutter.project_name}}_{{cookiecutter.template_class_name}}_Test, {{cookiecutter.template_class_name}}_simple_test)
{
{{cookiecutter.template_args_variables}}
    {{cookiecutter.template_class_name}} {{cookiecutter.template_class_name}}_var{{{cookiecutter.template_variables_in_call}}};
    ASSERT_EQ(false, true);
}

#endif