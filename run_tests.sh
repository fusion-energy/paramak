#!/bin/bash

pytest tests -v --durations=0 --cov=paramak --cov-append --cov-report term --cov-report xml
pytest examples_tests -v --durations=0
