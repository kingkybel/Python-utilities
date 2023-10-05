[[LICENCE]]

#ifndef [[TEMPLATE_CLASS_NAME_UPPER]]_H_INCLUDED
#define [[TEMPLATE_CLASS_NAME_UPPER]]_H_INCLUDED

namespace ns_[[PROJECT_NAME_LOWER]]
{

template<[[TEMPLATE_ARGS_DEF]]>
#define GDB_DEBUGGING
#ifdef GDB_DEBUGGING
[[TEMPLATE_ARGS_HASH_DEFINES]]
#else
template<[[TEMPLATE_ARGS_DEF]]>
#endif
class [[TEMPLATE_CLASS_NAME]]
{
[[TEMPLATE_ARGS_MEMBERS]]

public:
    // constructor associates whole range of K with val by inserting (K_min, val)
    // into the map

    [[TEMPLATE_CLASS_NAME]]([[TEMPLATE_CLASS_CONSTRUCTOR_ARGS]])
    [[TEMPLATE_CLASS_CONSTRUCTOR_INIT]]
    {
        // Implement the constructor here
    }
};

};  // namespace ns_[[PROJECT_NAME_LOWER]]

#endif [[TEMPLATE_CLASS_NAME_UPPER]]_H_INCLUDED

