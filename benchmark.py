""" Abstract Benchmark Class.
"""
import json
from abc import ABC, abstractmethod

ROOT_DIR = ''


class Benchmark(ABC):
    """ Abstract benchmark class, specifying the public API.

    This class represents the requirements for a benchmark suite to be used in this model. Note that
    all methods are not *currently* required, in the current version, only clean() and the various collect()
    methods *must* be defined.
    """

    def __init__(self):
        self.programs = []
        self.clean()
        self.collect_programs()
        self.collect_dynamic()
        self.collect_static()
        self.collect_runtimes()

    def __iter__(self):
        for program in self.programs:
            yield program

    def __len__(self):
        return len(self.programs)

    def __getitem__(self, item):
        return self.programs[item]

    def generate_runtimes(self, save_path, num_loops=5):
        """ Generates runtimes. """
        runtimes = {}
        for i in range(num_loops):
            [p.build_runtimes() for p in self.programs]
            runtimes[i] = [p.to_json() for p in self.programs]
            # Overwrite with every loop, so progress is saved, yet
            # it still adheres with JSON protocol, one large dictionary.
            with open(save_path, 'w') as f:
                json.dump({'runtimes': runtimes}, f)

    @abstractmethod
    def collect_programs(self) -> None:
        """ Builds the Programs List. """
        pass

    @abstractmethod
    def generate_dynamic(self) -> None:
        """ Generate Dynamic Features. """
        pass

    @abstractmethod
    def generate_static(self) -> None:
        """ Generate Static Features. """
        pass

    @abstractmethod
    def collect_runtimes(self) -> None:
        """ Collects the runtimes from cache. """
        pass

    @abstractmethod
    def collect_dynamic(self) -> None:
        """ Collect Previously Generated Dynamic Features. """
        pass

    @abstractmethod
    def collect_static(self) -> None:
        """ Collect Previously Generated Static Features. """
        pass

    @abstractmethod
    def clean(self) -> None:
        """ Clean the Benchmark Folder. """
        pass
