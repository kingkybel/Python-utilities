{{cookiecutter.licence}}

#ifndef {{cookiecutter.class_name_upper}}_H_INCLUDED
#define {{cookiecutter.class_name_upper}}_H_INCLUDED

#include <iostream>
#include <map>
#include <set>
#include <vector>

namespace ns_{{cookiecutter.project_name_lower}}
{

class {{cookiecutter.class_name}}
{
public:
    explicit {{cookiecutter.class_name}}(size_t sz = 1UL);
    {{cookiecutter.class_name}}(const {{cookiecutter.class_name}} &rhs);
    {{cookiecutter.class_name}}& operator =(const {{cookiecutter.class_name}} &rhs);
    {{cookiecutter.class_name}}({{cookiecutter.class_name}} &&rhs) noexcept;
    {{cookiecutter.class_name}}& operator =(const {{cookiecutter.class_name}} &&rhs);
    virtual ~{{cookiecutter.class_name}}();

    // Add your public interface here

private:
    // Add your private members here
    size_t sz_ = 1UL;
};

};  // namespace ns_{{cookiecutter.project_name_lower}}

#endif // {{cookiecutter.class_name_upper}}_H_INCLUDED
