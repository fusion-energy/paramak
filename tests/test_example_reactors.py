
import os
import sys
import unittest
from pathlib import Path
import time
from .notebook_testing import notebook_run

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'examples'))


class TestExampleReactors(unittest.TestCase):

    def test_jupyter_notebooks_example_parametric_reactors(self):
        timings = []
        for notebook in Path().rglob("examples/example_parametric_reactors/*.ipynb"):
            start = time.time()

            print(notebook)
            nb, errors = notebook_run(notebook)
            assert errors == []

            stop = time.time()
            duration = stop - start

            print((notebook, duration))
            timings.append((notebook, duration))

        # to see timings run with pytest --capture=tee-sys
        print(timings)


if __name__ == "__main__":
    unittest.main()
