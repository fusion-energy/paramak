
import os
import sys
from pathlib import Path

from notebook_testing import notebook_run

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'examples'))


def main():
    for notebook in Path().rglob("examples/example_parametric_shapes/*.ipynb"):
        print(notebook)
        errors = notebook_run(notebook)
        assert errors == []


if __name__ == "__main__":
    main()
