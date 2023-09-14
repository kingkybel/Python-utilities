[[LICENCE]]

#ifndef [[PROJECT_NAME_TEMPLATE_UPPER]]_H_INCLUDED
#define [[PROJECT_NAME_TEMPLATE_UPPER]]_H_INCLUDED

#include <iostream>
#include <map>
#include <set>
#include <vector>

namespace ns_[[PROJECT_NAME_TEMPLATE_LOWER]]
{

class [[PROJECT_NAME_TEMPLATE]]
{
public:
    explicit [[PROJECT_NAME_TEMPLATE]](size_t sz = 1UL);
    [[PROJECT_NAME_TEMPLATE]](const [[PROJECT_NAME_TEMPLATE]] &rhs);
    [[PROJECT_NAME_TEMPLATE]]& operator =(const [[PROJECT_NAME_TEMPLATE]] &rhs);
    [[PROJECT_NAME_TEMPLATE]]([[PROJECT_NAME_TEMPLATE]] &&rhs) noexcept;
    [[PROJECT_NAME_TEMPLATE]]& operator =(const [[PROJECT_NAME_TEMPLATE]] &&rhs);
    virtual ~[[PROJECT_NAME_TEMPLATE]]();

    // Add your public interface here

private:
    // Add your private members here
    size_t sz_ = 1UL;
};

};  // namespace ns_[[PROJECT_NAME_TEMPLATE_LOWER]]

#endif // [[PROJECT_NAME_TEMPLATE_UPPER]]_H_INCLUDED
