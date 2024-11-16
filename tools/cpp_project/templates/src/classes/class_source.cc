{{cookiecutter.licence}}

#include "{{cookiecutter.class_name_lower}}.h"

#include <iostream>
#include <map>
#include <set>
#include <utility>
#include <vector>

namespace ns_{{cookiecutter.project_name_lower}}
{

{{cookiecutter.class_name}}::{{cookiecutter.class_name}}(size_t sz /* = 0UL */)
: sz_(sz)
{
    // implementation of (default-)constructor
}

{{cookiecutter.class_name}}::{{cookiecutter.class_name}}(const {{cookiecutter.class_name}} &rhs)
: sz_(rhs.sz_)
{
    // implementation of copy-constructor
}

{{cookiecutter.class_name}}& {{cookiecutter.class_name}}::operator =(const {{cookiecutter.class_name}} &rhs)
{
    if(&rhs != this)
    {
        // implementation of assignment
        this->sz_ = rhs.sz_;
    }

    return *this;
}

{{cookiecutter.class_name}}::{{cookiecutter.class_name}}({{cookiecutter.class_name}} &&rhs) noexcept
: sz_(std::exchange(rhs.sz_, 0UL))     // explicit move of a member of non-class type
//, cls_obj_(std::move(rhs.cls_obj_)), // explicit move of a member of class type
{
    // implementation of move-constructor
}

{{cookiecutter.class_name}}& {{cookiecutter.class_name}}::operator =(const {{cookiecutter.class_name}} &&rhs)
{
     sz_ = std::move(rhs.sz_);
     return *this;
}

{{cookiecutter.class_name}}::~{{cookiecutter.class_name}}()
{
    // implementation of destructor
}

};  // namespace ns_{{cookiecutter.project_name_lower}}

