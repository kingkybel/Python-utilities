import os
import sys

this_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = f"{this_dir}/.."
sys.path.insert(0, parent_dir)

from lib.overrides import overrides
from threading import Thread


class ReturningThread(Thread):
    def __init__(self,
                 group=None,
                 target=None,
                 name=None,
                 args=(),
                 kwargs=None,
                 daemon: bool = False):
        if kwargs is None:
            kwargs = dict()
        Thread.__init__(self=self,
                        group=group,
                        target=target,
                        name=name,
                        args=args,
                        kwargs=kwargs,
                        daemon=daemon)
        self.__return__ = None

    @overrides(Thread)
    def run(self):
        if self._target is not None:
            self.__return__ = self._target(*self._args, **self._kwargs)

    @overrides(Thread)
    def join(self, *args) -> object:
        Thread.join(self, *args)
        return self.__return__
