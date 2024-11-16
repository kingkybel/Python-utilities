{{cookiecutter.licence}}

#ifndef {{cookiecutter.template_class_name_upper}}_H_INCLUDED
#define {{cookiecutter.template_class_name_upper}}_H_INCLUDED

#include <type_traits>
#include <cstdint>

namespace ns_{{cookiecutter.project_name_lower}}
{

// uncomment the following line if you want to gdb-debug the class (templates are not debuggable)
//#define GDB_DEBUGGING
#ifdef GDB_DEBUGGING
// type definitions of types to use. Modify as required.
{{cookiecutter.template_args_hash_defines}}
#else
template<{{cookiecutter.template_args_def}}>
#endif
class {{cookiecutter.template_class_name}}
{
private:
{{cookiecutter.template_args_members}}

public:
    /**
     * @brief constructor of {{cookiecutter.template_class_name}}
     */
    {{cookiecutter.template_class_name}}({{cookiecutter.template_class_constructor_args}}){{cookiecutter.template_class_constructor_init}}
    {
        // Implement the constructor here
    }
};

};  // namespace ns_{{cookiecutter.project_name_lower}}

#endif  // {{cookiecutter.template_class_name_upper}}_H_INCLUDED

