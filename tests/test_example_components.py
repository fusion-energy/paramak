
import os
import sys
import unittest
from pathlib import Path

from notebook_testing import notebook_run

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'examples'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'paramak'))


class TestExampleComponents(unittest.TestCase):

    def test_jupyter_notebooks_example_parametric_components(self):
        for notebook in Path().rglob("examples/example_parametric_components/*.ipynb"):
            print(notebook)
            errors = notebook_run(notebook)
            assert errors == []
            # assert False


if __name__ == "__main__":
    unittest.main()
