import numpy as np
from decimal import Decimal
from unittest import TestCase

from Benchmarks.cBench import *


class TestcBench(TestCase):
    def test_build(self):
        programs = cBench().programs()
        # There are 28 programs.
        self.assertEqual(len({p.name for p in programs}), 27)
        # Each with 5 datasets.
        self.assertEqual(len(programs), 135)
        return

    def test_compile(self):
        programs = cBench().programs()
        p = programs[0]
        p.compile(['-O2'])
        self.assertListEqual(p.flags, [])
        return

    def test_run(self):
        programs = cBench().programs()
        p = programs[0]
        p.compile(['-O2'])
        runtime = p.run()
        self.assertIsInstance(runtime, float)
        self.assertLess(runtime, Decimal("inf"))
        return

    def test_step(self):
        programs = cBench().programs()
        p = programs[0]
        p.reset()
        features, runtime, done, info = p.step('-O2')
        self.assertIsInstance(features, np.ndarray)
        self.assertIsInstance(runtime, float)
        self.assertIsInstance(done, bool)
        self.assertIsInstance(info, dict)
        return

    def test_reset(self):
        programs = cBench().programs()
        p = programs[0]
        features = p.reset()
        self.assertIsInstance(features, np.ndarray)
        return
