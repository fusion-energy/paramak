import os
import sys
import pytest
from pathlib import Path

from notebook_testing import notebook_run

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "examples"))


@pytest.mark.parametrize(
    "notebook",
    Path().rglob("examples/example_parametric_reactors/*.ipynb"),
    ids=os.path.basename,
)
def test_example_reactors(notebook):
    errors = notebook_run(notebook)
    assert errors == []
