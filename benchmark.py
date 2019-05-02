""" Abstract Benchmark Class.
"""
from abc import ABC, abstractmethod

ROOT_DIR = ''


class Benchmark(ABC):
    """ Abstract benchmark class, specifying the public API.

    This class represents the requirements for a benchmark suite to be used in this model. Note that
    all methods are not *currently* required, in the current version, only clean() and the various collect()
    methods *must* be defined.
    """

    def __iter__(self):
        for program in self.programs():
            yield program

    def __len__(self):
        return len(self.programs())

    def __getitem__(self, item):
        return self.programs()[item]

    @abstractmethod
    def programs(self) -> list:
        """ Builds the Programs List. """
        pass
