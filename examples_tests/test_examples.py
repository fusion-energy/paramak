import pytest
import nbformat
import platform
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert.preprocessors.execute import CellExecutionError
from pathlib import Path


def notebook_run(path):
    """
    Execute a notebook via nbconvert and collect output.
    :returns (parsed nb object, execution errors)
    """
    kernel_name = "python%s" % platform.python_version_tuple()[0]

    with open(path) as file:
        note_book = nbformat.read(file, as_version=4)
        note_book.metadata.get("kernelspec", {})["name"] = kernel_name
        ep = ExecutePreprocessor(kernel_name=kernel_name, timeout=800)

        try:
            ep.preprocess(note_book)

        except CellExecutionError as e:
            if "SKIP" in e.traceback:
                print(str(e.traceback).split("\n")[-2])
            else:
                raise e


@pytest.mark.parametrize(
    "notebook",
    Path().rglob("examples/*/*.ipynb"),
    ids=lambda x: x.stem,
)
def test_example(notebook):
    notebook_run(notebook)
