# Repository:   https://github.com/Python-utilities
# File Name:    tools/bulk_replacements/replace_in_files.py
# Description:  bulk-replacing strings in files with regular-expression matching
#
# Copyright (C) 2024 Dieter J Kybelksties <github@kybelksties.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# @date: 2024-09-06
# @author: Dieter J Kybelksties

import argparse
import re
import sys
import os
import pandas as pd

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/../../../Python-utilities")
if not os.path.isdir(dk_lib_dir):
    raise FileNotFoundError(f"Library directory '{dk_lib_dir}' cannot be found")
sys.path.insert(0, dk_lib_dir)

# pylint: disable=wrong-import-position
from lib.file_system_object import find, FileSystemObjectType
from lib.logger import error, log_info


def load_replacements(file_path):
    """Load the replacements from a CSV or Excel file."""
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    # Ensure the file has the correct number of columns
    if df.shape[1] < 2:
        raise ValueError(
            "The replacement file must have at least 2 columns (Pattern, Replacement, Optional: PatternIsRegex, ReplacementIsRegex).")

    # Fill the boolean columns with False if not present
    if df.shape[1] == 2:
        df['PatternIsRegex'] = False
        df['ReplacementIsRegex'] = False
    elif df.shape[1] == 3:
        df['ReplacementIsRegex'] = False

    return df


def perform_replacements(text, replacements):
    """Perform the replacements using either regular expressions or string replacements."""
    temp_placeholder = '___PLACEHOLDER___'

    for _, row in replacements.iterrows():
        pattern = row[0]
        replacement = row[1]
        if not isinstance(replacement, str):
            error(error_code=-1, message=f"Row '{row}' ")
        pattern_is_regex = bool(row[2])
        replacement_is_regex = bool(row[3])

        # If the pattern is a regular expression, use re.sub
        if pattern_is_regex:
            # Perform the replacement using regex
            if replacement_is_regex:
                # Handle swapping by using a placeholder to avoid interfering replacements
                text = re.sub(pattern, temp_placeholder, text)
                text = re.sub(temp_placeholder, replacement, text)
            else:
                text = re.sub(pattern, replacement, text)
        # If it's a simple string replacement, we use Python's built-in replace function
        elif replacement_is_regex:
            # Swap with regex-based replacement but plain string match
            text = text.replace(pattern, temp_placeholder)
            text = re.sub(temp_placeholder, replacement, text)
        else:
            # Plain string replacement
            text = text.replace(pattern, replacement)

    return text


def main():
    parser = argparse.ArgumentParser(description='Perform regex/string replacements in a file.')
    parser.add_argument('--replacements', '-r', required=True, help='CSV or Excel file with replacements.')
    parser.add_argument('--template-directory', '-t', required=True,
                        help='Directory where to find files with templates.')

    args = parser.parse_args()

    # Load the replacement patterns from the file
    replacements = load_replacements(args.replacements)

    files = find(paths=args.template_directory, file_type_filter=FileSystemObjectType.FILE, exclude_patterns=[R".*/__pycache__/.*"])

    for file in files:
        log_info(message=f"Processing {file}")
        # Read the file where replacements need to be performed
        with open(file, 'r', encoding="utf-8") as f:
            content = f.read()

        # Perform the replacements
        modified_content = perform_replacements(content, replacements)

        # Save the modified content back to the file (or alternatively output it)
        with open(file, 'w', encoding="utf-8") as f:
            f.write(modified_content)

        print(f"Replacements applied to {file} successfully.")


if __name__ == "__main__":
    main()
