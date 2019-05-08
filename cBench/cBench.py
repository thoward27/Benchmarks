""" cBench Benchmark Suite.
"""
import logging
import os
from csv import reader
from subprocess import run, PIPE

import numpy as np
import torch

from Benchmarks.benchmark import Benchmark
from Benchmarks.program import Program

ROOT_DIR = os.path.join(os.path.dirname(__file__), 'source')
CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache')
DATASETS = 5
DATASTART = 1
LOOPS = 75

MEAN = torch.load(os.path.join(os.path.dirname(__file__), 'mean.t'))
STD = torch.load(os.path.join(os.path.dirname(__file__), 'std.t'))

events = logging.getLogger(__name__)


# noinspection PyPep8Naming
class cBench(Benchmark):

    def programs(self):
        self.clean()
        self.prepare()
        events.info("Gathering list of benchmarks.")
        programs = []
        for path, _, _ in os.walk(ROOT_DIR):
            if 'src_work' in path:
                for i in range(DATASTART, DATASETS + 1):
                    programs.append(
                        Program(
                            benchmark="cBench",
                            name=str(path.split('/')[-2]),
                            dataset=str(i),
                            path=path,
                            run="./__run {} {}".format(i, LOOPS),  # 75 == Number of loops to do.
                            compile="make CCC_OPTS='-w {}'",
                        )
                    )
        return programs

    def collect_static(self):
        with open(os.path.join(CACHE_DIR, 'static_features.csv'), 'r') as csvfile:
            r = reader(csvfile)
            for row in r:
                for program in [p for p in self.programs() if p.name == row[0]]:
                    program.features[Features.STATIC] = np.array(row[2:])
                    program.features[Features.HYBRID] = np.append(program.features[Features.HYBRID], np.array(row[2:]))
        return

    @staticmethod
    def clean():
        """ Clean the benchmarks"""
        events.info("Deleting working directories for benchmarks.")
        create_dirs = run('./all__delete_work_dirs', cwd=ROOT_DIR, stdout=PIPE)
        if not create_dirs.returncode == 0:
            events.error(create_dirs.stderr)
            raise OSError("Cannot create working dirs.")

    @staticmethod
    def prepare():
        events.info("Creating working directories for benchmarks.")
        create_dirs = run('./all__create_work_dirs', cwd=ROOT_DIR, stdout=PIPE)
        if not create_dirs.returncode == 0:
            events.error(create_dirs.stderr)
            raise OSError("Cannot create working dirs.")
        return

    @staticmethod
    def test():
        compile_all = run(['./all_compile', 'gcc'], cwd=ROOT_DIR)
        if not compile_all.returncode == 0:
            events.error(compile_all.stderr)
            raise OSError("Cannot compile programs.")
        return


if __name__ == "__main__":
    cBench.prepare()
    cBench.test()
    cBench.clean()
