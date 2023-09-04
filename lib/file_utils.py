import os.path
from os import PathLike

from lib.basic_functions import valid_absolute_path, is_empty_string
from lib.file_system_object import mkdir
from lib.logger import log_command, error
from lib.string_utils import squeeze_chars


def generate_incremental_filename(filename: (str | PathLike)) -> str:
    """
    Generate a filename with incremental numbers if file exists.
    :param filename: The basic path of the file, may contain spaces, which will be replaced by underscores.
    :return: A unique filename with an incremental number.
    """
    filename = squeeze_chars(source=str(filename), squeeze_set="\n\t\r ", replace_with="_")
    base_filename = os.path.basename(filename)
    base_filename = str(base_filename)
    extension = ""
    ext_index = base_filename.rfind(".")
    if ext_index > -1:
        extension = base_filename[ext_index:]
        base_filename = base_filename[:ext_index]
    dir_path = os.path.dirname(filename)
    full_path = f"{dir_path}/{base_filename}{extension}"

    # If the file already exists, append an incremental number
    counter = 1
    while os.path.exists(full_path):
        full_path = f"{dir_path}/{base_filename}_{counter}{extension}"
        counter += 1

    return valid_absolute_path(full_path)


def read_file(filename: (str | PathLike), dryrun: bool = False) -> str:
    """
    Read a text file and return the contents as string.
    :param filename: filename to read.
    :param dryrun: if set to True, then do not execute but just output a comment describing the command.
    :return: the contents of the file as string.
    """
    content = ""
    log_command(f"read_file {filename}", extra_comment=f"Python command in {__file__}", dryrun=dryrun)
    if not dryrun:
        with open(filename, "r") as file:
            content = file.read()
    return content


def write_file(filename: (str | PathLike),
               content: (str | list[str]) = None,
               mode: str = "w",
               dryrun: bool = False):
    """
    Write the given content to the given filename.
    :param filename: filename to read.
    :param content: string or list of strings to write.
    :param mode: one of 'a': append, 'w': write
    :param dryrun: if set to True, then do not execute but just output a comment describing the command.
    :return:
    """
    filename = valid_absolute_path(filename)
    log_command(f"write_file({filename}, mode='{mode}')",
                extra_comment=f"Python command in {__file__}",
                dryrun=dryrun)
    if mode not in ["a", "w"]:
        error(f"Cannot write file {filename}. Unknown mode '{mode}'. Choose from 'a' and 'W'")
    if not dryrun:
        mkdir(os.path.dirname(filename))
        if is_empty_string(content):
            content = ""
        if isinstance(content, str):
            content = [content]
        if len(content) > 0:
            last = content[len(content) - 1]
            # add line feeds to lines 0 .. len(contents) - 2
            content = [l + "\n" for l in content[:len(content) - 1]]
            # no line-feed at the last line
            content.append(last)
        with open(filename, mode) as file:
            file.writelines(content)


def parse_env_file(filename: (str | PathLike), dryrun: bool = False) -> dict[str, str]:
    """
    Simple *.env file parser.
    Ignores:
        – comments (Everything after '#')
        – empty or whitespace-only lines, ignoring comments
    Creates dictionary of key/value pairs given as
    MY_KEY1  = My value 1
    MY_KEY_2 = 234
    :param filename: path to the .env file
    :param dryrun: if set to True, then do not execute but just output a comment describing the command.
    :return: dictionary of key/value pairs.
    """
    content = read_file(filename=filename, dryrun=dryrun)
    key_val_dict = dict()
    if not dryrun:
        lines = content.split("\n")
        for line in lines:
            key_val = squeeze_chars(source=(line.split("#")[0]), squeeze_set="\t ").split("=")
            key = key_val[0]
            if not is_empty_string(key):
                if len(key_val) == 1:
                    val = ""
                else:
                    val = key_val[1]
                key_val_dict[key] = val
    return key_val_dict
