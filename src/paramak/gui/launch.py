import runpy
import sys
import openmc_plot
from pathlib import Path


def main():

    path_to_app = str(Path(openmc_plot.__path__[0])/'app.py')

    sys.argv = ["streamlit", "run", path_to_app]; 
    runpy.run_module("streamlit", run_name="__main__")


if __name__ == "__main__":
    main()
