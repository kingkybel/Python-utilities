[[LICENCE]]

#ifndef [[CLASS_NAME_UPPER]]_H_INCLUDED
#define [[CLASS_NAME_UPPER]]_H_INCLUDED

#include <iostream>
#include <map>
#include <set>
#include <vector>

namespace ns_[[PROJECT_NAME_LOWER]]
{

class [[CLASS_NAME]]
{
public:
    explicit [[CLASS_NAME]](size_t sz = 1UL);
    [[CLASS_NAME]](const [[CLASS_NAME]] &rhs);
    [[CLASS_NAME]]& operator =(const [[CLASS_NAME]] &rhs);
    [[CLASS_NAME]]([[CLASS_NAME]] &&rhs) noexcept;
    [[CLASS_NAME]]& operator =(const [[CLASS_NAME]] &&rhs);
    virtual ~[[CLASS_NAME]]();

    // Add your public interface here

private:
    // Add your private members here
    size_t sz_ = 1UL;
};

};  // namespace ns_[[PROJECT_NAME_LOWER]]

#endif // [[CLASS_NAME_UPPER]]_H_INCLUDED
