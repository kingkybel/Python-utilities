import os
import sys
from enum import auto

this_dir = os.path.dirname(os.path.abspath(__file__))
dk_lib_dir = os.path.abspath(f"{this_dir}/../../../Python-utilities")
if not os.path.isdir(dk_lib_dir):
    raise FileNotFoundError(f"Library directory '{dk_lib_dir}' cannot be found")
sys.path.insert(0, dk_lib_dir)

from lib.extended_enum import ExtendedEnum


class GrpcMessagingType(ExtendedEnum):
    DEFAULT = auto()
    ASYNC = auto()
    CALLBACK = auto()

    def __str__(self):
        if self == GrpcMessagingType.ASYNC:
            return "async"
        if self == GrpcMessagingType.CALLBACK:
            return "callback"
        return ""
