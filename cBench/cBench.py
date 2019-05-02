""" cBench Benchmark Suite.

TODO: Remove cBench files from project, add copying functionality to setup.py
"""
import logging
import os
from csv import reader
from decimal import Decimal
from subprocess import run, PIPE

import numpy as np

from Benchmarks.benchmark import Benchmark
from Benchmarks.program import Program
from source.config import *

ROOT_DIR = os.path.join(os.path.dirname(__file__), 'cBench')
CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache')
DATASETS = 5
DATASTART = 1
LOOPS = 75


events = logging.getLogger(__name__)


# noinspection PyPep8Naming
class cBench(Benchmark):

    def collect_programs(self):
        events.info("Gathering list of benchmarks.")
        for path, _, _ in os.walk(ROOT_DIR):
            if 'src_work' in path:
                for i in range(DATASTART, DATASETS + 1):
                    self.programs.append(
                        Program(
                            benchmark="cBench",
                            name=str(path.split('/')[-2]),
                            dataset=str(i),
                            path=path,
                            run="./__run {} {}".format(i, LOOPS),  # 75 == Number of loops to do.
                            compile="make CCC_OPTS='-w {}'",
                            features="{} -t {} -- ./__run {} {}".format(PIN, MICA, i, LOOPS)
                        )
                    )
        return

    def generate_runtimes(self, **kwargs):
        super().generate_runtimes(
            save_path='./benchmarks/cBench/cache/runtimes.json',
            num_loops=5
        )
        return

    def generate_dynamic(self):
        # TODO
        for program in self.programs:
            results = run(
                "{} -t {} -- ./__run 1".format(PIN, MICA),
                cwd=program['path'],
                shell=True,
                stdout=PIPE,
                stderr=PIPE)
            if not results.returncode == 0:
                events.error(results.stdout)
                events.error("Feature collection failed")

        events.info("running table generation.")
        run("sh tableGen.sh", cwd=ROOT_DIR, shell=True, stdout=PIPE)
        raise NotImplemented

    def generate_static(self):
        # TODO
        super().generate_static()
        return

    def collect_runtimes(self):
        with open(os.path.join(CACHE_DIR, 'runtimes.csv'), 'r') as csvfile:
            r = reader(csvfile)
            for row in r:
                for program in [p for p in self.programs if p.name == row[0] and p.dataset == row[1]]:
                    program.runtimes = [round(Decimal(r), 3) for r in row[2:]]

    def collect_dynamic(self):
        with open(os.path.join(CACHE_DIR, 'dynamic_features.csv'), 'r') as csvfile:
            r = reader(csvfile)
            for row in r:
                for program in [p for p in self.programs if p.name == row[0] and p.dataset == row[1]]:
                    program.features[Features.DYNAMIC] = np.array(row[2:])
                    program.features[Features.HYBRID] = np.append(program.features[Features.HYBRID], np.array(row[2:]))
        return

    def collect_static(self):
        with open(os.path.join(CACHE_DIR, 'static_features.csv'), 'r') as csvfile:
            r = reader(csvfile)
            for row in r:
                for program in [p for p in self.programs if p.name == row[0]]:
                    program.features[Features.STATIC] = np.array(row[2:])
                    program.features[Features.HYBRID] = np.append(program.features[Features.HYBRID], np.array(row[2:]))
        return

    def clean(self):
        """ Clean the benchmarks"""
        events.info("Deleting working directories for benchmarks.")
        create_dirs = run('./all__delete_work_dirs', cwd=ROOT_DIR, stdout=PIPE)
        if not create_dirs.returncode == 0:
            events.error(create_dirs.stderr)
            raise OSError("Cannot create working dirs.")

        events.info("Creating working directories for benchmarks.")
        create_dirs = run('./all__create_work_dirs', cwd=ROOT_DIR, stdout=PIPE)
        if not create_dirs.returncode == 0:
            events.error(create_dirs.stderr)
            raise OSError("Cannot create working dirs.")
        return

    def test(self):
        compile_all = run(['./all_compile', 'gcc'], cwd=ROOT_DIR, stdout=PIPE)
        if not compile_all.returncode == 0:
            events.error(compile_all.stderr)
            raise OSError("Cannot compile programs.")
        return
