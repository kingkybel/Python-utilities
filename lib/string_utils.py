# Repository:   https://github.com/Python-utilities
# File Name:    lib/string_utils.py
# Description:  utilities to perform string manipulations
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
# @date: 2024-07-13
# @author: Dieter J Kybelksties

from __future__ import annotations
import itertools
import keyword
import os
import random
import re
import string
import sys
from colorama import init as colorama_init

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/../../Python-utilities")
if not os.path.isdir(dk_lib_dir):
    raise FileNotFoundError(f"Library directory '{dk_lib_dir}' cannot be found")
sys.path.insert(0, dk_lib_dir)

# pylint: disable=wrong-import-position
from lib.basic_functions import is_empty_string
from lib.exceptions import StringUtilError

colorama_init()

FALSE_STRINGS = ["false", "f", "no", "n", "0"]
TRUE_STRINGS = ["true", "t", "yes", "y", "1"]


def input_value(
    var_name: str,
    help_str: str,
    var_type=str,
    regex_str=None,
    constraint: (range | list) = None
) -> any:
    """
    An interactive prompt to enter a value.
    :param: var_name: The name of the variable to enter. Can be any string.
    :param: help_str: A string describing the desired value-range.
    :param: var_type: the type of the value; one of (int, float, bool, str)
    :param: regex_str: a regular expression that the value must conform to
    :param: constraint: alternatively a list or range of valid values.
    :return: the entered value in the correct type.
    """
    if regex_str and constraint:
        raise ValueError(f"Cannot use both regex '{regex_str}' and constraint '{constraint}'")

    # Default regex for bool if none provided
    if var_type == bool and regex_str is None:
        regex_str = "|".join(FALSE_STRINGS + TRUE_STRINGS)

    # Generate constraint description
    range_str = f"[{constraint.start}..{constraint.stop}]" if isinstance(constraint, range) else ""
    prompt = f"\t{var_name} ({help_str}{range_str}) [{regex_str or '*'}] -> "

    while True:
        # Simulating input for flexibility and testing
        reval = __get_user_input(prompt)  # Replace 'input' with a function for testability

        # Validate against regex
        if regex_str and not re.match(regex_str, reval):
            print("Input does not match the required format. Please try again.")
            continue

        # Validate against constraint
        if constraint:
            if isinstance(constraint, range) and int(reval) not in constraint:
                print(f"Input must be in range {range_str}. Please try again.")
                continue
            if isinstance(constraint, list) and reval not in constraint:
                print(f"Input must be one of {constraint}. Please try again.")
                continue

        # Convert input to the specified type
        try:
            if var_type == bool:
                return reval in TRUE_STRINGS
            return var_type(reval)
        except ValueError:
            print(f"Input could not be converted to {var_type.__name__}. Please try again.")


# Replace 'input' for better testability
def __get_user_input(prompt: str) -> str:
    """Wrapper function to replace input, allowing easier testing."""
    # pylint: disable=bad-builtin
    return input(prompt)


def squeeze_chars(source: str, squeeze_set: str, replace_with: str = ' ') -> str:
    """
    Return a string that is identical to the given source, but with sub-strings containing
    only chars in the squeeze-set replaced by a single replacement char.
    :param: source: the original string.
    :param: squeeze_set: characters to squeeze out.
    :param: replace_with: the replacement char.
    :return: the modified squeezed string.
    """
    if is_empty_string(source):
        return ""
    if is_empty_string(squeeze_set):
        return source
    if len(replace_with) != 1:
        raise StringUtilError(f"replace_with must be 1 char long but is '{replace_with}'")
    # translate all occurrences of chars in squeeze_set to replacement char.
    translater = source.maketrans(squeeze_set, replace_with * len(squeeze_set))
    source = source.translate(translater)

    # compress multiple consecutive occurrences of the replacement char to a single one.
    compress_re = re.compile(f"{replace_with}+")
    source = re.sub(compress_re, replace_with, source)

    # remove replacement char from front ad back
    return source.strip(replace_with)


def remove_control_chars(text: str) -> str:
    """
    Remove ASCII control characters from a string.
    :param: text: the string containing control characters.
    :return: the same string without control characters.
    """
    text = text.encode("ascii", "ignore")
    text = text.decode()
    control_chars = ''.join(chr(c) for c in itertools.chain(range(0x00, 0x20), range(0x7f, 0xa0)))
    control_char_re = re.compile(f'[{re.escape(control_chars)}]')
    return control_char_re.sub(' ', text)


def matches_any(search_string: str, patterns: (str | list[str]) = None) -> bool:
    """
    Check whether the search-string matches any of the given patterns.
    :param: search_string: the string to test.
    :param: patterns: the list of patterns to match against.
    :return: True if any pattern matches, False otherwise.
    """
    if patterns is None:
        return True
    if isinstance(patterns, str):
        patterns = [patterns]
    if any(re.match(pattern=pattern, string=search_string) for pattern in patterns):
        return True
    return False


def replace_all(content: str, replacements: dict[str, str]) -> str:
    for tag in replacements.keys():
        content = content.replace(tag, replacements[tag])
    return content


def normalise_sentence(sentence: str,
                       squeeze_set: str = "\n\t\r *#\\*@><|^&~",
                       expected_non_al_nums: (str | list[str]) = None) -> str:
    """
    Remove most common non-sentence characters, repeated whitespace etc. from a string.
    :param: sentence: the original string containing a sentence.
    :param: squeeze_set: pollutant characters to remove.
    :param: expected_non_al_nums: list of non-alpha-numeric chars that should not to be stripped.
    :return:
    """
    sentence = squeeze_chars(source=sentence,
                             squeeze_set=squeeze_set,
                             replace_with=" ")
    if expected_non_al_nums is None:
        expected_non_al_nums = ['.', '!', '?', ',', ';',
                                '"', "'", '/', '%',
                                '(', ')',
                                '{', '}',
                                '[', ']']
    reval = ""
    for c in sentence:
        if c in expected_non_al_nums:
            reval += f" {c} "
        else:
            reval += c
    reval = squeeze_chars(source=reval, squeeze_set=" ", replace_with=" ")
    if reval.count(' ') < 1:
        reval = ""
    return reval


def get_random_string(length, letters: str = None) -> str:
    """
    Create a random string of given length.
    :param: length: number of characters.
    :param: letters: characters to choose from.
    :return: a random string.
    """
    # choose from all lowercase letter
    if letters is None:
        letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def contains_at_least_n_of(text, specified_words: (str | list[str]) = None, minimum: int = 10) -> bool:
    """
    Check whether a text contains at least `minimum` of the specified words.
    :param: text: the text to check.
    :param: specified_words: a list of words to look for.
    :param: minimum: minimum number of words to be found.
    :return: True if at least `minimum` words are in tex, False otherwise.
    """
    if specified_words is None:
        return False
    if minimum < 1:
        return True
    word_count = sum(1 for word in specified_words if word in text)
    return word_count >= minimum


def is_cpp_id(identifier: str) -> bool:
    # Check if the identifier is not empty
    if not identifier:
        return False

    # Check if the first character is a letter or an underscore
    if not (identifier[0].isalpha() or identifier[0] == '_'):
        return False

    # Check the remaining characters
    for char in identifier[1:]:
        if not (char.isalnum() or char == '_'):
            return False

    # Check if the identifier is not a C++ keyword or reserved word
    if keyword.iskeyword(identifier):
        return False

    # If all checks pass, it's a valid C++ identifier
    return True


def split_text_into_chunks(text: str, max_chunk_size: int) -> list[str]:
    """
    Split a text into smaller texts and without splitting words or sentences.
    :param: text: the text to split.
    :param: max_chunk_size: the approximate size of the resulting chunks.
    :return: a list of smaller texts.
    """
    # Split the text into sentences
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)

    # Initialize variables
    current_chunk = ""
    chunks = []

    for sentence in sentences:
        # Check if adding the sentence to the current chunk exceeds the max_chunk_size
        if len(current_chunk) + len(sentence) <= max_chunk_size:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk)
            current_chunk = sentence + " "

    # Add the last chunk
    chunks.append(current_chunk)

    return chunks


def is_utf8_ascii(text: str) -> bool:
    try:
        text.encode(encoding='utf-8').decode('ascii')
        return True
    except UnicodeDecodeError:
        return False


def is_roman_numeral(text: str) -> bool:
    """
    Check whether a number is a Roman numeral.
    :param: text: the text to check.
    :return: True, if the text is a Roman numeral, False otherwise.
    """
    text = text.upper().strip()

    # Regular expression pattern to match Roman numerals
    pattern = r'^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$'

    # Use regex to match the pattern
    if re.match(pattern, text):
        return True
    return False


def roman_to_integer(text: str) -> int:
    if not is_roman_numeral(text):
        return -1

    roman_numerals = {
        'I': 1, 'V': 5, 'X': 10, 'L': 50,
        'C': 100, 'D': 500, 'M': 1000
    }

    total = 0
    prev_value = 0

    for char in text[::-1]:
        value = roman_numerals[char]

        if value < prev_value:
            total -= value
        else:
            total += value

        prev_value = value

    return total
