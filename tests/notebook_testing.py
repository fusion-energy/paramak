
import sys
import os

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert.preprocessors.execute import CellExecutionError


def notebook_run(path):
    """
    Execute a notebook via nbconvert and collect output.
    :returns (parsed nb object, execution errors)
    """
    kernel_name = 'python%d' % sys.version_info[0]
    this_file_directory = os.path.dirname(__file__)
    errors = []

    with open(path) as file:
        note_book = nbformat.read(file, as_version=4)
        note_book.metadata.get('kernelspec', {})['name'] = kernel_name
        ep = ExecutePreprocessor(
            kernel_name=kernel_name,
            timeout=800)

        try:
            ep.preprocess(
                note_book, {
                    'metadata': {
                        'path': this_file_directory}})

        except CellExecutionError as e:
            if "SKIP" in e.traceback:
                print(str(e.traceback).split("\n")[-2])
            else:
                raise e

    return note_book, errors
