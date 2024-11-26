# Repository:   https://github.com/Python-utilities
# File Name:    lib/json_object.py
# Description:  wrapper for json that has a more comfortable way to set and get keys/values
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
import json
import os
import os.path
import sys
from os import PathLike

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/../../Python-utilities")
if not os.path.isdir(dk_lib_dir):
    raise FileNotFoundError(f"Library directory '{dk_lib_dir}' cannot be found")
sys.path.insert(0, dk_lib_dir)

# pylint: disable=wrong-import-position
from lib.basic_functions import is_empty_string
from lib.exceptions import JsonGeneralError, JsonError, JsonKeyStringRequired, JsonIndexRequired, JsonValueMismatch
from lib.file_system_object import find
from lib.json_key_path import JsonKeyPath, JsonIndexKey, JsonStringKey
from lib.logger import log_command
from lib.string_utils import squeeze_chars, get_random_string


class JsonObject:
    NOT_FOUND = None

    def __init__(self,
                 json_str: (str | list) = None,
                 filename: (str | PathLike) = None,
                 json_obj: (list | dict) = None):
        self.json_: dict | list | None = None
        if json_str is not None:
            if squeeze_chars(source=json_str, squeeze_set="\n\t\r ", replace_with=" ") == "":
                json_str = "{}"
            self.from_string(json_str)
        elif not is_empty_string(filename):
            self.from_file(filename)
        elif json_obj is not None:
            self.from_object(json_obj)
        else:
            self.from_string("{}")

    def __str__(self):
        return json.dumps(self.json_)

    def to_str(self, indent: int = 2) -> str:
        """
        Output as a string.
        :param indent: number of indentations to use
        :return: this object as a string
        """
        return json.dumps(self.json_, indent=indent)

    def from_string(self, json_str: str):
        """
        Create a JsonObject from a string.
        :param json_str: the json string
        """
        if is_empty_string(json_str):
            json_str = "{}"
        self.json_ = json.loads(json_str)

    @classmethod
    def convert_sets_to_vectors(cls, obj: object) -> object:
        """
        Recursively convert sets to vectors.
        :param obj: the object to convert
        :return: a copy of obj that can be used as a json-object
        """
        if isinstance(obj, set):
            # If it's a set, convert it to a list after doing the same recursively.
            return [JsonObject.convert_sets_to_vectors(item) for item in obj]
        if isinstance(obj, dict):
            # If it's a dictionary, recursively process its values
            return {key: JsonObject.convert_sets_to_vectors(value) for key, value in obj.items()}
        if isinstance(obj, list):
            # If it's a list, recursively process its elements
            return [JsonObject.convert_sets_to_vectors(item) for item in obj]
        if isinstance(obj, tuple):
            # If it's a tuple, recursively process its elements and convert to list
            return [JsonObject.convert_sets_to_vectors(item) for item in obj]
        # elif isinstance(obj, object):
        #     # If it's a custom object, recursively process its attributes
        #     for attr_name in dir(obj):
        #         attr_value = getattr(obj, attr_name)
        #         setattr(obj, attr_name, JsonObject.convert_sets_to_vectors(attr_value))
        if not isinstance(obj, (bool, int, float, str)):
            return str(obj)
        return obj

    def from_object(self, obj: object):
        """
        Create a JsonObject from an object.
        :param obj: the object to initialise this JsonObject with
        """
        obj = JsonObject.convert_sets_to_vectors(obj)
        self.from_string(json.dumps(obj))

    def from_file(self, filename: (str | PathLike), encoding: str = "utf-8"):
        """
        Initialize this JsonObject from a json-file.
        :param filename: json-file
        :param encoding: encoding of the file
        """
        if not os.path.isfile(filename):
            raise JsonGeneralError(f"Cannot load json from file '{filename}': file does not exist")
        with open(filename, encoding=encoding) as file:
            try:
                self.json_ = json.load(file)
            except json.JSONDecodeError:
                file.close()
                raise
            file.close()

    def to_file(self, filename: (str | PathLike), indent: int = 4, encoding: str = "utf-8", dryrun: bool = False):
        """
        Write this JsonObject to a json-file.
        :param filename: the output filename
        :param indent: number of indentation chars to use
        :param encoding: encoding of the file
        :param dryrun: whether to write the file, or only go through the motions
        """
        log_command(f"JsonObject.to_file({filename})", dryrun=dryrun)
        if not dryrun:
            with open(filename, 'w', encoding=encoding) as file:
                json.dump(self.json_, file, indent=indent)

    def empty(self, obj: object = None) -> bool:
        """
        Check whether the given object is empty.
        :param obj: object to check
        :return: True if the given object is empty (empty list/dict or None), false otherwise
        """
        if obj is None:
            return not bool(self.json_) or self.json_ == {} or self.json_ == []
        return not bool(obj) or obj == {} or obj == []

    def is_list(self, obj: object = None) -> bool:
        """
        Check whether the given object is a list.
        :param obj: the object to check
        :return: True, if obj is a list, False otherwise
        """
        if obj is None:
            return isinstance(self.json_, list)
        return isinstance(obj, list)

    def is_dict(self, obj: object = None) -> bool:
        """
        Check whether the given object is a dict.
        :param obj:  the object to check
        :return:  True, if obj is a dict, False otherwise
        """
        if obj is None:
            return isinstance(self.json_, dict)
        return isinstance(obj, dict)

    def size(self, obj: object = None) -> int:
        """
        Size of the given object, if it is a list.
        :param obj: object to check
        :return: size of the given object, if it is a list, 0 otherwise
        """
        if obj is None:
            if self.is_list():
                return len(self.json_)
            return 0
        if self.is_list(obj):
            return len(self.json_)
        return 0

    @classmethod
    def assert_json_files_valid(cls, paths: (str | PathLike | list[str | PathLike])) -> tuple[
        int, list[str | PathLike]]:
        """ | PathLike
        Assert that the given paths are valid and that the files are a json-files.
        :param paths: file-paths to check
        :return: tuple of an error code and a list of invalid paths/files
        """
        json_files = find(paths=paths, file_type_filter="f", name_patterns=r".*\.json")
        failed_files = []
        reval = 0
        for json_file in json_files:
            try:
                JsonObject(filename=json_file)
            except JsonError:
                failed_files.append(json_file)
                reval = -1
        return reval, failed_files

    def key_exists(self, keys: (str | list[str])):
        """
        Check if a key exists.
        :param keys: path to a key
        :return: True if key exists, False otherwise
        """
        not_exist_str = "KEY-DOES-NOT-EXIST-" + get_random_string(47, "0123456789ABCDEF")
        if self.get(keys, default=not_exist_str) == not_exist_str:
            return False
        return True

    def get(self, keys: (str | list[str] | None) = None, default: (bool | int | float | str | list | dict) = None):
        """
        Get the value of the given key-path. If a default is defined, and it's possible to default a key, then the
        default value will be returned when the key is missing.This happens when this object and the key are structurally
        compatible, but the path is too long and the object can no longer be iterated.
        Example: object = {"key1":{"Key2":[]} and key is key1/key2/[0]/key3
        :param keys: key-path
        :param default: default-value
        :return: the value of the given key, or the default if key is compatible
        :raise JsonKeyStringRequired, JsonIndexRequired, JsonGeneralError: on compatibility problems
        """
        if keys is None:
            return self.json_
        if isinstance(keys, str):
            keys = JsonKeyPath(keys).key_list()

        iterator = self.json_
        for key_index, key in enumerate(keys):
            self.__assert_iterator_and_key_are_compatible(default, iterator, key, key_index, keys)

            is_last_key = (key_index >= len(keys) - 1)

            try:
                if isinstance(key, JsonIndexKey):
                    index = JsonObject.__get_absolute_index(key_index=key_index, keys=keys, json_obj=iterator,
                                                            for_insert=False)

                    # if we are at a path-end we return:
                    # - for indices greater/equal the length of the list: the default if defined, error otherwise
                    # - the value at the index, if index is in range
                    if is_last_key:
                        if int(index) >= len(iterator):
                            if default is not None:
                                return default
                            raise JsonIndexRequired(key_index=key_index, keys=keys, json_obj=iterator)
                        return list(iterator)[int(index)]

                    # We're not at a path-end, so if the index is in range, then we advance the iterator
                    if int(index) < len(iterator):
                        iterator = list(iterator)[int(index)]
                    else:
                        # otherwise if a default is defined return it, otherwise error
                        if default is not None:
                            return default
                        raise JsonIndexRequired(key_index=key_index, keys=keys, json_obj=iterator)

                elif isinstance(key, JsonStringKey):
                    if isinstance(iterator, list):
                        raise JsonIndexRequired(key_index=key_index, keys=keys, json_obj=iterator)
                    if not isinstance(iterator, dict):
                        raise JsonKeyStringRequired(key_index=key_index, keys=keys, json_obj=iterator)
                    # if we are at the last key then either
                    # - return the value, if it exists
                    # - otherwise if default is defined return the default, error otherwise
                    if is_last_key:
                        if iterator is not None and dict(iterator).get(key.get()) is not None:
                            return dict(iterator).get(key.get())
                        if default is not None:
                            return default
                        raise JsonKeyStringRequired(key_index=key_index, keys=keys, json_obj=iterator)
                    # it's not a list and not the last key, so it must be a dict, so advance the iterator
                    iterator = dict(iterator)[key.get()]
            except JsonKeyStringRequired:
                raise
            except KeyError as k:
                if default is not None:
                    return default
                error_msg = f"Cannot get key number '{key_index}' in json {iterator}. {k}"
                raise JsonGeneralError(message=error_msg) from k
        return iterator

    @classmethod
    def __assert_iterator_and_key_are_compatible(cls, default, iterator, key, key_index, keys):
        # check the key is compatible with the container
        if iterator is None:
            raise JsonGeneralError(f"get({keys}, {default}) and key_index {key_index}({key}) iterator is None")
        if isinstance(iterator, list) and not isinstance(key, JsonIndexKey):
            raise JsonIndexRequired(key_index=key_index, keys=keys, json_obj=iterator)
        if isinstance(iterator, dict) and not isinstance(key, JsonStringKey):
            raise JsonKeyStringRequired(key_index=key_index, keys=keys, json_obj=iterator)

    def set(self,
            keys: (str | list[str] | JsonKeyPath),
            value: (bool | int | float | str | list | dict),
            force: bool = False,
            dryrun: bool = False):
        """
        Set a value in this JsonObject
        :param keys: path to a key
        :param value: value to set
        :param force: if True, then force the path to exist, before the value is set
        :param dryrun: if set to false then just go through the motions
        :raise JsonKeyStringRequired, JsonGeneralError: on compatibility problems
        """
        if value is None:
            raise JsonGeneralError("Cannot set value that is None")
        if not isinstance(value, (bool, int, float, str, dict, list)):
            raise JsonGeneralError(f"Unsupported json-value type {type(value)}")
        path = JsonKeyPath(keys)
        keys = path.key_list()

        if not dryrun:
            self.__change_root_or_raise(keys=keys, force=force)
            if force:
                self.__make_forced_path(keys=keys, value=value)
            self.__set_impl(keys=keys, value=value, force=force)

    @classmethod
    def __get_absolute_index(cls, key_index: int, keys, json_obj, for_insert: bool):
        if not isinstance(json_obj, list):
            raise JsonIndexRequired(key_index=key_index, keys=keys, json_obj=json_obj)
        cur_key = keys[key_index]
        if cur_key.is_start_symbol:
            index = 0
        elif cur_key.is_end_symbol:
            index = len(json_obj) - 1
            if for_insert:
                index += 1
        else:
            index = cur_key.index
        return index

    def __change_root_or_raise(self, keys: JsonKeyPath, force: bool):
        if isinstance(keys[0], JsonIndexKey) and not isinstance(self.json_, list):
            if force:
                self.json_ = []
            else:
                raise JsonIndexRequired(key_index=0, keys=keys.list_of_keys, json_obj=self.json_)
        elif isinstance(keys[0], JsonStringKey) and not isinstance(self.json_, dict):
            if force:
                # we need to change the variable type here
                # pylint: disable=redefined-variable-type
                self.json_ = {}
            else:
                raise JsonKeyStringRequired(key_index=0, keys=keys.list_of_keys, json_obj=self.json_)

    def __make_forced_path(self, keys: JsonKeyPath, value: bool | int | float | str | list | dict):
        # make the root element compatible
        self.__change_root_or_raise(keys, force=True)
        iterator = self.json_
        for key_index, key in enumerate(keys):
            is_last_key = (key_index >= len(keys) - 1)

            if not is_last_key:
                blank_object = []
                if isinstance(keys[key_index + 1], JsonStringKey):
                    blank_object = {}
                if isinstance(iterator, list):
                    abs_index = self.__get_absolute_index(key_index, keys, iterator, for_insert=True)
                    self.__extend_list(blank_object, iterator, key_index, keys)
                    iterator = iterator[abs_index]
                elif isinstance(iterator, dict):
                    if iterator.get(key.get()) is None:
                        iterator[key.get()] = blank_object
                    iterator = iterator[key.get()]
            else:
                blank_object = type(value)()
                if isinstance(iterator, list):
                    self.__extend_list(blank_object, iterator, key_index, keys)
                elif isinstance(iterator, dict):
                    if iterator.get(key.get()) is None:
                        iterator[key.get()] = blank_object

    def __extend_list(self, blank_object, iterator, key_index, keys):
        index_key = keys[key_index]
        if index_key.is_start_symbol:
            iterator.insert(0, blank_object)
        elif index_key.is_end_symbol:
            iterator.append(blank_object)
        else:
            abs_index = self.__get_absolute_index(key_index, keys, iterator, for_insert=True)
            for _ in range(abs_index - len(iterator) + 1):
                iterator.append(blank_object)

    def __set_impl(self, keys: JsonKeyPath, value: (bool | int | float | str | list | dict), force: bool):
        iterator = self.json_

        for key_index, key in enumerate(keys):
            is_last_key = (key_index >= len(keys) - 1)
            try:
                if isinstance(key, JsonIndexKey):
                    if not isinstance(iterator, list):
                        raise JsonIndexRequired(key_index=key_index, keys=keys.list_of_keys, json_obj=self.json_)
                    if key.is_start_symbol:
                        index = 0
                    elif key.is_end_symbol:
                        index = len(iterator) - 1
                    else:
                        index = key.index

                    if is_last_key:
                        if isinstance(iterator[int(index)], type(value)):
                            iterator[int(index)] = value
                        else:
                            raise JsonValueMismatch(orig_value=iterator[int(index)], new_value=value)
                    iterator = iterator[int(index)]
                else:
                    if isinstance(iterator, list):
                        raise JsonKeyStringRequired(key_index=key_index, keys=keys.list_of_keys, json_obj=self.json_)
                    if is_last_key:
                        if isinstance(iterator[key.get()], type(value)) or force:
                            iterator[key.get()] = value
                        else:
                            raise JsonValueMismatch(orig_value=iterator[key.get()], new_value=value)
                    iterator = iterator[key.get()]
            except JsonKeyStringRequired:
                raise
            except JsonIndexRequired:
                raise
            except KeyError as k:
                error_msg = f"Cannot create/overwrite key number '{key_index}' '{key}' - not path-end"
                raise JsonGeneralError(message=error_msg) from k
        return self.json_
