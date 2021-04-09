
import os
import sys
import unittest
from pathlib import Path

import nbformat
from examples.example_parametric_reactors import (
    ball_reactor, ball_reactor_single_null, make_animation,
    submersion_reactor_single_null)
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert.preprocessors.execute import CellExecutionError

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'examples'))


def _notebook_run(path):
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
            timeout=300)

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


class TestExampleReactors(unittest.TestCase):

    def test_jupyter_notebooks_example_parametric_reactors(self):
        for notebook in Path().rglob("examples/example_parametric_reactors/*.ipynb"):
            print(notebook)
            nb, errors = _notebook_run(notebook)
            assert errors == []

    def test_make_animations(self):
        """Runs the example to check the output files are produced"""
        output_filenames = [
            "random_0000.svg",
            "random_0001.svg",
            "rotation_0000.svg",
            "rotation_0001.svg",
        ]
        os.system("rm *.svg")
        make_animation.rotate_single_reactor(2)
        make_animation.make_random_reactors(2)
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True

    def test_make_parametric_ball_rector(self):
        """Runs the example and checks the output files are produced"""
        output_filenames = [
            "plasma.stp",
            "inboard_tf_coils.stp",
            "center_column_shield.stp",
            "divertor.stp",
            "firstwall.stp",
            "blanket.stp",
            "blanket_rear_wall.stp",
            "graveyard.stp",
        ]
        for output_filename in output_filenames:
            os.system("rm " + output_filename)
        ball_reactor.make_ball_reactor(output_folder='')
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
            os.system("rm " + output_filename)

    def test_make_parametric_single_null_ball_reactor(self):
        """Runs the example and checks the output files are produced"""
        output_filenames = [
            "blanket_rear_wall.stp",
            "blanket.stp",
            "center_column_shield.stp",
            "divertor.stp",
            "firstwall.stp",
            "graveyard.stp",
            "inboard_tf_coils.stp",
            "pf_coils.stp",
            "plasma.stp",
            "tf_coil.stp"
        ]
        for output_filename in output_filenames:
            os.system("rm " + output_filename)
        ball_reactor_single_null.make_ball_reactor_sn(output_folder='')
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
            os.system("rm " + output_filename)

    def test_make_parametric_single_null_submersion_reactor(self):
        """Runs the example and checks the output files are produced"""
        output_filenames = [
            'inboard_tf_coils.stp',
            'center_column_shield.stp',
            'plasma.stp',
            'divertor.stp',
            'supports.stp',
            'outboard_firstwall.stp',
            'blanket.stp',
            'outboard_rear_blanket_wall.stp',
            'outboard_tf_coil.stp',
            'pf_coils.stp',
            'graveyard.stp'
        ]
        for output_filename in output_filenames:
            os.system("rm " + output_filename)
        submersion_reactor_single_null.make_submersion_sn(output_folder='')
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
            os.system("rm " + output_filename)


if __name__ == "__main__":
    unittest.main()
