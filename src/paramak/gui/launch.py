import runpy
import sys
from pathlib import Path

import paramak


def main():

    path_to_app = str(Path(paramak.__path__[0]) / "gui"/"app.py")

    sys.argv = ["streamlit", "run", path_to_app]
    runpy.run_module("streamlit", run_name="__main__")


if __name__ == "__main__":
    main()
