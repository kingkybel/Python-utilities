#!/usr/bin/env python3
import os
import argparse
from pygccxml import parser, declarations


def parse_arguments():
    arg_parser = argparse.ArgumentParser(description='Generate Google Test suites for C++ project.')
    arg_parser.add_argument('--project-folder', type=str, required=True, help='Path to the C++ project folder')
    return arg_parser.parse_args()


def find_cpp_files(directory):
    cpp_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.h'):
                cpp_files.append(os.path.join(root, file))
    return cpp_files


def extract_public_functions(class_decl):
    public_functions = []
    for member in class_decl.get_members():
        if isinstance(member, declarations.member_function_t) and member.access_type == 'public':
            public_functions.append(member)
    return public_functions


def generate_gtest_suite(class_name, public_functions):
    suite = f"TEST({class_name}Test, {class_name}Functionality) {{\n"
    for func in public_functions:
        suite += f"    // TODO: Write test case for {func.name}\n"
    suite += "}\n"
    return suite


def main():
    args = parse_arguments()
    project_folder = args.project_folder

    include_folder = os.path.join(project_folder, 'include')
    src_folder = os.path.join(project_folder, 'src')

    include_files = find_cpp_files(include_folder)
    src_files = find_cpp_files(src_folder)

    all_files = include_files + src_files

    if not all_files:
        print('No C++ source files found.')
        return

    castxml_path = '/usr/bin/castxml'
    if not os.path.exists(castxml_path):
        print(f"Error: castxml not found at {castxml_path}")
        return

    print(f"Using castxml at {castxml_path}")
    print(include_folder)

    # Configure the C++ parser
    cxx_config = parser.xml_generator_configuration_t(
        xml_generator_path=castxml_path,
        xml_generator='castxml',
        include_paths=[include_folder],
        cflags='-std=c++17'
    )

    decls = []
    for file in all_files:
        try:
            parsed = parser.parse([file], cxx_config)
            decls += parsed.declarations
        except Exception as e:
            print(f"Error parsing {file}: {e}")

    gtest_suites = ""
    for decl in decls:
        if isinstance(decl, declarations.class_t):
            class_decl = decl
            public_functions = extract_public_functions(class_decl)
            gtest_suite = generate_gtest_suite(class_decl.name, public_functions)
            gtest_suites += gtest_suite + "\n"

    if gtest_suites:
        output_file = os.path.join(project_folder, 'test_generated.cpp')
        with open(output_file, 'w', encoding="utf-8") as f:
            f.write("#include <gtest/gtest.h>\n")
            f.write("#include <iostream>\n")
            f.write("#include <string>\n")
            for file in include_files:
                header = os.path.relpath(file, project_folder)
                f.write(f'#include "{header}"\n')
            f.write("\n")
            f.write(gtest_suites)

        print(f"Google Test suite generated in '{output_file}'.")
    else:
        print("No public functions found to generate tests for.")


if __name__ == "__main__":
    main()
