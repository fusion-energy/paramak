#!/bin/bash

pytest tests/test_neutronics_utils.py -v --cov=paramak --cov-append --cov-report term --cov-report xml
pytest tests/test_example_neutronics_simulations.py -v --cov=paramak --cov-append --cov-report term --cov-report xml
pytest tests/test_utils.py -v --cov=paramak --cov-append --cov-report term --cov-report xml
pytest tests/test_Shape.py -v --cov=paramak --cov-append --cov-report term --cov-report xml
pytest tests/test_Reactor.py -v --cov=paramak --cov-append --cov-report term --cov-report xml
pytest tests/test_parametric_shapes/ -v --cov=paramak --cov-append --cov-report term --cov-report xml
pytest tests/test_parametric_components/ -v --cov=paramak --cov-append --cov-report term --cov-report xml
pytest tests/test_parametric_reactors/ -v --cov=paramak --cov-append --cov-report term --cov-report xml
pytest tests/test_example_shapes.py -v --cov=paramak --cov-append --cov-report term --cov-report xml
pytest tests/test_example_components.py -v --cov=paramak --cov-append --cov-report term --cov-report xml
pytest tests/test_example_reactors.py -v --cov=paramak --cov-append --cov-report term --cov-report xml
pytest tests/test_parametric_neutronics/ -v --cov=paramak --cov-append --cov-report term --cov-report xml