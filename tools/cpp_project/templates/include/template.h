[[LICENCE]]

#ifndef [[TEMPLATE_CLASS_NAME_UPPER]]_H_INCLUDED
#define [[TEMPLATE_CLASS_NAME_UPPER]]_H_INCLUDED

#include <type_traits>
#include <cstdint>

namespace ns_[[PROJECT_NAME_LOWER]]
{

// uncomment the following line if you want to gdb-debug the class (templates are not debuggable)
//#define GDB_DEBUGGING
#ifdef GDB_DEBUGGING
// type definitions of types to use. Modify as required.
[[TEMPLATE_ARGS_HASH_DEFINES]]
#else
template<[[TEMPLATE_ARGS_DEF]]>
#endif
class [[TEMPLATE_CLASS_NAME]]
{
private:
[[TEMPLATE_ARGS_MEMBERS]]

public:
    /**
     * @brief constructor of [[TEMPLATE_CLASS_NAME]]
     */
    [[TEMPLATE_CLASS_NAME]]([[TEMPLATE_CLASS_CONSTRUCTOR_ARGS]])[[TEMPLATE_CLASS_CONSTRUCTOR_INIT]]
    {
        // Implement the constructor here
    }
};

};  // namespace ns_[[PROJECT_NAME_LOWER]]

#endif  // [[TEMPLATE_CLASS_NAME_UPPER]]_H_INCLUDED

