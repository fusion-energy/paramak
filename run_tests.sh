#!/bin/bash

pytest tests -v --cov=paramak --cov-append --cov-report term --cov-report xml
pytest examples_tests -v
