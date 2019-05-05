import numpy as np
import logging
import re
import shlex
import subprocess
from decimal import Decimal
from glob import glob
from os.path import abspath, join, dirname
from typing import Tuple, List, Union

from source.config import FLAGS

events = logging.getLogger(__name__)

PIN = abspath(join(dirname(__file__), 'pin', 'pin'))
MICA = abspath(join(dirname(__file__), 'pin', 'source', 'tools', 'MICA', 'obj-intel64', 'mica.so'))


class Program:
    """ A single executable program.

    Comparable, save-able, usable objects, that have been built for usability.
    """

    def __init__(self, benchmark: str, name: str, dataset: str, path: str, run: str, compile: str):
        """ Constructs a new program. All fields are required. "Benchmark + name + dataset" must be unique.

        :param benchmark: The benchmark the program belongs to (group ID)
        :param name: The name of the program
        :param dataset: The dataset to use. (Allows copies of a program to be instantiated)
        """
        self.benchmark = benchmark
        self.name = name
        self.dataset = dataset
        self.path = path
        self._compile = compile
        self._run = run

        # Constants
        self.observation_space = 101

        # Internal state
        self.flags = []
        self.runtimes = []
        return

    def __repr__(self) -> str:
        """ Unique representation of the program. """
        return "{}_{}_{}".format(self.benchmark, self.name, self.dataset)

    def __str__(self) -> str:
        """ A non-unique representation of the program. """
        return "{}_{}".format(self.benchmark, self.name)

    def __eq__(self, other) -> bool:
        """ Equality based on str() non-unique representation.

        Essentially this tests whether or not two programs are the same,
        expect for their dataset.
        """
        return str(self) == str(other)

    def __lt__(self, other) -> bool:
        """ This allows sorting by name, using the rep() unique representation. """
        return repr(self) < repr(other)

    def reset(self):
        self.compile([])
        self.runtimes = [self.run()]
        return self.features()

    def compile(self, flags: list) -> None:
        """ Compile the program using the given flags.
        """
        result = subprocess.run(
            shlex.split(self._compile.format(' '.join(self.flags))),
            shell=False,
            cwd=self.path,
            stdout=subprocess.PIPE
        )

        if not result.returncode == 0:
            events.error("Failed to compile {} with {}".format(repr(self), flags))
            raise OSError("Failed to compile {}".format(repr(self)))
        return

    def run(self) -> float:
        """ Run the program, return it's runtime.
        """
        result = subprocess.run(
            shlex.split(self._run),
            shell=False,
            cwd=self.path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if not result.returncode == 0:
            events.error("Failed to run " + repr(self))

        result = result.stderr.decode('utf-8')
        m = re.search(
            r'\nreal\t(?P<real>\d+m\d+.\d+)s\nuser\t(?P<user>\d+m\d+.\d+)s\nsys.(?P<sys>\d+m\d.\d+)s',
            result
        )

        # real_time = self._compute_time(m.group('real'))
        user_time = self._compute_time(m.group('user'))
        syst_time = self._compute_time(m.group('sys'))

        return user_time + syst_time

    def features(self) -> np.ndarray:
        """ Extract features from program.
        """
        result = subprocess.run(
            shlex.split("{} -t {} -- {}".format(PIN, MICA, self._run)),
            shell=False,
            cwd=self.path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if not result.returncode == 0:
            events.error("Failed to extract features from {}".format(repr(self)))
            raise OSError("Failed to extract features from {}".format(repr(self)))

        features = []
        for file in sorted(glob(self.path + '/*pin.out')):
            with open(file, 'r') as f:
                features.extend(f.readline().split())
        return np.array([int(f) for f in features])

    def step(self, flag: Union[str, int, list]) -> Tuple[np.ndarray, Decimal, bool, dict]:
        """ Add the given flag to the current compilation sequence, compile, and run. """
        if type(flag) is int:
            try:
                flag = FLAGS[flag]
            except IndexError:
                return np.array([]), (self.runtimes[0] - self.runtimes[-1]) / self.runtimes[0], True, {}

        # Compile and run with the new flag.
        self.flags.append(flag)
        self.compile(self.flags)
        self.runtimes.append(self.run())

        # Gather features
        features = self.features()

        # Reward is measured as the ratio of base time to current, clips rewards to [-1, 1]
        reward = (self.runtimes[0] - self.runtimes[-1]) / self.runtimes[0]

        # Game ends after trying 10 flags.
        end = len(self.flags) > 10

        # No debugging info, yet!
        info = {}

        return features, reward, end, info

    @staticmethod
    def _compute_time(group) -> float:
        time = group.split('m')
        time = float(time[0]) * 60 + float(time[1])
        return time


class Programs:
    """ A simple wrapper over a list of programs, providing a `filter` method. """

    def __init__(self):
        from Benchmarks.cBench import cBench
        self.programs = list(cBench().programs())

    def __iter__(self):
        for p in self.programs:
            yield p

    def __getitem__(self, item):
        return self.programs[item]

    def filter(self, program) -> Tuple[List[Program], List[Program]]:
        train, test = [], []
        [train.append(p) if p != program else test.append(p) for p in self.programs]
        return train, test
