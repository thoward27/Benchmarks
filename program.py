import logging
import re
import shlex
import subprocess
from decimal import Decimal
from typing import Tuple, List

events = logging.getLogger(__name__)


class Program:
    """ A single executable program.

    Comparable, save-able, usable objects, that have been built for usability.
    """

    def __init__(self, benchmark: str, name: str, dataset: str, path: str, run: str, compile: str, features: str):
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
        self._features = features
        self.features = {}
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

    def run(self) -> Decimal:
        """ Run the program.
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

    def compile(self, flags: str) -> None:
        """ Compile the program using the given flags.
        """
        result = subprocess.run(
            shlex.split(self._compile.format(flags)),
            shell=False,
            cwd=self.path,
            stdout=subprocess.PIPE
        )
        if not result.returncode == 0:
            events.error("Failed to compile {} with {}".format(repr(self), flags), exc_info=True)
            raise OSError("Failed to compile {}".format(repr(self)))
        return

    def step(self, flags) -> Tuple[List, Decimal, bool, List]:
        self.compile(flags)
        runtime = self.run()
        features = self.features()
        return features, runtime, terminal, info

    @staticmethod
    def _compute_time(group) -> Decimal:
        time = group.split('m')
        time = Decimal(time[0]) * 60 + Decimal(time[1])
        return time