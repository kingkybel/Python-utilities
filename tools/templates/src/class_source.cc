[[LICENCE]]

#include "[[CLASS_NAME_LOWER]].h"

#include <iostream>
#include <map>
#include <set>
#include <utility>
#include <vector>

namespace ns_[[PROJECT_NAME_LOWER]]
{

[[CLASS_NAME]]::[[CLASS_NAME]](size_t sz /* = 0UL */)
: sz_(sz)
{
    // implementation of (default-)constructor
}

[[CLASS_NAME]]::[[CLASS_NAME]](const [[CLASS_NAME]] &rhs)
: sz_(rhs.sz_)
{
    // implementation of copy-constructor
}

[[CLASS_NAME]]& [[CLASS_NAME]]::operator =(const [[CLASS_NAME]] &rhs)
{
    if(&rhs != this)
    {
        // implementation of assignment
        this->sz_ = rhs.sz_;
    }

    return *this;
}

[[CLASS_NAME]]::[[CLASS_NAME]]([[CLASS_NAME]] &&rhs) noexcept
: sz_(std::exchange(rhs.sz_, 0UL))     // explicit move of a member of non-class type
//, cls_obj_(std::move(rhs.cls_obj_)), // explicit move of a member of class type
{
    // implementation of move-constructor
}

[[CLASS_NAME]]& [[CLASS_NAME]]::operator =(const [[CLASS_NAME]] &&rhs)
{
     sz_ = std::move(rhs.sz_);
     return *this;
}

[[CLASS_NAME]]::~[[CLASS_NAME]]()
{
    // implementation of destructor
}

};  // namespace ns_[[PROJECT_NAME_LOWER]]

