[[LICENCE]]

#include "[[PROJECT_NAME_TEMPLATE_LOWER]].h"

#include <iostream>
#include <map>
#include <set>
#include <utility>
#include <vector>

namespace ns_[[PROJECT_NAME_TEMPLATE_LOWER]]
{

[[PROJECT_NAME_TEMPLATE]]::[[PROJECT_NAME_TEMPLATE]](size_t sz /* = 0UL */)
: sz_(sz)
{
    // implementation of constructor
}

[[PROJECT_NAME_TEMPLATE]]::[[PROJECT_NAME_TEMPLATE]](const [[PROJECT_NAME_TEMPLATE]] &rhs)
: sz_(rhs.sz_)
{
    // implementation of constructor
}

[[PROJECT_NAME_TEMPLATE]]& [[PROJECT_NAME_TEMPLATE]]::operator =(const [[PROJECT_NAME_TEMPLATE]] &rhs)
{
    if(&rhs != this)
    {
        // implementation of assignment
        this->sz_ = rhs.sz_;
    }

    return *this;
}

[[PROJECT_NAME_TEMPLATE]]::[[PROJECT_NAME_TEMPLATE]]([[PROJECT_NAME_TEMPLATE]] &&rhs) noexcept
: sz_(std::exchange(rhs.sz_, 0UL))     // explicit move of a member of non-class type
//, cls_obj_(std::move(rhs.cls_obj_)), // explicit move of a member of class type
{
    // implementation of constructor
}

[[PROJECT_NAME_TEMPLATE]]& [[PROJECT_NAME_TEMPLATE]]::operator =(const [[PROJECT_NAME_TEMPLATE]] &&rhs)
{
     sz_ = std::move(rhs.sz_);
     return *this;
}

[[PROJECT_NAME_TEMPLATE]]::~[[PROJECT_NAME_TEMPLATE]]()
{
    // implementation of constructor
}

};  // namespace ns_[[PROJECT_NAME_TEMPLATE_LOWER]]

