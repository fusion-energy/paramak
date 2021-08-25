#!/bin/bash

pytest tests/test_utils.py -v --cov=paramak --cov-append --cov-report term --cov-report xml
pytest tests/test_Shape.py -v --cov=paramak --cov-append --cov-report term --cov-report xml
pytest tests/test_Reactor.py -v --cov=paramak --cov-append --cov-report term --cov-report xml
pytest tests/test_parametric_shapes/ -v --cov=paramak --cov-append --cov-report term --cov-report xml
pytest tests/test_parametric_components/ -v --cov=paramak --cov-append --cov-report term --cov-report xml
pytest tests/test_parametric_reactors/ -v --cov=paramak --cov-append --cov-report term --cov-report xml
python tests/test_example_shapes.py
python tests/test_example_components.py
python tests/test_example_reactors.py
